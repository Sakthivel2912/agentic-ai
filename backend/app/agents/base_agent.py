"""
AI Council - Base Agent Class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseAgent(ABC):
    """
    Base class for all AI agents
    """
    
    def __init__(self, agent_id: str, agent_name: str, agent_type: str, description: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.description = description
    
    @abstractmethod
    async def execute(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        previous_outputs: Optional[Dict[str, Any]] = None,
        rag_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the agent's primary function
        
        Args:
            question: The research question
            context: Additional context
            previous_outputs: Outputs from previous agents
            rag_results: RAG retrieval results if enabled
            
        Returns:
            Agent output with findings and metadata
        """
        pass
