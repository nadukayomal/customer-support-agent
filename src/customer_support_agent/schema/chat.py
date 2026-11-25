from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = None
    # NO customer_id here: it comes from the auth token


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    sources: list[str] = []
    escalated: bool = False
