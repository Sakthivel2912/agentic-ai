"""
AI Council - Technical Agent
Specialized agent for technical architecture and implementation analysis
"""
from typing import Dict, Any, Optional
from app.agents.base_agent import BaseAgent
from app.llm.groq_client import GroqClient
from app.core.config import settings
from app.core.logging import setup_logging
import logging

logger = logging.getLogger(__name__)


class TechnicalAgent(BaseAgent):
    """
    Technical Agent
    Analyzes technical aspects, architecture, implementation details, and technical feasibility
    """
    
    def __init__(self):
        super().__init__(
            agent_id="technical_agent",
            agent_name="Technical Agent",
            agent_type="technical",
            description="Analyzes technical architecture, implementation details, and feasibility"
        )
        self.groq_client = None  # Lazy initialization
    
    async def execute(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        previous_outputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute technical analysis
        
        Args:
            question: The research question
            context: Additional context
            previous_outputs: Outputs from previous agents (e.g., research agent)
            
        Returns:
            Technical analysis results
        """
        logger.info(f"Technical agent executing: {question}")
        
        # Lazy initialize Groq client
        if self.groq_client is None:
            self.groq_client = GroqClient()
        
        # Build prompt with previous outputs
        prompt = self._build_prompt(question, context, previous_outputs)
        
        # Execute with Groq
        try:
            response = await self.groq_client.generate(
                prompt=prompt,
                temperature=settings.GROQ_TEMPERATURE,
                max_tokens=settings.GROQ_MAX_TOKENS
            )
            
            # Parse response
            result = self._parse_response(response, question)
            
            logger.info(f"Technical agent completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Technical agent execution failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "question": question
            }
    
    def _build_prompt(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        previous_outputs: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the prompt for the technical agent"""
        prompt = f"""You are a Technical Agent for the AI Council system. Your task is to analyze the technical aspects of the research question.

RESEARCH QUESTION:
{question}

"""
        
        # Add previous research output if available
        if previous_outputs and "research_agent" in previous_outputs:
            research_output = previous_outputs["research_agent"]
            prompt += f"\nRESEARCH FINDINGS:\n{research_output.get('raw_output', '')}\n"
        
        prompt += """
INSTRUCTIONS:
1. Analyze technical requirements and constraints
2. Identify appropriate technologies and frameworks
3. Assess technical feasibility
4. Consider scalability and performance implications
5. Identify potential technical challenges
6. Suggest technical approaches and solutions

OUTPUT FORMAT:
Provide your analysis in the following JSON-like structure (without the outer quotes):
{
    "technical_requirements": ["requirement1", "requirement2", ...],
    "recommended_technologies": ["tech1", "tech2", ...],
    "feasibility_assessment": "high/medium/low",
    "scalability_considerations": "consideration details",
    "potential_challenges": ["challenge1", "challenge2", ...],
    "technical_approaches": ["approach1", "approach2", ...],
    "technical_summary": "concise technical summary",
    "confidence_level": "high/medium/low"
}

Provide your response:
"""
        
        return prompt
    
    def _parse_response(self, response: str, question: str) -> Dict[str, Any]:
        """Parse the LLM response into structured output"""
        return {
            "status": "completed",
            "question": question,
            "raw_output": response,
            "structured_output": {
                "technical_requirements": [],
                "recommended_technologies": [],
                "feasibility_assessment": "medium",
                "scalability_considerations": response[:300] if len(response) > 300 else response,
                "potential_challenges": [],
                "technical_approaches": [],
                "technical_summary": response[:500] if len(response) > 500 else response,
                "confidence_level": "medium"
            }
        }
