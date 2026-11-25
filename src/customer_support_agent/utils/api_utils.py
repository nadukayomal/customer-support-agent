from uuid import uuid4

from customer_support_agent.schema.chat import ChatRequest, ChatResponse


def get_user_query(request: ChatRequest) -> ChatResponse:
    print(request.message)
    conversation_id = request.conversation_id or str(uuid4())
    return ChatResponse(
        reply=request.message,
        conversation_id=conversation_id,
    )
