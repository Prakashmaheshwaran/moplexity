from typing import List, Dict, Optional
import httpx
import re


class WikipediaService:
    """Service for searching and extracting Wikipedia articles"""
    
    def __init__(self):
        self.base_url = "https://en.wikipedia.org/api/rest_v1"
        self.search_url = "https://en.wikipedia.org/w/api.php"
    
    async def search_wikipedia(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search Wikipedia for articles matching the query"""
        results = []
        
        try:
            # Use Wikipedia Search API
            params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": max_results,
                "format": "json",
                "utf8": 1
            }
            
            # Wikipedia requires a User-Agent header
            headers = {
                "User-Agent": "Moplexity/1.0 (https://github.com/yourusername/moplexity; contact@example.com)"
            }
            
            async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
                response = await client.get(self.search_url, params=params)
                response.raise_for_status()
                data = response.json()
            
            search_results = data.get("query", {}).get("search", [])
            
            # Fetch summaries for each result
            for item in search_results:
                title = item.get("title", "")
                page_id = item.get("pageid")
                
                if title and page_id:
                    # Get article summary
                    summary_result = await self._get_article_summary(title)
                    if summary_result:
                        results.append({
                            "title": title,
                            "url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                            "snippet": summary_result.get("extract", ""),
                            "source_type": "web"
                        })
            
            return results
            
        except Exception as e:
            print(f"Wikipedia search error: {e}")
            return []
    
    async def _get_article_summary(self, title: str) -> Optional[Dict]:
        """Get article summary using Wikipedia REST API"""
        try:
            # URL encode the title
            encoded_title = title.replace(" ", "_")
            url = f"{self.base_url}/page/summary/{encoded_title}"
            
            # Wikipedia requires a User-Agent header
            headers = {
                "User-Agent": "Moplexity/1.0 (https://github.com/yourusername/moplexity; contact@example.com)"
            }
            
            async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
            
            return {
                "extract": data.get("extract", "")[:500],  # Limit to 500 chars
                "title": data.get("title", title)
            }
            
        except Exception as e:
            print(f"Wikipedia summary error for {title}: {e}")
            return None
    
    async def search_wikipedia_fallback(self, query: str, max_results: int = 3) -> List[Dict]:
        """Simplified Wikipedia search for fallback scenarios"""
        try:
            # Try direct article lookup first
            results = await self.search_wikipedia(query, max_results)
            
            # If no results, try searching for related topics
            if not results:
                # Extract key terms from query
                key_terms = self._extract_key_terms(query)
                for term in key_terms[:2]:  # Try top 2 terms
                    results = await self.search_wikipedia(term, max_results=2)
                    if results:
                        break
            
            return results
            
        except Exception as e:
            print(f"Wikipedia fallback error: {e}")
            return []
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract key terms from query for better Wikipedia searching"""
        # Remove common words
        stop_words = {"what", "is", "the", "a", "an", "how", "why", "when", "where", "who", "do", "does", "did", "can", "could", "should", "will", "would"}
        
        # Simple word extraction
        words = re.findall(r'\b\w+\b', query.lower())
        key_terms = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Prioritize capitalized words (likely proper nouns)
        capitalized = re.findall(r'\b[A-Z][a-z]+\b', query)
        key_terms = capitalized + key_terms
        
        return list(dict.fromkeys(key_terms))  # Remove duplicates while preserving order

