import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.schemas import ChatRequest

@pytest.mark.asyncio
async def test_chat_endpoint(client, db_session):
    """Test the non-streaming chat endpoint."""
    
    # Mock SearchService
    with patch('app.api.v1.chat.SearchService') as MockSearchService:
        mock_search_instance = MockSearchService.return_value
        mock_search_instance.multi_source_search = AsyncMock(return_value=[
            {"title": "Test Source", "url": "http://test.com", "snippet": "Test snippet", "source_type": "web"}
        ])
        mock_search_instance.search_across_modes = AsyncMock(return_value=[])
        mock_search_instance.search_all_sources = AsyncMock(return_value=[])

        # Mock LLMService
        with patch('app.api.v1.chat.LLMService') as MockLLMService:
            mock_llm_instance = MockLLMService.return_value
            mock_llm_instance.set_model = AsyncMock()
            mock_llm_instance._evaluate_result_quality = AsyncMock(return_value={"is_sufficient": True, "score": 1.0})
            mock_llm_instance.generate_response = AsyncMock(return_value={
                "content": "This is a test response.",
                "follow_up_questions": ["Question 1?"]
            })

            response = await client.post("/api/chat/", json={
                "query": "Hello world",
                "model_id": 1,
                "pro_mode": False
            })

            assert response.status_code == 200
            data = response.json()
            assert data["content"] == "This is a test response."
            assert len(data["sources"]) == 1
            assert data["sources"][0]["title"] == "Test Source"

@pytest.mark.asyncio
async def test_chat_stream_endpoint(client, db_session):
    """Test the streaming chat endpoint."""
    
    # Mock SearchService
    with patch('app.api.v1.chat.SearchService') as MockSearchService:
        mock_search_instance = MockSearchService.return_value
        mock_search_instance.multi_source_search = AsyncMock(return_value=[])
        
        # Mock LLMService
        with patch('app.api.v1.chat.LLMService') as MockLLMService:
            mock_llm_instance = MockLLMService.return_value
            mock_llm_instance.set_model = AsyncMock()
            mock_llm_instance._evaluate_result_quality = AsyncMock(return_value={"is_sufficient": True})
            
            # Mock streaming generator
            async def mock_stream(*args, **kwargs):
                yield "Hello "
                yield "World"
            
            mock_llm_instance.generate_streaming_response = mock_stream
            mock_llm_instance._generate_follow_up_questions = AsyncMock(return_value=[])

            async with client.stream("POST", "/api/chat/stream", json={
                "query": "Stream test",
                "model_id": 1
            }) as response:
                assert response.status_code == 200
                
                # Read the stream
                chunks = []
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        chunks.append(line)
                
                assert len(chunks) > 0
