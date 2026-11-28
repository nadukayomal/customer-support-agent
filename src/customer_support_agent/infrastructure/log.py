"""
This file contain centralized logging configurations.

Usage:
    from infrastructure.log import setup logging
    setup_logging()
    setup_logging("DEBUG")
"""

import sys
import logging
from loguru import logger
from typing import Optional


# Format string
_FMT_FULL = (
    "<green>{time:HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
    "<level>{message}</level>"
)


class _InterceptHandler(logging.Handler):
    """
    This class makes third-party libraries play nicely with Loguru so you get consistent, pretty logs from the entire application.

        - Route stdlib : 
            Take messages from the old logging system and send them into Loguru.
        - Attach this handler to the root logge : 
            We install this handler on the main (root) logger of the standard library so it can catch everything.
        - Libraries which use logging.getLogger(…) … automatically emit through loguru's sink
    """
    def emit(self, record: logging.LogRecord) -> None:
        # Map stdlib level to loguru level
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find the caller frame that originated the log call
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# Public API 

def setup_logging(
                    level: str = "INFO",
                    *,
                    intercept_stdlib: bool = True,
                    log_file: Optional[str] = None,
                ) -> None:
    """
    Configure loguru for the current process.

    Call this **once** at your entry-point (script ``main()`` or CLI dispatcher).

    Args:
        level: Minimum log level (``DEBUG``, ``INFO``, ``WARNING``, …).
        intercept_stdlib: Route stdlib ``logging`` through loguru so
                         third-party libraries also emit structured logs.
        log_file: Optional path to a rotating log file.
    """
    # Remove default loguru handler (id 0)
    logger.remove()

    # Primary sink: stderr
    logger.add(
        sys.stderr,
        format=_FMT_FULL,
        level=level.upper(),
        colorize=True,
        backtrace=True,
        diagnose=False,  # keep tracebacks concise in production
    )

    # Optional file sink
    if log_file:
        logger.add(
            log_file,
            format=_FMT_FULL,
            level=level.upper(),
            rotation="10 MB",
            retention="7 days",
            compression="gz",
        )

    # Intercept stdlib logging
    if intercept_stdlib:
        logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)

    logger.debug("Loguru configured — level={}", level)