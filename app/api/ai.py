from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.ai_compliance import build_compliance_context, build_prompt

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/query")
def ai_query(
    user_id: int,
    question: str,
    db: Session = Depends(get_db)
):
    context = build_compliance_context(db, user_id)
    prompt = build_prompt(context, question)

    
    return {
        "prompt_sent_to_llm": prompt,
        "answer": "LLM integration pending"
    }

