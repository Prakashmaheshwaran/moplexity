from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import SearchCache
from app.services.youtube_service import YouTubeService
from app.services.reddit_service import RedditService
from app.services.wikipedia_service import WikipediaService
from app.core.config import settings
import asyncio
import json
from datetime import datetime, timedelta


class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.youtube_service = YouTubeService()
        self.reddit_service = RedditService()
        self.wikipedia_service = WikipediaService()
    
    async def multi_source_search(self, query: str, max_results: int = 10, focus_mode: str = 'web') -> List[Dict]:
        """Perform multi-source search based on focus mode
        
        Supports: web, social, academic
        """
        
        # Check cache first (cache for 1 hour)
        cache_key = f"{query}_{focus_mode}"
        cached_results = await self._get_cached_results(cache_key)
        if cached_results:
            return cached_results[:max_results]
        
        results = []
        
        if focus_mode == 'web':
            # Web search: Always include Wikipedia, then DuckDuckGo, Bing, Google
            # Try Wikipedia first as it's reliable
            try:
                wiki_results = await self.wikipedia_service.search_wikipedia(query, max_results=min(3, max_results))
                if wiki_results:
                    results.extend(wiki_results)
                    print(f"Wikipedia search returned {len(wiki_results)} results")
            except Exception as e:
                print(f"Wikipedia search failed: {e}")
            
            # Then try DuckDuckGo
            try:
                ddg_results = await self._duckduckgo_search(query, max_results - len(results))
                if ddg_results:
                    results.extend(ddg_results)
                    print(f"DuckDuckGo search returned {len(ddg_results)} results")
                else:
                    print("DuckDuckGo search returned no results")
            except Exception as e:
                print(f"DuckDuckGo search failed: {e}")
            
            # If still no results, try Wikipedia fallback
            if len(results) == 0:
                try:
                    wiki_fallback = await self.wikipedia_service.search_wikipedia_fallback(query, max_results=3)
                    if wiki_fallback:
                        results.extend(wiki_fallback)
                        print(f"Wikipedia fallback returned {len(wiki_fallback)} results")
                except Exception as e:
                    print(f"Wikipedia fallback failed: {e}")
            
            if len(results) < max_results and settings.bing_search_api_key:
                try:
                    bing_results = await self._bing_search(query, max_results - len(results))
                    results.extend(bing_results)
                except Exception as e:
                    print(f"Bing search failed: {e}")
            
            if len(results) < max_results and settings.google_search_api_key and settings.google_cse_id:
                try:
                    google_results = await self._google_search(query, max_results - len(results))
                    results.extend(google_results)
                except Exception as e:
                    print(f"Google search failed: {e}")
        
        elif focus_mode == 'social':
            # Social search: Reddit, YouTube, LinkedIn, Twitter, GitHub - all marked as 'social'
            try:
                reddit_results = await self.reddit_service.search_reddit(query, max_results=max(max_results // 3, 3))
                # Mark as social
                for result in reddit_results:
                    result["source_type"] = "social"
                results.extend(reddit_results)
            except Exception as e:
                print(f"Reddit search failed: {e}")
            
            # YouTube search
            if len(results) < max_results:
                try:
                    youtube_results = await self.youtube_service.search_youtube(query, max_results=max((max_results - len(results)) // 2, 2))
                    # Mark as social
                    for result in youtube_results:
                        result["source_type"] = "social"
                    results.extend(youtube_results)
                except Exception as e:
                    print(f"YouTube search failed: {e}")
            
            # LinkedIn search using structured query
            if len(results) < max_results:
                linkedin_query = f"{query} site:linkedin.com"
                try:
                    ddg_results = await self._duckduckgo_search(linkedin_query, max_results - len(results))
                    # Mark as social
                    for result in ddg_results:
                        result["source_type"] = "social"
                    results.extend(ddg_results)
                except Exception as e:
                    print(f"LinkedIn search failed: {e}")
            
            # Twitter/X search
            if len(results) < max_results:
                twitter_query = f"{query} (site:twitter.com OR site:x.com)"
                try:
                    ddg_results = await self._duckduckgo_search(twitter_query, max_results - len(results))
                    # Mark as social
                    for result in ddg_results:
                        result["source_type"] = "social"
                    results.extend(ddg_results)
                except Exception as e:
                    print(f"Twitter search failed: {e}")
            
            # GitHub search
            if len(results) < max_results:
                github_query = f"{query} site:github.com"
                try:
                    ddg_results = await self._duckduckgo_search(github_query, max_results - len(results))
                    # Mark as social
                    for result in ddg_results:
                        result["source_type"] = "social"
                    results.extend(ddg_results)
                except Exception as e:
                    print(f"GitHub search failed: {e}")
            
            # Fallback to Wikipedia and web if not enough results
            if len(results) < max_results:
                try:
                    wiki_results = await self.wikipedia_service.search_wikipedia(query, max_results=2)
                    # Mark as social since user selected social mode
                    for result in wiki_results:
                        result["source_type"] = "social"
                    results.extend(wiki_results)
                except Exception as e:
                    print(f"Wikipedia fallback failed: {e}")
                
                if len(results) < max_results:
                    try:
                        ddg_results = await self._duckduckgo_search(query, max_results - len(results))
                        # Mark as social since user selected social mode
                        for result in ddg_results:
                            result["source_type"] = "social"
                        results.extend(ddg_results)
                    except Exception as e:
                        print(f"DuckDuckGo search failed: {e}")
        
        elif focus_mode == 'academic':
            # Academic search: Focus on scholarly sources
            academic_query = f"{query} (site:edu OR site:org OR site:gov OR filetype:pdf)"
            try:
                ddg_results = await self._duckduckgo_search(academic_query, max_results)
                # Mark as academic source type
                for result in ddg_results:
                    result["source_type"] = "academic"
                results.extend(ddg_results)
            except Exception as e:
                print(f"Academic search failed: {e}")
            
            # Fallback to Wikipedia and regular web search (still mark as academic)
            if len(results) < max_results:
                try:
                    wiki_results = await self.wikipedia_service.search_wikipedia(query, max_results=2)
                    # Mark as academic since user selected academic mode
                    for result in wiki_results:
                        result["source_type"] = "academic"
                    results.extend(wiki_results)
                except Exception as e:
                    print(f"Wikipedia fallback failed: {e}")
                
                if len(results) < max_results:
                    try:
                        ddg_results = await self._duckduckgo_search(query, max_results - len(results))
                        # Mark as academic since user selected academic mode
                        for result in ddg_results:
                            result["source_type"] = "academic"
                        results.extend(ddg_results)
                    except Exception as e:
                        print(f"DuckDuckGo search failed: {e}")
        
        # Cache results
        await self._cache_results(cache_key, results)
        
        return results[:max_results]
    
    async def _duckduckgo_search(self, query: str, max_results: int) -> List[Dict]:
        """Search using DuckDuckGo with retry logic"""
        max_retries = 3
        retry_delay = 2  # seconds
        
        # Add a small delay before first attempt to avoid rate limits
        await asyncio.sleep(0.5)
        
        for attempt in range(max_retries):
            try:
                from duckduckgo_search import DDGS
                
                results = []
                with DDGS() as ddgs:
                    search_results = ddgs.text(query, max_results=max_results)
                    for result in search_results:
                        # Skip invalid results
                        if not result.get("title") or not result.get("href"):
                            continue
                        results.append({
                            "title": result.get("title", ""),
                            "url": result.get("href", ""),
                            "snippet": result.get("body", "")[:500],  # Limit snippet length
                            "source_type": "web"
                        })
                
                if results:
                    print(f"DuckDuckGo search successful: {len(results)} results for query: {query[:50]}")
                    return results
                else:
                    print(f"DuckDuckGo returned no results (attempt {attempt + 1}/{max_retries})")
                    # If no results and not last attempt, wait and retry
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2
                    
            except Exception as e:
                error_msg = str(e)
                print(f"DuckDuckGo error (attempt {attempt + 1}/{max_retries}): {error_msg}")
                
                # If rate limited, wait before retrying
                if "Ratelimit" in error_msg or "rate" in error_msg.lower() or "Ratelimit" in str(type(e).__name__):
                    if attempt < max_retries - 1:
                        print(f"Rate limited, waiting {retry_delay} seconds before retry...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        print("DuckDuckGo rate limit exceeded after all retries")
                        return []
                
                # For other errors, try again if not last attempt
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    print(f"DuckDuckGo search failed after {max_retries} attempts")
                    return []
        
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
    
    async def _get_cached_results(self, cache_key: str) -> Optional[List[Dict]]:
        """Get cached search results if available and fresh"""
        try:
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            result = await self.db.execute(
                select(SearchCache)
                .where(SearchCache.query == cache_key)
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
    
    async def _cache_results(self, cache_key: str, results: List[Dict]):
        """Cache search results"""
        try:
            cache_entry = SearchCache(
                query=cache_key,
                results_json=results
            )
            self.db.add(cache_entry)
            await self.db.commit()
        except Exception as e:
            print(f"Cache storage error: {e}")
            await self.db.rollback()

