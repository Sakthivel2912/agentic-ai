from app.services.adaptive_router import route_research_question
from app.workflows.research_workflow import research_workflow
import pytest


def test_simple_definition_selects_only_research_agent():
    decision = route_research_question("What is RAG?")

    assert decision["selected_agents"] == ["research_agent"]
    assert decision["estimated_complexity"] == "low"


def test_technical_comparison_selects_relevant_specialists():
    decision = route_research_question(
        "Compare LangGraph and CrewAI for production agent orchestration"
    )

    assert decision["selected_agents"] == [
        "research_agent",
        "technical_agent",
        "data_agent",
    ]
    assert decision["estimated_research_depth"] == "deep"


def test_category_can_select_a_specialist():
    decision = route_research_question("What should we investigate?", "security")

    assert "security_agent" in decision["selected_agents"]
    assert decision["reason_for_selection"]["security_agent"]


@pytest.mark.asyncio
async def test_router_node_records_selection_in_workflow_state():
    state = {
        "session_id": "session-test",
        "question": "Compare two production orchestration frameworks",
        "category": "general",
        "selected_agents": [],
        "current_stage": "initializing",
        "progress": 0.0,
        "metadata": {},
    }

    result = await research_workflow._adaptive_router_node(state)

    assert "technical_agent" in result["selected_agents"]
    assert result["metadata"]["adaptive_router"]["selected_agents"] == result["selected_agents"]
    assert result["current_stage"] == "adaptive_routing"


@pytest.mark.asyncio
async def test_graph_skips_unselected_specialists(monkeypatch):
    executed_agents = []

    async def research_execute(**kwargs):
        executed_agents.append("research_agent")
        return {"status": "completed", "raw_output": "Research summary", "sources": []}

    async def reviewer_execute(**kwargs):
        executed_agents.append("reviewer_agent")
        return {"status": "completed", "raw_output": "Review summary"}

    async def synthesizer_execute(**kwargs):
        executed_agents.append("synthesizer_agent")
        return {"status": "completed", "raw_output": "Final response"}

    monkeypatch.setattr(research_workflow.research_agent, "execute", research_execute)
    monkeypatch.setattr(research_workflow.reviewer_agent, "execute", reviewer_execute)
    monkeypatch.setattr(research_workflow.synthesizer_agent, "execute", synthesizer_execute)

    result = await research_workflow.execute_workflow(
        session_id="adaptive-router-graph-test",
        user_id="test-user",
        question="What is RAG?",
        title="RAG definition",
        category="general",
        selected_agents=[],
        enable_rag=False,
        enable_review=True,
        enable_citations=True,
        selected_document_ids=[],
    )

    assert executed_agents == ["research_agent", "reviewer_agent", "synthesizer_agent"]
    assert result["selected_agents"] == ["research_agent"]
    assert result["final_answer"] == "Final response"