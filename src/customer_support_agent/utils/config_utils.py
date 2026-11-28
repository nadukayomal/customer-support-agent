"""
Load YAML configuration files from the project ``config/`` directory.

Each file maps to a top-level key (stem name)::

    {
        "app": {...},      # config/app.yaml
        "llm": {...},      # config/llm.yaml
        "models": {...},   # config/models.yaml
        "rag": {...},      # config/rag.yaml
    }

Usage::

    from customer_support_agent.utils.config_utils import get_paths, get_llm, load_all_configs
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from loguru import logger

# src/customer_support_agent/utils/config_utils.py -> project root / config
CONFIG_DIR = Path(__file__).resolve().parents[3] / "config"


def _empty() -> dict[str, Any]:
    return {}


def load_yaml(filename: str) -> dict[str, Any]:
    """Load a single YAML file from ``config/`` by name (with or without ``.yaml``)."""
    name = filename if filename.endswith((".yaml", ".yml")) else f"{filename}.yaml"
    path = CONFIG_DIR / name

    if not path.is_file():
        logger.error("Config file not found: {}", path)
        return _empty()

    try:
        with path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return config if isinstance(config, dict) else _empty()
    except Exception as e:
        logger.error("Error loading configuration from {}: {}", path, e)
        return _empty()


@lru_cache(maxsize=1)
def load_all_configs() -> dict[str, dict[str, Any]]:
    """Load every ``*.yaml`` / ``*.yml`` file under ``config/``, keyed by stem."""
    configs: dict[str, dict[str, Any]] = {}

    if not CONFIG_DIR.is_dir():
        logger.error("Config directory not found: {}", CONFIG_DIR)
        return configs

    for path in sorted(CONFIG_DIR.glob("*.y*ml")):
        if path.suffix.lower() not in {".yaml", ".yml"}:
            continue
        try:
            with path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            configs[path.stem] = data if isinstance(data, dict) else _empty()
        except Exception as e:
            logger.error("Error loading configuration from {}: {}", path, e)
            configs[path.stem] = _empty()

    return configs


def reload_configs() -> dict[str, dict[str, Any]]:
    """Clear the cache and reload all YAML configs from disk."""
    load_all_configs.cache_clear()
    return load_all_configs()


def _section(file_stem: str, key: str) -> dict[str, Any]:
    return load_all_configs().get(file_stem, _empty()).get(key, _empty())


# ---------------------------------------------------------------------------
# Per-file accessors
# ---------------------------------------------------------------------------

def get_app_config() -> dict[str, Any]:
    return load_all_configs().get("app", _empty())


def get_llm_config() -> dict[str, Any]:
    return load_all_configs().get("llm", _empty())


def get_models_config() -> dict[str, Any]:
    return load_all_configs().get("models", _empty())


def get_rag_config() -> dict[str, Any]:
    return load_all_configs().get("rag", _empty())


# ---------------------------------------------------------------------------
# app.yaml sections
# ---------------------------------------------------------------------------

def get_paths() -> dict[str, Any]:
    return _section("app", "paths")


def get_logging() -> dict[str, Any]:
    return _section("app", "logging")


def get_observability() -> dict[str, Any]:
    return _section("app", "observability")


# ---------------------------------------------------------------------------
# llm.yaml sections
# ---------------------------------------------------------------------------

def get_provider() -> dict[str, Any]:
    return _section("llm", "provider")


def get_llm() -> dict[str, Any]:
    return _section("llm", "llm")


def get_embedding() -> dict[str, Any]:
    return _section("llm", "embedding")


# ---------------------------------------------------------------------------
# models.yaml sections
# ---------------------------------------------------------------------------

def get_embedding_dimensions() -> dict[str, Any]:
    return _section("models", "embedding_dimensions")


def get_provider_models(provider: str | None = None) -> dict[str, Any]:
    """Return model catalogue for one provider, or the full models config."""
    models = get_models_config()
    if provider is None:
        return models
    return models.get(provider, _empty())


# ---------------------------------------------------------------------------
# rag.yaml sections
# ---------------------------------------------------------------------------

def get_qdrant() -> dict[str, Any]:
    return _section("rag", "qdrant")


def get_chunking() -> dict[str, Any]:
    return _section("rag", "chunking")


def get_retrieval() -> dict[str, Any]:
    return _section("rag", "retrieval")


def get_cag() -> dict[str, Any]:
    return _section("rag", "cag")


def get_crag() -> dict[str, Any]:
    return _section("rag", "crag")
