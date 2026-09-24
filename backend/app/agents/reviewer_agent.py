"""
AI Council - Reviewer Agent
Critical reviewer that evaluates agent outputs and provides feedback
"""
from typing import Dict, Any, Optional, List
from app.agents.base_agent import BaseAgent
from app.llm.groq_client import GroqClient
from app.core.config import settings
from app.core.logging import setup_logging
import logging

logger = logging.getLogger(__name__)


class ReviewerAgent(BaseAgent):
    """
    Reviewer Agent
    Critically evaluates outputs from all specialized agents
    Identifies gaps, inconsistencies, and areas for improvement
    """
    
    def __init__(self):
        super().__init__(
            agent_id="reviewer_agent",
            agent_name="Critical Reviewer",
            agent_type="reviewer",
            description="Critically evaluates agent outputs and provides feedback"
        )
        self.groq_client = None  # Lazy initialization
    
    async def execute(
        self,
        question: str,
        agent_outputs: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute critical review of agent outputs
        
        Args:
            question: The original research question
            agent_outputs: Dictionary of outputs from all agents
            context: Additional context
            
        Returns:
            Review feedback and recommendations
        """
        logger.info(f"Reviewer agent executing critical review")
        
        # Lazy initialize Groq client
        if self.groq_client is None:
            self.groq_client = GroqClient()
        
        # Build prompt with all agent outputs
        prompt = self._build_prompt(question, agent_outputs, context)
        
        # Execute with Groq
        try:
            response = await self.groq_client.generate(
                prompt=prompt,
                temperature=0.3,  # Lower temperature for more critical analysis
                max_tokens=settings.GROQ_MAX_TOKENS
            )
            
            # Parse response
            result = self._parse_response(response, question, agent_outputs)
            
            logger.info(f"Reviewer agent completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Reviewer agent execution failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "question": question
            }
    
    def _build_prompt(
        self,
        question: str,
        agent_outputs: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the prompt for the reviewer agent"""
        prompt = f"""You are a Critical Reviewer for the AI Council system. Your task is to critically evaluate the outputs from multiple specialized agents and provide constructive feedback.

ORIGINAL RESEARCH QUESTION:
{question}

"""
        
        # Add all agent outputs
        prompt += "\n=== AGENT OUTPUTS ===\n"
        for agent_id, output in agent_outputs.items():
            if isinstance(output, dict) and "raw_output" in output:
                prompt += f"\n{agent_id.upper()}:\n{output['raw_output']}\n"
            else:
                prompt += f"\n{agent_id.upper()}:\n{str(output)}\n"
        
        prompt += """
INSTRUCTIONS:
1. Critically evaluate each agent's output
2. Identify gaps, inconsistencies, or missing information
3. Assess the quality and completeness of each analysis
4. Identify conflicting information between agents
5. Provide specific feedback for each agent
6. Suggest areas that need additional investigation
7. Assess overall confidence in the collective outputs
8. Provide recommendations for improvement

OUTPUT FORMAT:
Provide your review in the following JSON-like structure (without the outer quotes):
{
    "agent_evaluations": {
        "research_agent": {"quality": "high/medium/low", "feedback": "specific feedback", "gaps": ["gap1", "gap2"]},
        "technical_agent": {"quality": "high/medium/low", "feedback": "specific feedback", "gaps": ["gap1", "gap2"]},
        "cost_agent": {"quality": "high/medium/low", "feedback": "specific feedback", "gaps": ["gap1", "gap2"]},
        "data_agent": {"quality": "high/medium/low", "feedback": "specific feedback", "gaps": ["gap1", "gap2"]},
        "product_agent": {"quality": "high/medium/low", "feedback": "specific feedback", "gaps": ["gap1", "gap2"]},
        "security_agent": {"quality": "high/medium/low", "feedback": "specific feedback", "gaps": ["gap1", "gap2"]}
    },
    "inconsistencies": ["inconsistency1", "inconsistency2"],
    "missing_information": ["missing1", "missing2"],
    "additional_investigation_needed": ["area1", "area2"],
    "overall_confidence": "high/medium/low",
    "review_summary": "concise summary of the review",
    "recommendations": ["recommendation1", "recommendation2"]
}

Provide your critical review:
"""
        
        return prompt
    
    def _parse_response(
        self,
        response: str,
        question: str,
        agent_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse the LLM response into structured output"""
        # Build agent evaluations structure
        agent_evaluations = {}
        for agent_id in agent_outputs.keys():
            agent_evaluations[agent_id] = {
                "quality": "medium",
                "feedback": "Evaluation pending",
                "gaps": []
            }
        
        return {
            "status": "completed",
            "question": question,
            "raw_output": response,
            "structured_output": {
                "agent_evaluations": agent_evaluations,
                "inconsistencies": [],
                "missing_information": [],
                "additional_investigation_needed": [],
                "overall_confidence": "medium",
                "review_summary": response[:500] if len(response) > 500 else response,
                "recommendations": []
            }
        }
