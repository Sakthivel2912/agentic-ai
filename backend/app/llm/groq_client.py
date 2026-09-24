"""
AI Council - Groq LLM Client
"""
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings
from app.core.logging import setup_logging
import logging

logger = logging.getLogger(__name__)


class GroqClient:
    """
    Groq LLM client for AI agents
    """
    
    def __init__(self):
        """Initialize Groq client"""
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment variables")
        
        self.client = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=settings.GROQ_TEMPERATURE,
            max_tokens=settings.GROQ_MAX_TOKENS,
        )
        self.model_name = settings.GROQ_MODEL
        logger.info(f"Initialized Groq client with model: {self.model_name}")
    
    async def generate_response(
        self,
        system_prompt: str,
        user_message: str,
        **kwargs
    ) -> str:
        """
        Generate a response from Groq LLM
        
        Args:
            system_prompt: System prompt for the LLM
            user_message: User message/question
            **kwargs: Additional parameters for the LLM
            
        Returns:
            Generated response text
        """
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ]
            
            response = await self.client.ainvoke(messages, **kwargs)
            
            logger.info(f"Generated response using {self.model_name}")
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating response from Groq: {e}")
            raise

    async def generate(self, prompt: str, **kwargs) -> str:
        """Compatibility method used by the existing specialist agents."""
        return await self.generate_response(
            system_prompt="You are a specialist member of an AI research council.",
            user_message=prompt,
            **kwargs,
        )
    
    async def generate_structured_response(
        self,
        system_prompt: str,
        user_message: str,
        response_format: dict = None
    ) -> dict:
        """
        Generate a structured response from Groq LLM
        
        Args:
            system_prompt: System prompt for the LLM
            user_message: User message/question
            response_format: Expected response format (if supported)
            
        Returns:
            Structured response as dictionary
        """
        try:
            # For now, return as text and parse later
            # Groq may support structured outputs in the future
            response_text = await self.generate_response(system_prompt, user_message)
            
            # Basic parsing - this can be enhanced based on requirements
            return {
                "content": response_text,
                "model": self.model_name,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error generating structured response from Groq: {e}")
            return {
                "content": None,
                "error": str(e),
                "success": False
            }
    
    def get_model_info(self) -> dict:
        """
        Get information about the current model
        
        Returns:
            Model information dictionary
        """
        return {
            "model_name": self.model_name,
            "temperature": settings.GROQ_TEMPERATURE,
            "max_tokens": settings.GROQ_MAX_TOKENS,
            "api_configured": bool(settings.GROQ_API_KEY)
        }
