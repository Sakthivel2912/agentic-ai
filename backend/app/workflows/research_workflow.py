"""
AI Council - Research Workflow
LangGraph workflow for multi-agent research orchestration
"""
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from operator import add
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.models.research_session import SessionStatus
from app.models.agent_execution import AgentType
from app.agents.research_agent import ResearchAgent
from app.agents.technical_agent import TechnicalAgent
from app.agents.cost_agent import CostAgent
from app.agents.data_agent import DataAgent
from app.agents.product_agent import ProductAgent
from app.agents.security_agent import SecurityAgent
from app.agents.reviewer_agent import ReviewerAgent
from app.agents.synthesizer_agent import SynthesizerAgent
from app.core.logging import setup_logging
import logging

logger = logging.getLogger(__name__)


class ResearchState(TypedDict):
    """
    Research workflow state
    Shared state passed between agent nodes in the workflow
    """
    # Session information
    session_id: str
    user_id: str
    question: str
    title: str
    category: str
    selected_agents: List[str]
    
    # RAG configuration
    enable_rag: bool
    enable_review: bool
    enable_citations: bool
    selected_document_ids: List[str]
    
    # Agent outputs (accumulated)
    agent_outputs: Annotated[Dict[str, Any], add]
    
    # Reviewer feedback
    reviewer_feedback: Optional[Dict[str, Any]]
    
    # Final results
    final_answer: Optional[str]
    sources: List[Dict[str, Any]]
    
    # Workflow status
    current_stage: str
    progress: float
    error_message: Optional[str]
    
    # Execution tracking
    agent_executions: List[Dict[str, Any]]
    
    # Metadata
    metadata: Dict[str, Any]


