from fastapi import APIRouter

from customer_support_agent.schema.chat import ChatRequest, ChatResponse
from customer_support_agent.utils.api_utils import get_user_query

router = APIRouter()


@router.post("/user_query", response_model=ChatResponse)
def user_query(request: ChatRequest) -> ChatResponse:
    return get_user_query(request)
