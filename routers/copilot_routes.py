# routers/copilot_routes.py
from fastapi import APIRouter, Depends

from models import User
from schemas import CopilotRequest, CopilotResponse
from auth import get_current_user
from llm_service import explain_requirement

router = APIRouter(prefix="/copilot", tags=["copilot"])


@router.post("/explain", response_model=CopilotResponse)
def explain(
    payload: CopilotRequest,
    current_user: User = Depends(get_current_user),
):
    result = explain_requirement(payload.requirement_text)
    return CopilotResponse(**result)