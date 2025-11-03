from typing import List, Dict
import feedparser
import httpx
import re


class RedditService:
    def __init__(self):
        self.base_url = "https://www.reddit.com"
    
    async def search_reddit(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search Reddit using RSS feeds"""
        results = []
        
        try:
            # Clean query for URL
            clean_query = query.replace(" ", "+")
            
            # Search across all of Reddit
            rss_url = f"{self.base_url}/search.rss?q={clean_query}&limit={max_results}"
            
            # Fetch RSS feed
            async with httpx.AsyncClient() as client:
                response = await client.get(rss_url, follow_redirects=True)
                response.raise_for_status()
            
            # Parse RSS feed
            feed = feedparser.parse(response.text)
            
            for entry in feed.entries[:max_results]:
                # Extract subreddit from link if possible
                subreddit_match = re.search(r'/r/([^/]+)/', entry.link)
                subreddit = subreddit_match.group(1) if subreddit_match else "reddit"
                
                # Clean up summary
                summary = entry.get('summary', '')
                # Remove HTML tags
                summary = re.sub(r'<[^>]+>', '', summary)
                summary = summary[:500] + "..." if len(summary) > 500 else summary
                
                results.append({
                    "title": f"[r/{subreddit}] {entry.title}",
                    "url": entry.link,
                    "snippet": summary,
                    "source_type": "reddit"
                })
        
        except Exception as e:
            print(f"Reddit search error: {e}")
        
        return results
    
    async def search_subreddit(self, subreddit: str, query: str, max_results: int = 5) -> List[Dict]:
        """Search within a specific subreddit"""
        results = []
        
        try:
            clean_query = query.replace(" ", "+")
            rss_url = f"{self.base_url}/r/{subreddit}/search.rss?q={clean_query}&restrict_sr=on&limit={max_results}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(rss_url, follow_redirects=True)
                response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            
            for entry in feed.entries[:max_results]:
                summary = entry.get('summary', '')
                summary = re.sub(r'<[^>]+>', '', summary)
                summary = summary[:500] + "..." if len(summary) > 500 else summary
                
                results.append({
                    "title": f"[r/{subreddit}] {entry.title}",
                    "url": entry.link,
                    "snippet": summary,
                    "source_type": "reddit"
                })
        
        except Exception as e:
            print(f"Subreddit search error: {e}")
        
        return results
    
    async def get_hot_posts(self, subreddit: str = "", max_results: int = 5) -> List[Dict]:
        """Get hot posts from Reddit or a specific subreddit"""
        results = []
        
        try:
            if subreddit:
                rss_url = f"{self.base_url}/r/{subreddit}/hot.rss?limit={max_results}"
            else:
                rss_url = f"{self.base_url}/hot.rss?limit={max_results}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(rss_url, follow_redirects=True)
                response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            
            for entry in feed.entries[:max_results]:
                subreddit_match = re.search(r'/r/([^/]+)/', entry.link)
                sub = subreddit_match.group(1) if subreddit_match else "reddit"
                
                summary = entry.get('summary', '')
                summary = re.sub(r'<[^>]+>', '', summary)
                summary = summary[:500] + "..." if len(summary) > 500 else summary
                
                results.append({
                    "title": f"[r/{sub}] {entry.title}",
                    "url": entry.link,
                    "snippet": summary,
                    "source_type": "reddit"
                })
        
        except Exception as e:
            print(f"Hot posts error: {e}")
        
        return results

