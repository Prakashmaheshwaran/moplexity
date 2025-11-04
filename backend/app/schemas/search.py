from pydantic import BaseModel
from typing import List


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source_type: str


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int

