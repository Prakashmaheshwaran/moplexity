from typing import List, Dict, AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models import Message, LLMModel
from app.schemas.llm import infer_provider_type
import litellm
import os


class LLMService:
    def __init__(self):
        self.current_model = None

    async def set_model(self, model_id: int, db: AsyncSession) -> bool:
        """Set the current model by fetching from database"""
        try:
            result = await db.execute(
                select(LLMModel).where(LLMModel.id == model_id)
            )
            model = result.scalar_one_or_none()

            if not model or not model.is_active:
                return False

            self.current_model = model

            # Infer provider type from model_name if not set
            provider_type = model.provider_type
            if not provider_type:
                provider_type = infer_provider_type(model.model_name)

            # Set API key for this provider dynamically
            if provider_type:
                api_key_env_var = self._get_api_key_env_var(provider_type)
                os.environ[api_key_env_var] = model.api_key

            # Set base URL if provided (for custom endpoints like Ollama)
            if model.base_url:
                # LiteLLM uses custom_base_url parameter
                # For Ollama, we need to set it per model call
                litellm.drop_params = True  # Don't drop custom params
                # Store base_url in model object for use in completion calls

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
            "ollama": "OLLAMA_API_KEY",  # Ollama typically doesn't need API key but included for completeness
        }
        return provider_env_vars.get(provider_type, f"{provider_type.upper()}_API_KEY")
    
    def _format_sources_for_context(self, search_results: List[Dict]) -> str:
        """Format search results into context for the LLM"""
        if not search_results:
            return "No search results were found for this query. You should still provide a helpful answer based on your general knowledge."
        
        context = "Here are the search results to help answer the query:\n\n"
        for idx, result in enumerate(search_results[:10], 1):
            source_type = result.get('source_type', 'web')
            title = result.get('title', 'Untitled')
            url = result.get('url', '')
            snippet = result.get('snippet', '')
            
            if title and snippet:  # Only include valid results
                context += f"[{idx}] {title}\n"
                if url:
                    context += f"Source: {source_type.upper()} - {url}\n"
                context += f"Content: {snippet}\n\n"
        
        return context
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for the LLM"""
        return """You are Moplexity, an AI search assistant that provides accurate, well-researched answers.

Your role:
1. Always provide a helpful answer, even if search results are limited or unavailable
2. When search results are provided, analyze them carefully and synthesize information from multiple sources
3. If search results are insufficient or missing, use your general knowledge to provide the best possible answer
4. Cite sources using [1], [2], etc. format when referencing search results
5. If information is conflicting, mention different perspectives
6. Be conversational but professional
7. Never refuse to answer - always provide helpful information to the best of your ability

