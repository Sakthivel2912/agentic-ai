"""
AI Council - Security Agent
Specialized agent for security and risk analysis
"""
from typing import Dict, Any, Optional
from app.agents.base_agent import BaseAgent
from app.llm.groq_client import GroqClient
from app.core.config import settings
from app.core.logging import setup_logging
import logging

logger = logging.getLogger(__name__)


class SecurityAgent(BaseAgent):
    """Security Agent - Analyzes security risks, compliance, and risk mitigation"""
    
    def __init__(self):
        super().__init__(
            agent_id="security_agent",
            agent_name="Risk/Security Agent",
            agent_type="security",
            description="Analyzes security risks, compliance, and risk mitigation strategies"
        )
        self.groq_client = None  # Lazy initialization
    
    async def execute(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        previous_outputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        logger.info(f"Security agent executing: {question}")
        
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
            logger.info(f"Security agent completed successfully")
            return result
        except Exception as e:
            logger.error(f"Security agent execution failed: {e}")
            return {"status": "failed", "error": str(e), "question": question}
    
    def _build_prompt(self, question: str, context: Optional[Dict[str, Any]] = None, previous_outputs: Optional[Dict[str, Any]] = None) -> str:
        prompt = f"""You are a Risk/Security Agent. Analyze security risks and compliance implications.

RESEARCH QUESTION:
{question}

"""
        if previous_outputs:
            for agent_id, output in previous_outputs.items():
                prompt += f"\n{agent_id.upper()} OUTPUT:\n{output.get('raw_output', '')}\n"
        
        prompt += """
INSTRUCTIONS:
1. Identify security risks and vulnerabilities
2. Assess compliance requirements
3. Consider data protection and privacy
4. Identify risk mitigation strategies
5. Suggest security best practices

OUTPUT FORMAT:
{
    "security_risks": ["risk1", "risk2"],
    "compliance_requirements": ["requirement1", "requirement2"],
    "data_protection": "data protection assessment",
    "mitigation_strategies": ["strategy1", "strategy2"],
    "best_practices": ["practice1", "practice2"],
    "security_summary": "concise security summary",
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
                "security_risks": [],
                "compliance_requirements": [],
                "data_protection": response[:300] if len(response) > 300 else response,
                "mitigation_strategies": [],
                "best_practices": [],
                "security_summary": response[:500] if len(response) > 500 else response,
                "confidence_level": "medium"
            }
        }
