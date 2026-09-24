"""
AI Council - Product Agent
Specialized agent for product and business strategy analysis
"""
from typing import Dict, Any, Optional
from app.agents.base_agent import BaseAgent
from app.llm.groq_client import GroqClient
from app.core.config import settings
from app.core.logging import setup_logging
import logging

logger = logging.getLogger(__name__)


class ProductAgent(BaseAgent):
    """Product Agent - Analyzes product strategy, business implications, and market fit"""
    
    def __init__(self):
        super().__init__(
            agent_id="product_agent",
            agent_name="Product/Business Agent",
            agent_type="product",
            description="Analyzes product strategy, business implications, and market fit"
        )
        self.groq_client = None  # Lazy initialization
    
    async def execute(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        previous_outputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        logger.info(f"Product agent executing: {question}")
        
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
            logger.info(f"Product agent completed successfully")
            return result
        except Exception as e:
            logger.error(f"Product agent execution failed: {e}")
            return {"status": "failed", "error": str(e), "question": question}
    
    def _build_prompt(self, question: str, context: Optional[Dict[str, Any]] = None, previous_outputs: Optional[Dict[str, Any]] = None) -> str:
        prompt = f"""You are a Product/Business Agent. Analyze product strategy and business implications.

RESEARCH QUESTION:
{question}

"""
        if previous_outputs:
            for agent_id, output in previous_outputs.items():
                prompt += f"\n{agent_id.upper()} OUTPUT:\n{output.get('raw_output', '')}\n"
        
        prompt += """
INSTRUCTIONS:
1. Assess product strategy alignment
2. Consider market fit and positioning
3. Identify business value and ROI
4. Consider competitive landscape
5. Suggest product recommendations

OUTPUT FORMAT:
{
    "product_strategy": "strategy assessment",
    "market_fit": "market fit analysis",
    "business_value": "business value details",
    "competitive_landscape": "competitive analysis",
    "recommendations": ["recommendation1", "recommendation2"],
    "product_summary": "concise product summary",
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
                "product_strategy": response[:300] if len(response) > 300 else response,
                "market_fit": "TBD",
                "business_value": "",
                "competitive_landscape": "",
                "recommendations": [],
                "product_summary": response[:500] if len(response) > 500 else response,
                "confidence_level": "medium"
            }
        }
