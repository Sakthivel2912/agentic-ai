"""
AI Council - Data Agent
Specialized agent for data analysis and statistical evaluation
"""
from typing import Dict, Any, Optional
from app.agents.base_agent import BaseAgent
from app.llm.groq_client import GroqClient
from app.core.config import settings
from app.core.logging import setup_logging
import logging

logger = logging.getLogger(__name__)


class DataAgent(BaseAgent):
    """Data Agent - Analyzes data requirements, statistical implications, and data strategies"""
    
    def __init__(self):
        super().__init__(
            agent_id="data_agent",
            agent_name="Data Analysis Agent",
            agent_type="data",
            description="Analyzes data requirements, statistical implications, and data strategies"
        )
        self.groq_client = None  # Lazy initialization
    
    async def execute(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        previous_outputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        logger.info(f"Data agent executing: {question}")
        
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
            logger.info(f"Data agent completed successfully")
            return result
        except Exception as e:
            logger.error(f"Data agent execution failed: {e}")
            return {"status": "failed", "error": str(e), "question": question}
    
    def _build_prompt(self, question: str, context: Optional[Dict[str, Any]] = None, previous_outputs: Optional[Dict[str, Any]] = None) -> str:
        prompt = f"""You are a Data Analysis Agent. Analyze data requirements and implications.

RESEARCH QUESTION:
{question}

"""
        if previous_outputs:
            for agent_id, output in previous_outputs.items():
                prompt += f"\n{agent_id.upper()} OUTPUT:\n{output.get('raw_output', '')}\n"
        
        prompt += """
INSTRUCTIONS:
1. Identify data requirements
2. Assess data availability and quality
3. Consider statistical methods
4. Identify data challenges
5. Suggest data strategies

OUTPUT FORMAT:
{
    "data_requirements": ["req1", "req2"],
    "data_availability": "availability assessment",
    "statistical_methods": ["method1", "method2"],
    "data_challenges": ["challenge1", "challenge2"],
    "data_strategies": ["strategy1", "strategy2"],
    "data_summary": "concise data summary",
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
                "data_requirements": [],
                "data_availability": "TBD",
                "statistical_methods": [],
                "data_challenges": [],
                "data_strategies": [],
                "data_summary": response[:500] if len(response) > 500 else response,
                "confidence_level": "medium"
            }
        }
