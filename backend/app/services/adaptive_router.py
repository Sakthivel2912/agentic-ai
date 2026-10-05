"""Heuristic agent selection for research sessions without manual agent choices."""
import re
from typing import Any, Dict, List


SPECIALIST_RULES = {
    "technical_agent": {
        "terms": ("architecture", "implementation", "production", "orchestration", "framework", "technical", "integration", "deployment"),
        "categories": {"software_architecture", "technology"},
        "reason": "The question asks for technical design, implementation, or production trade-offs.",
    },
    "data_agent": {
        "terms": ("compare", "comparison", "benchmark", "measure", "statistics", "dataset", "evidence", "evaluate"),
        "categories": {"data_analysis"},
        "reason": "The question calls for comparison, evaluation, or analysis of evidence and measurements.",
    },
    "cost_agent": {
        "terms": ("cost", "pricing", "price", "budget", "infrastructure", "total cost", "expensive", "compute"),
        "categories": {"business_strategy"},
        "reason": "The question involves cost, pricing, budgets, or infrastructure trade-offs.",
    },
    "product_agent": {
        "terms": ("business", "market", "customer", "product", "strategy", "adoption", "revenue", "market share"),
        "categories": {"business_strategy", "product_research", "market_research"},
        "reason": "The question concerns product, customer, business, or market decisions.",
    },
    "security_agent": {
        "terms": ("security", "privacy", "threat", "risk", "compliance", "vulnerability", "attack", "safety"),
        "categories": {"security"},
        "reason": "The question raises security, privacy, safety, or compliance concerns.",
    },
}


def route_research_question(question: str, category: str = "general") -> Dict[str, Any]:
    """Select only the specialists supported by explicit question/category cues."""
    normalized_question = question.casefold()
    normalized_category = category.casefold()
    selected_agents: List[str] = ["research_agent"]
    reasons = {"research_agent": "Baseline agent for gathering and organizing research."}

    for agent_id, rule in SPECIALIST_RULES.items():
        if normalized_category in rule["categories"] or any(
            re.search(rf"(?<!\w){re.escape(term)}(?!\w)", normalized_question)
            for term in rule["terms"]
        ):
            selected_agents.append(agent_id)
            reasons[agent_id] = rule["reason"]

    specialist_count = len(selected_agents) - 1
    if specialist_count == 0:
        complexity, depth = "low", "basic"
    elif specialist_count == 1:
        complexity, depth = "moderate", "standard"
    else:
        complexity, depth = "high", "deep"

    return {
        "selected_agents": selected_agents,
        "reason_for_selection": reasons,
        "estimated_complexity": complexity,
        "estimated_research_depth": depth,
    }