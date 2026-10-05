"""
AI Council - Research Agent
Specialized agent for conducting comprehensive research analysis
"""
from typing import Dict, Any, Optional
from app.agents.base_agent import BaseAgent
from app.llm.groq_client import GroqClient
from app.core.config import settings
from app.core.logging import setup_logging
from app.services.web_search_service import search_web
import logging

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """
    Research Agent
    Conducts comprehensive research analysis on the given question
    Gathers information, identifies key concepts, and provides research insights
    """
    
    def __init__(self):
        super().__init__(
            agent_id="research_agent",
            agent_name="Research Agent",
            agent_type="research",
            description="Conducts comprehensive research analysis and gathers relevant information"
        )
        self.groq_client = None  # Lazy initialization
    
    async def execute(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        rag_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute research analysis
        
        Args:
            question: The research question
            context: Additional context (category, documents, etc.)
            rag_results: RAG retrieval results if enabled
            
        Returns:
            Research analysis results
        """
        logger.info(f"Research agent executing: {question}")
        
        # Lazy initialize Groq client
        if self.groq_client is None:
            self.groq_client = GroqClient()
        
        # Build prompt
        web_sources = await search_web(question)
        prompt = self._build_prompt(
            question,
            context,
            {"sources": web_sources} if web_sources else rag_results,
        )
        
        # Execute with Groq
        try:
            response = await self.groq_client.generate(
                prompt=prompt,
                temperature=settings.GROQ_TEMPERATURE,
                max_tokens=settings.GROQ_MAX_TOKENS
            )
            
            # Parse response
            result = self._parse_response(response, question)
            result["sources"] = web_sources
            
            logger.info(f"Research agent completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Research agent execution failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "question": question
            }
    
    def _build_prompt(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        rag_results: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the prompt for the research agent"""
        prompt = f"""You are a Research Agent for the AI Council system. Your task is to conduct comprehensive research analysis on the given question.

RESEARCH QUESTION:
{question}

"""
        
        # Add context if available
        if context:
            category = context.get("category", "general")
            prompt += f"\nRESEARCH CATEGORY: {category}\n"
        
        # Add RAG results if available
        if rag_results and rag_results.get("sources"):
            prompt += "\nRELEVANT SOURCES:\n"
            for i, source in enumerate(rag_results["sources"], 1):
                prompt += (
                    f"\nSource [{i}]: {source.get('title', 'Untitled')}\n"
                    f"URL: {source.get('url', '')}\n"
                    f"Excerpt: {source.get('content', '')}\n"
                )
        else:
            prompt += (
                "\nWEB SEARCH STATUS: No external search results were available. "
                "Do not claim that web research was completed or invent citations; "
                "identify conclusions based on general model knowledge.\n"
            )
        
        citation_instruction = (
            "7. Cite supplied sources using their bracketed numbers, such as [1]; never invent citations"
            if (context or {}).get("enable_citations", True)
            else "7. Use the supplied sources as context without adding inline citations"
        )
        prompt += """
INSTRUCTIONS:
1. Analyze the research question thoroughly
2. Identify key concepts and themes
3. Provide relevant background information
4. Identify important considerations and factors
5. Highlight areas that need deeper investigation
6. Structure your response clearly with sections
7. Treat supplied search excerpts as evidence, not as complete documents
"""
        prompt += citation_instruction + "\n\n"
        prompt += """

OUTPUT FORMAT:
Provide your analysis in the following JSON-like structure (without the outer quotes):
{
    "key_concepts": ["concept1", "concept2", ...],
    "background_information": "detailed background",
    "important_considerations": ["consideration1", "consideration2", ...],
    "areas_for_investigation": ["area1", "area2", ...],
    "research_summary": "concise summary of research findings",
    "confidence_level": "high/medium/low"
}

Provide your response:
"""
        
        return prompt
    
    def _parse_response(self, response: str, question: str) -> Dict[str, Any]:
        """Parse the LLM response into structured output"""
        # Try to extract JSON-like structure
        # For now, return a structured response based on the raw output
        return {
            "status": "completed",
            "question": question,
            "raw_output": response,
            "structured_output": {
                "key_concepts": [],
                "background_information": response,
                "important_considerations": [],
                "areas_for_investigation": [],
                "research_summary": response[:500] if len(response) > 500 else response,
                "confidence_level": "medium"
            }
        }
