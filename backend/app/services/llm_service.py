from typing import List, Dict, AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.config import settings
from app.models import Message, LLMModel, LLMProvider
import litellm
import os


class LLMService:
    def __init__(self):
        # Keep fallback API keys from settings for backward compatibility
        if settings.openai_api_key:
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        if settings.anthropic_api_key:
            os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
        if settings.google_api_key:
            os.environ["GOOGLE_API_KEY"] = settings.google_api_key

        self.current_model = None
        self.current_provider = None

    async def set_model(self, model_id: int, db: AsyncSession) -> bool:
        """Set the current model by fetching from database"""
        try:
            result = await db.execute(
                select(LLMModel).options(joinedload(LLMModel.provider)).where(LLMModel.id == model_id)
            )
            model = result.scalar_one_or_none()

            if not model or not model.is_active or not model.provider.is_active:
                return False

            self.current_model = model
            self.current_provider = model.provider

            # Set API key for this provider dynamically
            api_key_env_var = self._get_api_key_env_var(model.provider.provider_type)
            os.environ[api_key_env_var] = model.provider.api_key

            return True
        except Exception as e:
            print(f"Error setting model {model_id}: {e}")
            return False

    def _get_api_key_env_var(self, provider_type: str) -> str:
        """Get the appropriate environment variable name for the provider"""
        provider_env_vars = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY",
            "vertexai": "GOOGLE_API_KEY",  # Vertex AI uses Google API key
            "gemini": "GOOGLE_API_KEY",    # Gemini uses Google API key
            "cohere": "COHERE_API_KEY",
            "replicate": "REPLICATE_API_TOKEN",
            "together": "TOGETHER_API_KEY",
            "huggingface": "HUGGINGFACE_API_KEY",
            "bedrock": "AWS_ACCESS_KEY_ID",  # AWS Bedrock uses AWS credentials
            "azure": "AZURE_API_KEY",
        }
        return provider_env_vars.get(provider_type, f"{provider_type.upper()}_API_KEY")
    
    def _format_sources_for_context(self, search_results: List[Dict]) -> str:
        """Format search results into context for the LLM"""
        if not search_results:
            return "No search results available."
        
        context = "Here are the search results to help answer the query:\n\n"
        for idx, result in enumerate(search_results[:10], 1):
            source_type = result.get('source_type', 'web')
            context += f"[{idx}] {result['title']}\n"
            context += f"Source: {source_type.upper()} - {result['url']}\n"
            context += f"Content: {result['snippet']}\n\n"
        
        return context
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for the LLM"""
        return """You are Moplexity, an AI search assistant that provides accurate, well-researched answers based on search results.

Your role:
1. Analyze the provided search results carefully
2. Synthesize information from multiple sources
3. Provide clear, comprehensive answers
4. Cite sources using [1], [2], etc. format when referencing information
5. If information is conflicting, mention different perspectives
6. If search results don't contain enough information, acknowledge limitations
7. Be conversational but professional

Format your response:
- Use markdown for better readability
- Reference sources inline using [1], [2] format
- Organize information logically
- Include relevant details from the sources"""
    
    async def generate_response(
        self,
        query: str,
        search_results: List[Dict],
        conversation_id: int,
        db: AsyncSession,
        model_id: Optional[int] = None
    ) -> Dict:
        """Generate a complete AI response"""

        # Set model if specified
        if model_id:
            success = await self.set_model(model_id, db)
            if not success:
                return {
                    "content": "I apologize, but the selected model is not available or inactive.",
                    "follow_up_questions": []
                }
        elif not self.current_model:
            return {
                "content": "No model selected. Please select a model to continue.",
                "follow_up_questions": []
            }

        # Get conversation history
        history = await self._get_conversation_history(conversation_id, db)
        
        # Format context
        context = self._format_sources_for_context(search_results)
        
        # Build messages
        messages = [
            {"role": "system", "content": self._create_system_prompt()},
        ]
        
        # Add conversation history (last 5 exchanges)
        for msg in history[-10:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current query with context
        user_message = f"Search Results:\n{context}\n\nUser Query: {query}\n\nPlease provide a comprehensive answer based on the search results above."
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Call LiteLLM
            response = await litellm.acompletion(
                model=self.current_model.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Generate follow-up questions
            follow_up_questions = await self._generate_follow_up_questions(query, content)
            
            return {
                "content": content,
                "follow_up_questions": follow_up_questions
            }
        
        except Exception as e:
            print(f"LLM error: {e}")
            return {
                "content": f"I apologize, but I encountered an error generating a response: {str(e)}",
                "follow_up_questions": []
            }
    
    async def generate_streaming_response(
        self,
        query: str,
        search_results: List[Dict],
        conversation_id: int,
        db: AsyncSession,
        model_id: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """Generate streaming AI response"""

        # Set model if specified
        if model_id:
            success = await self.set_model(model_id, db)
            if not success:
                yield "I apologize, but the selected model is not available or inactive."
                return
        elif not self.current_model:
            yield "No model selected. Please select a model to continue."
            return

        # Get conversation history
        history = await self._get_conversation_history(conversation_id, db)
        
        # Format context
        context = self._format_sources_for_context(search_results)
        
        # Build messages
        messages = [
            {"role": "system", "content": self._create_system_prompt()},
        ]
        
        # Add conversation history
        for msg in history[-10:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current query with context
        user_message = f"Search Results:\n{context}\n\nUser Query: {query}\n\nPlease provide a comprehensive answer based on the search results above."
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Stream response from LiteLLM
            response = await litellm.acompletion(
                model=self.current_model.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                stream=True
            )
            
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            print(f"LLM streaming error: {e}")
            yield f"\n\nI apologize, but I encountered an error: {str(e)}"
    
    async def _get_conversation_history(
        self,
        conversation_id: int,
        db: AsyncSession
    ) -> List[Message]:
        """Get conversation history"""
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        return result.scalars().all()
    
    async def _generate_follow_up_questions(
        self,
        original_query: str,
        response: str
    ) -> List[str]:
        """Generate follow-up questions based on the response"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "Generate 3 relevant follow-up questions based on the conversation. Return only the questions, one per line, without numbering."
                },
                {
                    "role": "user",
                    "content": f"Original question: {original_query}\n\nAnswer: {response}\n\nGenerate 3 follow-up questions:"
                }
            ]
            
            response = await litellm.acompletion(
                model=self.current_model.model_name,
                messages=messages,
                temperature=0.8,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            questions = [q.strip() for q in content.split('\n') if q.strip() and not q.strip().startswith(('-', '*', '1', '2', '3'))]
            
            return questions[:3]
        
        except Exception as e:
            print(f"Follow-up generation error: {e}")
            return []

