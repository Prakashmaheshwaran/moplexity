from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas import SearchResponse
from app.services.search_service import SearchService

router = APIRouter()


@router.get("/", response_model=SearchResponse)
async def search(
    query: str,
    max_results: int = 10,
    focus_mode: str = 'web',
    modes: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    """Perform multi-source search"""
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    
    search_service = SearchService(db)
    if modes:
        try:
            parsed_modes = [m.strip() for m in modes.split(',') if m.strip()]
        except Exception:
            parsed_modes = [focus_mode]
        results = await search_service.search_across_modes(query, parsed_modes, max_results)
    else:
        results = await search_service.multi_source_search(query, max_results, focus_mode)
    
    return SearchResponse(
        query=query,
        results=results,
        total_results=len(results)
    )

