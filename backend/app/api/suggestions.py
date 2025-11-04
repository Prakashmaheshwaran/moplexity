from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models import LLMModel
from app.services.llm_service import LLMService
from pydantic import BaseModel
from typing import List

router = APIRouter()


class SuggestionsResponse(BaseModel):
    suggestions: List[str]


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(db: AsyncSession = Depends(get_db)):
    """Generate AI-powered suggestions for the home page"""
    try:
        # Get first active model for generating suggestions
        result = await db.execute(
            select(LLMModel)
            .where(LLMModel.is_active == True)
            .limit(1)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            # Fallback to default suggestions
            return SuggestionsResponse(suggestions=[
                "What is artificial intelligence?",
                "Latest developments in quantum computing",
                "How does blockchain work?",
                "Climate change solutions"
            ])
        
        # Use LLM to generate contextual suggestions
        llm_service = LLMService()
        await llm_service.set_model(model.id, db)
        
        prompt = """Generate 4 engaging, diverse questions that would interest someone using a search AI assistant. 
Make them thought-provoking, current, and cover different topics. 
Return only the questions, one per line, without numbering or bullets."""

        import litellm
        response = await litellm.acompletion(
            model=model.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates engaging search questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=200
        )
        
        content = response.choices[0].message.content
        suggestions = [q.strip() for q in content.split('\n') if q.strip() and not q.strip().startswith(('-', '*', '1', '2', '3', '4'))]
        
        # Ensure we have exactly 4 suggestions
        if len(suggestions) < 4:
            fallback = [
                "What is artificial intelligence?",
                "Latest developments in quantum computing",
                "How does blockchain work?",
                "Climate change solutions"
            ]
            suggestions.extend(fallback[:4 - len(suggestions)])
        
        return SuggestionsResponse(suggestions=suggestions[:4])
        
    except Exception as e:
        print(f"Error generating suggestions: {e}")
        # Fallback to default suggestions
        return SuggestionsResponse(suggestions=[
            "What is artificial intelligence?",
            "Latest developments in quantum computing",
            "How does blockchain work?",
            "Climate change solutions"
        ])