class ResearchWorkflow:
    """
    Research workflow orchestrator using LangGraph
    Manages the multi-agent research process
    """
    
    def __init__(self):
        self.memory = MemorySaver()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow graph
        Defines nodes and edges for agent execution
        """
        workflow = StateGraph(ResearchState)
        
        # Add nodes for each agent type
        workflow.add_node("research_agent", self._research_agent_node)
        workflow.add_node("technical_agent", self._technical_agent_node)
        workflow.add_node("cost_agent", self._cost_agent_node)
        workflow.add_node("data_agent", self._data_agent_node)
        workflow.add_node("product_agent", self._product_agent_node)
        workflow.add_node("security_agent", self._security_agent_node)
        workflow.add_node("reviewer_agent", self._reviewer_agent_node)
        workflow.add_node("synthesizer_agent", self._synthesizer_agent_node)
        
        # Set entry point
        workflow.set_entry_point("research_agent")
        
        # Add conditional edges based on selected agents
        workflow.add_conditional_edges(
            "research_agent",
            self._should_continue_to_technical,
            {
                "technical": "technical_agent",
                "cost": "cost_agent",
                "data": "data_agent",
                "product": "product_agent",
                "security": "security_agent",
                "reviewer": "reviewer_agent",
                "synthesizer": "synthesizer_agent",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "technical_agent",
            self._should_continue_to_cost,
            {
                "cost": "cost_agent",
                "data": "data_agent",
                "product": "product_agent",
                "security": "security_agent",
                "reviewer": "reviewer_agent",
                "synthesizer": "synthesizer_agent",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "cost_agent",
            self._should_continue_to_data,
            {
                "data": "data_agent",
                "product": "product_agent",
                "security": "security_agent",
                "reviewer": "reviewer_agent",
                "synthesizer": "synthesizer_agent",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "data_agent",
            self._should_continue_to_product,
            {
                "product": "product_agent",
                "security": "security_agent",
                "reviewer": "reviewer_agent",
                "synthesizer": "synthesizer_agent",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "product_agent",
            self._should_continue_to_security,
            {
                "security": "security_agent",
                "reviewer": "reviewer_agent",
                "synthesizer": "synthesizer_agent",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "security_agent",
            self._should_continue_to_reviewer,
            {
                "reviewer": "reviewer_agent",
                "synthesizer": "synthesizer_agent",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "reviewer_agent",
            self._should_continue_to_synthesizer,
            {
                "synthesizer": "synthesizer_agent",
                "end": END
            }
        )
        
        workflow.add_edge("synthesizer_agent", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    def _should_continue_to_technical(self, state: ResearchState) -> str:
        """Determine next agent after research agent"""
        selected = state["selected_agents"]
        if "technical_agent" in selected:
            return "technical"
        elif "cost_agent" in selected:
            return "cost"
        elif "data_agent" in selected:
            return "data"
        elif "product_agent" in selected:
            return "product"
        elif "security_agent" in selected:
            return "security"
        elif state["enable_review"]:
            return "reviewer"
        else:
            return "synthesizer"
    
    def _should_continue_to_cost(self, state: ResearchState) -> str:
        """Determine next agent after technical agent"""
        selected = state["selected_agents"]
        if "cost_agent" in selected:
            return "cost"
        elif "data_agent" in selected:
            return "data"
        elif "product_agent" in selected:
            return "product"
        elif "security_agent" in selected:
            return "security"
        elif state["enable_review"]:
            return "reviewer"
        else:
            return "synthesizer"
    
    def _should_continue_to_data(self, state: ResearchState) -> str:
        """Determine next agent after cost agent"""
        selected = state["selected_agents"]
        if "data_agent" in selected:
            return "data"
        elif "product_agent" in selected:
            return "product"
        elif "security_agent" in selected:
            return "security"
        elif state["enable_review"]:
            return "reviewer"
        else:
            return "synthesizer"
    
    def _should_continue_to_product(self, state: ResearchState) -> str:
        """Determine next agent after data agent"""
        selected = state["selected_agents"]
        if "product_agent" in selected:
            return "product"
        elif "security_agent" in selected:
            return "security"
        elif state["enable_review"]:
            return "reviewer"
        else:
            return "synthesizer"
    
    def _should_continue_to_security(self, state: ResearchState) -> str:
        """Determine next agent after product agent"""
        selected = state["selected_agents"]
        if "security_agent" in selected:
            return "security"
        elif state["enable_review"]:
            return "reviewer"
        else:
            return "synthesizer"
    
    def _should_continue_to_reviewer(self, state: ResearchState) -> str:
        """Determine next agent after security agent"""
        if state["enable_review"]:
            return "reviewer"
        else:
            return "synthesizer"
    
    def _should_continue_to_synthesizer(self, state: ResearchState) -> str:
        """Determine next agent after reviewer agent"""
        return "synthesizer"
    
    # Agent instances
    research_agent = ResearchAgent()
    technical_agent = TechnicalAgent()
    cost_agent = CostAgent()
    data_agent = DataAgent()
    product_agent = ProductAgent()
    security_agent = SecurityAgent()
    reviewer_agent = ReviewerAgent()
    synthesizer_agent = SynthesizerAgent()
    
    # Agent node implementations
    async def _research_agent_node(self, state: ResearchState) -> ResearchState:
        """Research agent node implementation"""
        logger.info(f"Research agent processing: {state['question']}")
        result = await self.research_agent.execute(
            question=state["question"],
            context={"category": state["category"]},
            rag_results=None  # TODO: Implement RAG retrieval
        )
        state["current_stage"] = "research_analysis"
        state["progress"] = 10.0
        state["agent_outputs"]["research_agent"] = result
        return state
    
    async def _technical_agent_node(self, state: ResearchState) -> ResearchState:
        """Technical agent node implementation"""
        logger.info(f"Technical agent processing: {state['question']}")
        result = await self.technical_agent.execute(
            question=state["question"],
            context={"category": state["category"]},
            previous_outputs=state["agent_outputs"]
        )
        state["current_stage"] = "technical_analysis"
        state["progress"] = 25.0
        state["agent_outputs"]["technical_agent"] = result
        return state
    
    async def _cost_agent_node(self, state: ResearchState) -> ResearchState:
        """Cost agent node implementation"""
        logger.info(f"Cost agent processing: {state['question']}")
        result = await self.cost_agent.execute(
            question=state["question"],
            context={"category": state["category"]},
            previous_outputs=state["agent_outputs"]
        )
        state["current_stage"] = "cost_analysis"
        state["progress"] = 40.0
        state["agent_outputs"]["cost_agent"] = result
        return state
    
    async def _data_agent_node(self, state: ResearchState) -> ResearchState:
        """Data agent node implementation"""
        logger.info(f"Data agent processing: {state['question']}")
        result = await self.data_agent.execute(
            question=state["question"],
            context={"category": state["category"]},
            previous_outputs=state["agent_outputs"]
        )
        state["current_stage"] = "data_analysis"
        state["progress"] = 55.0
        state["agent_outputs"]["data_agent"] = result
        return state
    
    async def _product_agent_node(self, state: ResearchState) -> ResearchState:
        """Product agent node implementation"""
        logger.info(f"Product agent processing: {state['question']}")
        result = await self.product_agent.execute(
            question=state["question"],
            context={"category": state["category"]},
            previous_outputs=state["agent_outputs"]
        )
        state["current_stage"] = "product_analysis"
        state["progress"] = 70.0
        state["agent_outputs"]["product_agent"] = result
        return state
    
    async def _security_agent_node(self, state: ResearchState) -> ResearchState:
        """Security agent node implementation"""
        logger.info(f"Security agent processing: {state['question']}")
        result = await self.security_agent.execute(
            question=state["question"],
            context={"category": state["category"]},
            previous_outputs=state["agent_outputs"]
        )
        state["current_stage"] = "security_analysis"
        state["progress"] = 85.0
        state["agent_outputs"]["security_agent"] = result
        return state
    
    async def _reviewer_agent_node(self, state: ResearchState) -> ResearchState:
        """Reviewer agent node implementation"""
        logger.info(f"Reviewer agent processing outputs")
        result = await self.reviewer_agent.execute(
            question=state["question"],
            agent_outputs=state["agent_outputs"],
            context={"category": state["category"]}
        )
        state["current_stage"] = "critical_review"
        state["progress"] = 90.0
        state["reviewer_feedback"] = result
        return state
    
    async def _synthesizer_agent_node(self, state: ResearchState) -> ResearchState:
        """Synthesizer agent node implementation"""
        logger.info(f"Synthesizer agent combining outputs")
        result = await self.synthesizer_agent.execute(
            question=state["question"],
            agent_outputs=state["agent_outputs"],
            reviewer_feedback=state["reviewer_feedback"],
            context={"category": state["category"]}
        )
        state["current_stage"] = "synthesis"
        state["progress"] = 100.0
        state["final_answer"] = result.get("raw_output", "")
        state["agent_outputs"]["synthesizer_agent"] = result
        return state
    
    async def execute_workflow(
        self,
        session_id: str,
        user_id: str,
        question: str,
        title: str,
        category: str,
        selected_agents: List[str],
        enable_rag: bool,
        enable_review: bool,
        enable_citations: bool,
        selected_document_ids: List[str]
    ) -> ResearchState:
        """
        Execute the research workflow
        
        Args:
            session_id: Research session ID
            user_id: User ID
            question: Research question
            title: Session title
            category: Research category
            selected_agents: List of selected agent IDs
            enable_rag: Whether RAG is enabled
            enable_review: Whether review is enabled
            enable_citations: Whether citations are enabled
            selected_document_ids: List of document IDs for RAG
            
        Returns:
            Final workflow state
        """
        initial_state: ResearchState = {
            "session_id": session_id,
            "user_id": user_id,
            "question": question,
            "title": title,
            "category": category,
            "selected_agents": selected_agents,
            "enable_rag": enable_rag,
            "enable_review": enable_review,
            "enable_citations": enable_citations,
            "selected_document_ids": selected_document_ids,
            "agent_outputs": {},
            "reviewer_feedback": None,
            "final_answer": None,
            "sources": [],
            "current_stage": "initializing",
            "progress": 0.0,
            "error_message": None,
            "agent_executions": [],
            "metadata": {}
        }
        
        try:
            # Execute the workflow graph
            final_state = await self.graph.ainvoke(
                initial_state,
                config={"configurable": {"thread_id": session_id}}
            )
            
            logger.info(f"Workflow completed for session {session_id}")
            return final_state
            
        except Exception as e:
            logger.error(f"Workflow execution failed for session {session_id}: {e}")
            initial_state["error_message"] = str(e)
            initial_state["current_stage"] = "failed"
            return initial_state


# Global workflow instance
research_workflow = ResearchWorkflow()
