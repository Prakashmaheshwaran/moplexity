from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import SearchCache
from app.services.youtube_service import YouTubeService
from app.services.reddit_service import RedditService
from app.config import settings
import asyncio
import json
from datetime import datetime, timedelta


class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.youtube_service = YouTubeService()
        self.reddit_service = RedditService()
    
    async def multi_source_search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Perform multi-source search with cascading fallback"""
        
        # Check cache first (cache for 1 hour)
        cached_results = await self._get_cached_results(query)
        if cached_results:
            return cached_results[:max_results]
        
        results = []
        
        # Try DuckDuckGo first (no API key required)
        try:
            ddg_results = await self._duckduckgo_search(query, max_results)
            results.extend(ddg_results)
        except Exception as e:
            print(f"DuckDuckGo search failed: {e}")
        
        # If insufficient results, try Bing
        if len(results) < max_results and settings.bing_search_api_key:
            try:
                bing_results = await self._bing_search(query, max_results - len(results))
                results.extend(bing_results)
            except Exception as e:
                print(f"Bing search failed: {e}")
        
        # If still insufficient, try Google
        if len(results) < max_results and settings.google_search_api_key and settings.google_cse_id:
            try:
                google_results = await self._google_search(query, max_results - len(results))
                results.extend(google_results)
            except Exception as e:
                print(f"Google search failed: {e}")
        
        # Add Reddit results if query seems suitable
        try:
            reddit_results = await self.reddit_service.search_reddit(query, max_results=3)
            results.extend(reddit_results)
        except Exception as e:
            print(f"Reddit search failed: {e}")
        
        # Check for YouTube URLs or video-related queries
        if "youtube" in query.lower() or "video" in query.lower():
            try:
                youtube_results = await self.youtube_service.search_and_extract(query)
                results.extend(youtube_results)
            except Exception as e:
                print(f"YouTube search failed: {e}")
        
        # Cache results
        await self._cache_results(query, results)
        
        return results[:max_results]
    
    async def _duckduckgo_search(self, query: str, max_results: int) -> List[Dict]:
        """Search using DuckDuckGo"""
        try:
            from duckduckgo_search import DDGS
            
            results = []
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=max_results)
                for result in search_results:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "snippet": result.get("body", ""),
                        "source_type": "web"
                    })
            return results
        except Exception as e:
            print(f"DuckDuckGo error: {e}")
            return []
    
    async def _bing_search(self, query: str, max_results: int) -> List[Dict]:
        """Search using Bing API"""
        if not settings.bing_search_api_key:
            return []
        
        try:
            import httpx
            
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {"Ocp-Apim-Subscription-Key": settings.bing_search_api_key}
            params = {"q": query, "count": max_results}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            results = []
            for item in data.get("webPages", {}).get("value", []):
                results.append({
                    "title": item.get("name", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("snippet", ""),
                    "source_type": "web"
                })
            return results
        except Exception as e:
            print(f"Bing search error: {e}")
            return []
    
    async def _google_search(self, query: str, max_results: int) -> List[Dict]:
        """Search using Google Custom Search API"""
        if not settings.google_search_api_key or not settings.google_cse_id:
            return []
        
        try:
            import httpx
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": settings.google_search_api_key,
                "cx": settings.google_cse_id,
                "q": query,
                "num": min(max_results, 10)
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            
            results = []
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source_type": "web"
                })
            return results
        except Exception as e:
            print(f"Google search error: {e}")
            return []
    
    async def _get_cached_results(self, query: str) -> Optional[List[Dict]]:
        """Get cached search results if available and fresh"""
        try:
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            result = await self.db.execute(
                select(SearchCache)
                .where(SearchCache.query == query)
                .where(SearchCache.created_at > one_hour_ago)
                .order_by(SearchCache.created_at.desc())
                .limit(1)
            )
            cache_entry = result.scalar_one_or_none()
            
            if cache_entry:
                return cache_entry.results_json
        except Exception as e:
            print(f"Cache retrieval error: {e}")
        
        return None
    
    async def _cache_results(self, query: str, results: List[Dict]):
        """Cache search results"""
        try:
            cache_entry = SearchCache(
                query=query,
                results_json=results
            )
            self.db.add(cache_entry)
            await self.db.commit()
        except Exception as e:
            print(f"Cache storage error: {e}")
            await self.db.rollback()

