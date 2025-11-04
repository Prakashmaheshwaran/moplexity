from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload
from typing import List
from app.core.database import get_db
from app.models import Conversation, Message
from app.schemas import Conversation as ConversationSchema, ConversationList, ConversationCreate

router = APIRouter()


@router.get("/", response_model=List[ConversationList])
async def get_conversations(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get all conversations"""
    try:
        result = await db.execute(
            select(Conversation)
            .options(joinedload(Conversation.selected_model))
            .order_by(desc(Conversation.updated_at))
            .offset(skip)
            .limit(limit)
        )
        conversations = result.unique().scalars().all()
        
        return conversations
    except Exception as e:
        print(f"Error fetching conversations: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching conversations: {str(e)}")


@router.get("/{conversation_id}", response_model=ConversationSchema)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific conversation with all messages"""
    try:
        result = await db.execute(
            select(Conversation)
            .options(
                joinedload(Conversation.messages).joinedload(Message.sources),
                joinedload(Conversation.selected_model)
            )
            .where(Conversation.id == conversation_id)
        )
        conversation = result.unique().scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching conversation {conversation_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching conversation: {str(e)}")


@router.post("/", response_model=ConversationSchema)
async def create_conversation(
    conversation: ConversationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation"""
    db_conversation = Conversation(**conversation.dict())
    db.add(db_conversation)
    await db.commit()
    await db.refresh(db_conversation)
    return db_conversation


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation"""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    await db.delete(conversation)
    await db.commit()
    return {"message": "Conversation deleted successfully"}