Format your response:
- Use markdown for better readability
- Reference sources inline using [1], [2] format when available
- Organize information logically
- Include relevant details from the sources when available
- If no sources are available, clearly state you're providing a general knowledge answer"""
    
    async def generate_response(
        self,
        query: str,
        search_results: List[Dict],
        conversation_id: int,
        db: AsyncSession,
        model_id: Optional[int] = None
    ) -> Dict:
        """Generate a complete AI response"""

        # Set model if specified, otherwise try to get default
        if model_id:
            success = await self.set_model(model_id, db)
            if not success:
                return {
                    "content": "I apologize, but the selected model is not available or inactive.",
                    "follow_up_questions": []
                }
        elif not self.current_model:
            # Try to get first active model as default
            result = await db.execute(
                select(LLMModel)
                .where(LLMModel.is_active == True)
                .limit(1)
            )
            default_model = result.scalar_one_or_none()
            if default_model:
                success = await self.set_model(default_model.id, db)
                if not success:
                    return {
                        "content": "I apologize, but no active model is available.",
                        "follow_up_questions": []
                    }
            else:
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
        if search_results:
            user_message = f"Search Results:\n{context}\n\nUser Query: {query}\n\nPlease provide a comprehensive answer based on the search results above. If the search results don't fully address the query, supplement with your general knowledge."
        else:
            user_message = f"User Query: {query}\n\nNo search results were found. Please provide a helpful answer based on your general knowledge. Be informative and accurate."
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Prepare completion parameters
            completion_params = {
                "model": self.current_model.model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            # Add base_url if provided (for custom endpoints like Ollama)
            if self.current_model.base_url:
                completion_params["api_base"] = self.current_model.base_url
            
            # Call LiteLLM
            response = await litellm.acompletion(**completion_params)
            
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

        # Set model if specified, otherwise try to get default
        if model_id:
            success = await self.set_model(model_id, db)
            if not success:
                yield "I apologize, but the selected model is not available or inactive."
                return
        elif not self.current_model:
            # Try to get first active model as default
            result = await db.execute(
                select(LLMModel)
                .where(LLMModel.is_active == True)
                .limit(1)
            )
            default_model = result.scalar_one_or_none()
            if default_model:
                success = await self.set_model(default_model.id, db)
                if not success:
                    yield "I apologize, but no active model is available."
                    return
            else:
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
        if search_results:
            user_message = f"Search Results:\n{context}\n\nUser Query: {query}\n\nPlease provide a comprehensive answer based on the search results above. If the search results don't fully address the query, supplement with your general knowledge."
        else:
            user_message = f"User Query: {query}\n\nNo search results were found. Please provide a helpful answer based on your general knowledge. Be informative and accurate."
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Prepare completion parameters
            completion_params = {
                "model": self.current_model.model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000,
                "stream": True
            }
            
            # Add base_url if provided (for custom endpoints like Ollama)
            if self.current_model.base_url:
                completion_params["api_base"] = self.current_model.base_url
            
            # Stream response from LiteLLM
            response = await litellm.acompletion(**completion_params)
            
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
    
    async def _evaluate_result_quality(
        self,
        query: str,
        search_results: List[Dict],
        min_quality_score: float = 0.3  # Lowered threshold to be less strict
    ) -> Dict:
        """Evaluate the quality of search results
        
        Returns:
            Dict with 'is_sufficient' (bool) and 'score' (float 0-1)
        """
        if not search_results:
            return {
                "is_sufficient": False,
                "score": 0.0,
                "reason": "No results found"
            }
        
        # Count valid results
        valid_results = [r for r in search_results if r.get('title') and r.get('snippet')]
        
        # If we have at least 1 valid result, consider it sufficient (AI can work with it)
        if len(valid_results) >= 1:
            return {
                "is_sufficient": True,
                "score": min(len(valid_results) / 5.0, 1.0),
                "reason": f"Found {len(valid_results)} valid results",
                "result_count": len(valid_results),
                "avg_snippet_quality": 0.5
            }
        
        result_count_score = min(len(valid_results) / 5.0, 1.0)  # Normalize to 0-1, target 5+ results
        
        # Check snippet quality (length and content)
        snippet_scores = []
        for result in valid_results:
            snippet = result.get('snippet', '')
            snippet_length_score = min(len(snippet) / 200.0, 1.0)  # Prefer 200+ char snippets
            
            # Simple relevance check: does snippet contain query terms?
            query_terms = set(query.lower().split())
            snippet_lower = snippet.lower()
            relevance_score = sum(1 for term in query_terms if term in snippet_lower) / max(len(query_terms), 1)
            
            snippet_scores.append((snippet_length_score + relevance_score) / 2)
        
        avg_snippet_score = sum(snippet_scores) / len(snippet_scores) if snippet_scores else 0.0
        
        # Combined quality score
        quality_score = (result_count_score * 0.4) + (avg_snippet_score * 0.6)
        
        is_sufficient = quality_score >= min_quality_score
        
        reason = "Results are sufficient" if is_sufficient else f"Results quality score {quality_score:.2f} below threshold {min_quality_score}"
        
        return {
            "is_sufficient": is_sufficient,
            "score": quality_score,
            "reason": reason,
            "result_count": len(valid_results),
            "avg_snippet_quality": avg_snippet_score
        }
    
    async def _generate_follow_up_questions(
        self,
        original_query: str,
        response: str
    ) -> List[str]:
        """Generate follow-up questions from user's perspective as commands/statements"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "Generate 3 relevant follow-up requests from the user's perspective to learn more about the topic. These should be phrased as direct commands or statements (e.g., 'Tell me more about X', 'Explain Y in detail', 'What are the benefits of Z'), not as questions. Return only the requests, one per line, without numbering or question marks."
                },
                {
                    "role": "user",
                    "content": f"Original question: {original_query}\n\nAnswer: {response}\n\nGenerate 3 follow-up requests from the user's perspective (as commands/statements, not questions):"
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
            # Remove question marks if present
            questions = [q.rstrip('?') for q in questions]
            
            return questions[:3]
        
        except Exception as e:
            print(f"Follow-up generation error: {e}")
            return []

