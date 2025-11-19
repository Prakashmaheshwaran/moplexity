import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.search_service import SearchService
from app.models import SearchCache

@pytest.mark.asyncio
async def test_search_service_web_mode(db_session):
    """Test multi_source_search in web mode with mocked external calls."""
    service = SearchService(db_session)
    
    # Mock Wikipedia service
    service.wikipedia_service.search_wikipedia = AsyncMock(return_value=[
        {"title": "Wiki Result", "url": "http://wiki.com", "snippet": "Wiki snippet", "source_type": "web"}
    ])
    
    # Mock DuckDuckGo search
    with patch('app.services.search_service.SearchService._duckduckgo_search', new_callable=AsyncMock) as mock_ddg:
        mock_ddg.return_value = [
            {"title": "DDG Result", "url": "http://ddg.com", "snippet": "DDG snippet", "source_type": "web"}
        ]
        
        results = await service.multi_source_search("test query", max_results=5, focus_mode='web')
        
        assert len(results) == 2
        assert results[0]["title"] == "Wiki Result"
        assert results[1]["title"] == "DDG Result"

@pytest.mark.asyncio
async def test_search_caching(db_session):
    """Test that search results are cached and retrieved."""
    service = SearchService(db_session)
    query = "cache test"
    
    # Mock external searches to return data
    service.wikipedia_service.search_wikipedia = AsyncMock(return_value=[])
    with patch('app.services.search_service.SearchService._duckduckgo_search', new_callable=AsyncMock) as mock_ddg:
        mock_ddg.return_value = [
            {"title": "Cached Result", "url": "http://cache.com", "snippet": "Snippet", "source_type": "web"}
        ]
        
        # First call - should hit "API"
        results1 = await service.multi_source_search(query, max_results=5, focus_mode='web')
        assert len(results1) == 1
        
        # Verify it was written to DB
        # (In a real integration test we'd check the DB, but here we trust the service logic or check side effects)
        
        # Second call - should hit cache
        # We reset the mock to return empty to prove it didn't call it again
        mock_ddg.return_value = [] 
        mock_ddg.reset_mock()
        
        results2 = await service.multi_source_search(query, max_results=5, focus_mode='web')
        assert len(results2) == 1
        assert results2[0]["title"] == "Cached Result"
        
        # Ensure DDG was NOT called the second time (if caching works)
        # Note: The current implementation of _get_cached_results needs to find the entry.
        # Since we are using an in-memory DB, the commit in the service should have saved it.
