"""
Chat utilities for the FastAPI layer.

Helper functions used by the chat endpoint. At this stage the agent is not
connected yet, so the reply is a simple echo of the customer's message.
Replace the echo with the real agent call once the agent is ready.
"""

from uuid import uuid4
from customer_support_agent.schema.chat import ChatRequest, ChatResponse


def get_user_query(request: ChatRequest) -> ChatResponse:
    print(request.message)
    conversation_id = request.conversation_id or str(uuid4())
    return ChatResponse(
        reply=request.message,
        conversation_id=conversation_id,
    )
