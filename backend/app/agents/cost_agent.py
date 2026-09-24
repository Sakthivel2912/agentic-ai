"""
AI Council - Cost Agent
Specialized agent for cost and infrastructure analysis
"""
from typing import Dict, Any, Optional
from app.agents.base_agent import BaseAgent
from app.llm.groq_client import GroqClient
from app.core.config import settings
from app.core.logging import setup_logging
import logging

logger = logging.getLogger(__name__)


class CostAgent(BaseAgent):
    """
    Cost Agent
    Analyzes costs, infrastructure requirements, and financial implications
    """
    
    def __init__(self):
        super().__init__(
            agent_id="cost_agent",
            agent_name="Cost/Infrastructure Agent",
            agent_type="cost",
            description="Analyzes costs, infrastructure requirements, and financial implications"
        )
        self.groq_client = None  # Lazy initialization
    
    async def execute(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        previous_outputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute cost analysis"""
        logger.info(f"Cost agent executing: {question}")
        
        # Lazy initialize Groq client
        if self.groq_client is None:
            self.groq_client = GroqClient()
        
        prompt = self._build_prompt(question, context, previous_outputs)
        
        try:
            response = await self.groq_client.generate(
                prompt=prompt,
                temperature=settings.GROQ_TEMPERATURE,
                max_tokens=settings.GROQ_MAX_TOKENS
            )
            
            result = self._parse_response(response, question)
            logger.info(f"Cost agent completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Cost agent execution failed: {e}")
            return {"status": "failed", "error": str(e), "question": question}
    
    def _build_prompt(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        previous_outputs: Optional[Dict[str, Any]] = None
    ) -> str:
        prompt = f"""You are a Cost/Infrastructure Agent. Analyze the cost and infrastructure implications.

RESEARCH QUESTION:
{question}

"""
        if previous_outputs:
            for agent_id, output in previous_outputs.items():
                prompt += f"\n{agent_id.upper()} OUTPUT:\n{output.get('raw_output', '')}\n"
        
        prompt += """
INSTRUCTIONS:
1. Estimate infrastructure requirements
2. Identify cost factors and considerations
3. Assess operational costs
4. Consider scalability costs
5. Identify cost optimization opportunities

OUTPUT FORMAT:
{
    "infrastructure_requirements": ["req1", "req2"],
    "cost_factors": ["factor1", "factor2"],
    "estimated_costs": "cost estimate",
    "operational_costs": "operational cost details",
    "scalability_costs": "scalability cost details",
    "optimization_opportunities": ["opportunity1", "opportunity2"],
    "cost_summary": "concise cost summary",
    "confidence_level": "high/medium/low"
}

Provide your response:
"""
        return prompt
    
    def _parse_response(self, response: str, question: str) -> Dict[str, Any]:
        return {
            "status": "completed",
            "question": question,
            "raw_output": response,
            "structured_output": {
                "infrastructure_requirements": [],
                "cost_factors": [],
                "estimated_costs": "TBD",
                "operational_costs": response[:300] if len(response) > 300 else response,
                "scalability_costs": "",
                "optimization_opportunities": [],
                "cost_summary": response[:500] if len(response) > 500 else response,
                "confidence_level": "medium"
            }
        }
