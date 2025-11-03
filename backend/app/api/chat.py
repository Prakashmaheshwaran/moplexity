from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.schemas import ChatRequest, ChatResponse
from app.models import Conversation, Message, Source
from app.services.search_service import SearchService
from app.services.llm_service import LLMService
import json

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Process a chat query with AI response and sources"""
    
    # Get or create conversation
    if request.conversation_id:
        result = await db.execute(
            select(Conversation).where(Conversation.id == request.conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        # Create new conversation with query as title
        title = request.query[:100] + "..." if len(request.query) > 100 else request.query
        conversation = Conversation(title=title, selected_model_id=request.model_id)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
    
    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.query
    )
    db.add(user_message)
    await db.commit()
    
    # Perform search
    search_service = SearchService(db)
    max_results = 15 if request.pro_mode else 10
    search_results = await search_service.multi_source_search(request.query, max_results)
    
    # Generate AI response
    llm_service = LLMService()
    ai_response = await llm_service.generate_response(
        query=request.query,
        search_results=search_results,
        conversation_id=conversation.id,
        db=db,
        model_id=request.model_id
    )
    
    # Save assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=ai_response["content"]
    )
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)
    
    # Save sources
    sources = []
    for result in search_results[:10]:  # Limit to top 10 sources
        source = Source(
            message_id=assistant_message.id,
            title=result["title"],
            url=result["url"],
            snippet=result["snippet"],
            source_type=result["source_type"]
        )
        db.add(source)
        sources.append(source)
    
    await db.commit()
    
    # Refresh to get source IDs
    for source in sources:
        await db.refresh(source)
    
    return ChatResponse(
        conversation_id=conversation.id,
        message_id=assistant_message.id,
        content=ai_response["content"],
        sources=sources,
        follow_up_questions=ai_response.get("follow_up_questions", [])
    )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Stream chat response using SSE"""
    
    async def generate():
        try:
            # Get or create conversation
            if request.conversation_id:
                result = await db.execute(
                    select(Conversation).where(Conversation.id == request.conversation_id)
                )
                conversation = result.scalar_one_or_none()
                if not conversation:
                    yield f"data: {json.dumps({'error': 'Conversation not found'})}\n\n"
                    return
            else:
                title = request.query[:100] + "..." if len(request.query) > 100 else request.query
                conversation = Conversation(title=title, selected_model_id=request.model_id)
                db.add(conversation)
                await db.commit()
                await db.refresh(conversation)
            
            # Send conversation ID
            yield f"data: {json.dumps({'type': 'conversation_id', 'conversation_id': conversation.id})}\n\n"
            
            # Save user message
            user_message = Message(
                conversation_id=conversation.id,
                role="user",
                content=request.query
            )
            db.add(user_message)
            await db.commit()
            
            # Perform search
            yield f"data: {json.dumps({'type': 'status', 'message': 'Searching...'})}\n\n"
            search_service = SearchService(db)
            max_results = 15 if request.pro_mode else 10
            search_results = await search_service.multi_source_search(request.query, max_results)
            
            # Send sources
            yield f"data: {json.dumps({'type': 'sources', 'sources': search_results[:10]})}\n\n"
            
            # Generate streaming response
            yield f"data: {json.dumps({'type': 'status', 'message': 'Generating response...'})}\n\n"
            
            llm_service = LLMService()
            full_content = ""
            
            async for chunk in llm_service.generate_streaming_response(
                query=request.query,
                search_results=search_results,
                conversation_id=conversation.id,
                db=db,
                model_id=request.model_id
            ):
                full_content += chunk
                yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
            
            # Save assistant message
            assistant_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=full_content
            )
            db.add(assistant_message)
            await db.commit()
            await db.refresh(assistant_message)
            
            # Save sources
            for result in search_results[:10]:
                source = Source(
                    message_id=assistant_message.id,
                    title=result["title"],
                    url=result["url"],
                    snippet=result["snippet"],
                    source_type=result["source_type"]
                )
                db.add(source)
            
            await db.commit()
            
            # Send completion
            yield f"data: {json.dumps({'type': 'done', 'message_id': assistant_message.id})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

