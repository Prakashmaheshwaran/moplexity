from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
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
    
    # Perform search based on focus mode
    search_service = SearchService(db)
    max_results = 15 if request.pro_mode else 10
    search_results = await search_service.multi_source_search(request.query, max_results, request.focus_mode)
    
    # Evaluate result quality and perform smart fallback if needed
    llm_service = LLMService()
    await llm_service.set_model(request.model_id, db) if request.model_id else None
    
    quality_eval = await llm_service._evaluate_result_quality(request.query, search_results)
    
    # If results are insufficient, try searching all sources
    if not quality_eval["is_sufficient"]:
        print(f"Initial search quality insufficient ({quality_eval['score']:.2f}), trying cross-source fallback...")
        fallback_results = await search_service.search_all_sources(request.query, max_results)
        
        # Merge results, prioritizing original focus mode results
        merged_results = search_results.copy()
        seen_urls = {r.get('url', '') for r in merged_results}
        
        for result in fallback_results:
            if result.get('url') not in seen_urls:
                merged_results.append(result)
                seen_urls.add(result.get('url', ''))
        
        search_results = merged_results[:max_results]
        print(f"After fallback: {len(search_results)} total results")
    
    # Generate AI response
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
            search_results = await search_service.multi_source_search(request.query, max_results, request.focus_mode)
            
            # Evaluate result quality and perform smart fallback if needed
            llm_service = LLMService()
            await llm_service.set_model(request.model_id, db) if request.model_id else None
            
            quality_eval = await llm_service._evaluate_result_quality(request.query, search_results)
            
            # If results are insufficient, try searching all sources
            if not quality_eval["is_sufficient"]:
                yield f"data: {json.dumps({'type': 'status', 'message': 'Expanding search...'})}\n\n"
                fallback_results = await search_service.search_all_sources(request.query, max_results)
                
                # Merge results, prioritizing original focus mode results
                merged_results = search_results.copy()
                seen_urls = {r.get('url', '') for r in merged_results}
                
                for result in fallback_results:
                    if result.get('url') not in seen_urls:
                        merged_results.append(result)
                        seen_urls.add(result.get('url', ''))
                
                search_results = merged_results[:max_results]
            
            # Send sources
            yield f"data: {json.dumps({'type': 'sources', 'sources': search_results[:10]})}\n\n"
            
            # Generate streaming response
            yield f"data: {json.dumps({'type': 'status', 'message': 'Generating response...'})}\n\n"
            
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
            
            # Generate and send follow-up questions
            try:
                follow_up_questions = await llm_service._generate_follow_up_questions(request.query, full_content)
                yield f"data: {json.dumps({'type': 'follow_up_questions', 'questions': follow_up_questions})}\n\n"
            except Exception as e:
                print(f"Error generating follow-up questions: {e}")
            
            # Send completion
            yield f"data: {json.dumps({'type': 'done', 'message_id': assistant_message.id})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

