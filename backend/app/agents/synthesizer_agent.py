"""
AI Council - Synthesizer Agent
Master synthesizer that combines all agent outputs into a final answer
"""
from typing import Dict, Any, Optional
from app.agents.base_agent import BaseAgent
from app.llm.groq_client import GroqClient
from app.core.config import settings
from app.core.logging import setup_logging
import logging

logger = logging.getLogger(__name__)


class SynthesizerAgent(BaseAgent):
    """
    Synthesizer Agent
    Combines outputs from all specialized agents into a comprehensive final answer
    Integrates research, technical, cost, data, product, and security perspectives
    """
    
    def __init__(self):
        super().__init__(
            agent_id="synthesizer_agent",
            agent_name="Master Synthesizer",
            agent_type="synthesizer",
            description="Combines all agent outputs into a comprehensive final answer"
        )
        self.groq_client = None  # Lazy initialization
    
    async def execute(
        self,
        question: str,
        agent_outputs: Dict[str, Any],
        reviewer_feedback: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute synthesis of all agent outputs
        
        Args:
            question: The original research question
            agent_outputs: Dictionary of outputs from all agents
            reviewer_feedback: Feedback from the reviewer agent (if available)
            context: Additional context
            
        Returns:
            Final synthesized answer
        """
        logger.info(f"Synthesizer agent executing synthesis")
        
        # Lazy initialize Groq client
        if self.groq_client is None:
            self.groq_client = GroqClient()
        
        # Build prompt with all agent outputs and reviewer feedback
        prompt = self._build_prompt(question, agent_outputs, reviewer_feedback, context)
        
        # Execute with Groq
        try:
            response = await self.groq_client.generate(
                prompt=prompt,
                temperature=0.5,  # Balanced temperature for synthesis
                max_tokens=min(settings.GROQ_MAX_TOKENS, 2048)
            )
            
            # Parse response
            result = self._parse_response(response, question, agent_outputs)
            
            logger.info(f"Synthesizer agent completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Synthesizer agent execution failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "question": question
            }
    
    def _build_prompt(
        self,
        question: str,
        agent_outputs: Dict[str, Any],
        reviewer_feedback: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the prompt for the synthesizer agent"""
        prompt = f"""You are the Master Synthesizer for the AI Council system. Your task is to combine outputs from multiple specialized agents into a comprehensive, well-structured final answer.

ORIGINAL RESEARCH QUESTION:
{question}

"""
        
        # Add all agent outputs
        prompt += "\n=== AGENT OUTPUTS ===\n"
        for agent_id, output in agent_outputs.items():
            if isinstance(output, dict) and "raw_output" in output:
                output_text = str(output["raw_output"])
            else:
                output_text = str(output)
            if len(output_text) > 1800:
                output_text = output_text[:1800] + "\n[Output truncated for synthesis token budget.]"
            prompt += f"\n{agent_id.upper()}:\n{output_text}\n"
        
        # Add reviewer feedback if available
        if reviewer_feedback:
            prompt += "\n=== REVIEWER FEEDBACK ===\n"
            if isinstance(reviewer_feedback, dict) and "raw_output" in reviewer_feedback:
                reviewer_text = str(reviewer_feedback["raw_output"])
            else:
                reviewer_text = str(reviewer_feedback)
            if len(reviewer_text) > 1800:
                reviewer_text = reviewer_text[:1800] + "\n[Feedback truncated for synthesis token budget.]"
            prompt += f"\n{reviewer_text}\n"

        sources = (context or {}).get("sources", [])
        if sources:
            prompt += "\n=== WEB SEARCH RESULTS ===\n"
            for index, source in enumerate(sources, 1):
                prompt += f"[{index}] {source.get('title', 'Untitled')} - {source.get('url', '')}\n"
        if (context or {}).get("enable_citations", True) and sources:
            prompt += "Cite factual claims with the matching source numbers, for example [1]. Do not invent citations.\n"
        elif (context or {}).get("enable_citations", True):
            prompt += "No web sources were returned. Do not fabricate citations; state when a claim is based on general model knowledge.\n"
        
        prompt += """
INSTRUCTIONS:
1. Synthesize information from all agent perspectives
2. Identify key themes and insights across all analyses
3. Address any conflicts or inconsistencies
3. Provide a comprehensive answer that integrates all viewpoints
4. Structure the answer clearly with sections and subsections
5. Include actionable recommendations
6. Highlight any limitations or areas of uncertainty
7. Provide a clear executive summary
8. Consider the reviewer's feedback and address any gaps identified

OUTPUT FORMAT:
Provide your synthesis in the following structure:

## Executive Summary
[Brief 2-3 sentence summary of the key findings and recommendations]

## Comprehensive Analysis
[Detailed analysis integrating all agent perspectives]

### Research Perspective
[Summary of research findings]

### Technical Perspective
[Summary of technical analysis]

### Cost & Infrastructure Perspective
[Summary of cost analysis]

### Data Perspective
[Summary of data analysis]

### Product & Business Perspective
[Summary of product analysis]

### Security & Risk Perspective
[Summary of security analysis]

## Key Insights
[Bullet points of the most important insights from the synthesis]

## Recommendations
[Specific, actionable recommendations based on the synthesis]

## Considerations & Limitations
[Any important considerations, limitations, or areas requiring further investigation]

## Conclusion
[Concluding remarks and final recommendation]

Provide your comprehensive synthesis:
"""
        
        return prompt
    
    def _parse_response(
        self,
        response: str,
        question: str,
        agent_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse the LLM response into structured output"""
        return {
            "status": "completed",
            "question": question,
            "raw_output": response,
            "structured_output": {
                "executive_summary": self._extract_section(response, "Executive Summary"),
                "comprehensive_analysis": response,
                "key_insights": [],
                "recommendations": [],
                "considerations": self._extract_section(response, "Considerations & Limitations"),
                "conclusion": self._extract_section(response, "Conclusion")
            }
        }
    
    def _extract_section(self, text: str, section_title: str) -> str:
        """Extract a section from the response text"""
        # Simple extraction - in production, use more sophisticated parsing
        lines = text.split('\n')
        section_lines = []
        in_section = False
        
        for line in lines:
            if section_title in line:
                in_section = True
                continue
            if in_section and line.startswith('##'):
                break
            if in_section:
                section_lines.append(line)
        
        return '\n'.join(section_lines).strip() if section_lines else ""
