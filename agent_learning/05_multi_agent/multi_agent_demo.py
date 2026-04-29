"""Learning-only multi-agent demo for the Expat Germany Agent Lab.

This is intentionally simple and rule-based.

PlannerAgent receives a user query, chooses one specialist agent, and then
the selected specialist runs the right tool.

This does not modify the main Streamlit app, deployment files, or production
RAG chatbot.
"""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint


CURRENT_DIR = Path(__file__).resolve().parent
AGENT_LEARNING_DIR = CURRENT_DIR.parent
SKILLS_DIR = AGENT_LEARNING_DIR / "01_skills"
RAG_AGENT_DIR = AGENT_LEARNING_DIR / "04_agent_with_rag"

sys.path.append(str(SKILLS_DIR))
sys.path.append(str(RAG_AGENT_DIR))

from rag_tool_agent import search_real_rag_docs  # noqa: E402
from skills import (  # noqa: E402
    ask_clarifying_question_mock,
    draft_polite_reply_mock,
    explain_official_text_mock,
    extract_action_items_mock,
    safety_check_mock,
    translate_text_mock,
)


def contains_any(query: str, keywords: tuple[str, ...]) -> bool:
    """Small helper for readable rule-based routing."""
    query_lower = query.lower()
    return any(keyword.lower() in query_lower for keyword in keywords)


def make_final_answer(result: dict) -> str:
    """Create a readable answer from a specialist result dictionary."""
    for key in (
        "answer",
        "translation",
        "draft",
        "explanation",
        "clarifying_question",
    ):
        if result.get(key):
            return str(result[key])

    if result.get("is_high_risk"):
        risks = ", ".join(result.get("risks", []))
        return f"This looks high-risk ({risks}). Please use a qualified professional or current source."

    if result.get("error"):
        return str(result["error"])

    return f"Result: {result}"


class BaseAgent:
    """Base shape for all specialist agents."""

    name = "BaseAgent"
    description = "Base specialist agent."
    keywords: tuple[str, ...] = ()

    def can_handle(self, query: str) -> bool:
        """Return True if this agent is a good fit for the query."""
        return contains_any(query, self.keywords)

    def run(self, query: str) -> dict:
        """Run the specialist agent."""
        raise NotImplementedError


class RAGSpecialistAgent(BaseAgent):
    """Base class for factual specialists that use real RAG."""

    def run(self, query: str) -> dict:
        # RAG is used as a tool here. The specialist does not know FAISS details.
        result = search_real_rag_docs(query)
        return {
            "agent": self.name,
            "tool_used": "search_real_rag_docs",
            "result": result,
            "final_answer": make_final_answer(result),
        }


class VisaAgent(RAGSpecialistAgent):
    name = "VisaAgent"
    description = "Handles visa, Blue Card, and residence permit questions."
    keywords = (
        "blue card",
        "visa",
        "residence permit",
        "settlement permit",
        "opportunity card",
        "job seeker visa",
        "aufenthalt",
        "chancenkarte",
    )


class TaxAgent(RAGSpecialistAgent):
    name = "TaxAgent"
    description = "Handles Tax ID, tax class, Finanzamt, and tax bureaucracy."
    keywords = ("tax", "tax id", "steuer", "steuer-id", "tax class", "finanzamt")


class HousingAgent(RAGSpecialistAgent):
    name = "HousingAgent"
    description = "Handles Anmeldung, renting, landlord, and apartment documents."
    keywords = (
        "anmeldung",
        "rent",
        "renting",
        "landlord",
        "apartment",
        "wohnung",
        "miete",
        "wohnungsgeberbestätigung",
        "documents to rent",
    )


class HealthAgent(RAGSpecialistAgent):
    name = "HealthAgent"
    description = "Handles health insurance and German medical system basics."
    keywords = (
        "health insurance",
        "statutory insurance",
        "private insurance",
        "doctor",
        "krankenversicherung",
        "krankenkasse",
        "arzt",
    )


class FamilyAgent(RAGSpecialistAgent):
    name = "FamilyAgent"
    description = "Handles Kindergeld, Elterngeld, and family support topics."
    keywords = (
        "kindergeld",
        "elterngeld",
        "family reunification",
        "spouse",
        "children",
        "family",
    )


class SchoolKitaAgent(RAGSpecialistAgent):
    name = "SchoolKitaAgent"
    description = "Handles Kita, childcare, kindergarten, and school questions."
    keywords = ("kita", "school", "childcare", "kindergarten", "education")


class TravelLeisureAgent(RAGSpecialistAgent):
    name = "TravelLeisureAgent"
    description = "Handles travel, day trips, hiking, festivals, and places to visit."
    keywords = (
        "day trip",
        "day trips",
        "hiking",
        "festival",
        "must-see",
        "travel",
        "places",
        "oktoberfest",
    )


class JobsAgent(RAGSpecialistAgent):
    name = "JobsAgent"
    description = "Handles jobs, applications, qualifications, and unemployment basics."
    keywords = (
        "job",
        "jobs",
        "application",
        "qualifications",
        "bundesagentur",
        "unemployment",
        "arbeitslos",
        "arbeit",
    )


class CommunicationAgent(BaseAgent):
    name = "CommunicationAgent"
    description = "Handles translation, German replies, official letters, and action items."
    keywords = (
        "translate",
        "übersetze",
        "draft",
        "reply",
        "explain this",
        "official letter",
        "action items",
        "formuliere",
        "brief",
    )

    def run(self, query: str) -> dict:
        query_lower = query.lower()

        if contains_any(query, ("translate", "übersetze")):
            tool_result = translate_text_mock(query, "English")
            tool_used = "translate_text_mock"
        elif contains_any(query, ("draft", "reply", "formuliere")):
            tool_result = draft_polite_reply_mock(query)
            tool_used = "draft_polite_reply_mock"
        elif contains_any(query, ("action items", "todo", "to-do")):
            tool_result = extract_action_items_mock(query)
            tool_used = "extract_action_items_mock"
        elif "explain" in query_lower or "erkläre" in query_lower:
            tool_result = explain_official_text_mock(query, "English")
            tool_used = "explain_official_text_mock"
        else:
            tool_result = ask_clarifying_question_mock(query)
            tool_used = "ask_clarifying_question_mock"

        return {
            "agent": self.name,
            "tool_used": tool_used,
            "result": tool_result,
            "final_answer": make_final_answer(tool_result),
        }


class SafetyAgent(BaseAgent):
    name = "SafetyAgent"
    description = "Handles high-risk, vague, live/current, and out-of-scope requests."
    keywords = (
        "stock",
        "investment",
        "court",
        "legal argument",
        "medical advice",
        "diagnose",
        "weather today",
        "current weather",
        "live",
    )

    def can_handle(self, query: str) -> bool:
        safety_result = safety_check_mock(query)
        is_vague = len(query.split()) <= 4 and not query.strip().endswith("?")
        return safety_result["is_high_risk"] or is_vague or contains_any(query, self.keywords)

    def run(self, query: str) -> dict:
        safety_result = safety_check_mock(query)

        if safety_result["is_high_risk"]:
            tool_used = "safety_check_mock"
            tool_result = safety_result
        else:
            tool_used = "ask_clarifying_question_mock"
            tool_result = ask_clarifying_question_mock(query)

        return {
            "agent": self.name,
            "tool_used": tool_used,
            "result": tool_result,
            "final_answer": make_final_answer(tool_result),
        }


class PlannerAgent:
    """Rule-based planner that chooses one specialist agent."""

    name = "PlannerAgent"

    def __init__(self) -> None:
        self.safety_agent = SafetyAgent()
        self.specialists = [
            VisaAgent(),
            TaxAgent(),
            HousingAgent(),
            HealthAgent(),
            FamilyAgent(),
            SchoolKitaAgent(),
            TravelLeisureAgent(),
            JobsAgent(),
            CommunicationAgent(),
        ]

    def route(self, query: str) -> BaseAgent:
        """Choose the best specialist for the query.

        Safety is checked first because high-risk requests should not be
        accidentally routed into a factual RAG answer.
        """
        if self.safety_agent.can_handle(query):
            return self.safety_agent

        for specialist in self.specialists:
            if specialist.can_handle(query):
                return specialist

        return self.safety_agent

    def run(self, query: str) -> dict:
        """Run the full planner -> specialist flow."""
        selected_agent = self.route(query)
        print(f"Planner selected: {selected_agent.name}")
        return selected_agent.run(query)


if __name__ == "__main__":
    example_queries = [
        "Can I change jobs with an EU Blue Card?",
        "How do I get a German tax ID after Anmeldung?",
        "What documents do I need to rent an apartment in Germany?",
        "How does health insurance work in Germany?",
        "How does Kindergeld work?",
        "How do I find a Kita in Germany?",
        "Suggest day trips in Germany.",
        "How do I find a job in Germany?",
        "Translate this: Ich brauche einen Termin.",
        "Draft a polite German reply saying I will send the documents tomorrow.",
        "Which German stock should I buy this month?",
        "What is the weather in Berlin today?",
        "I need help.",
    ]

    planner = PlannerAgent()

    for user_query in example_queries:
        print("=" * 80)
        print(f"User query: {user_query}")

        try:
            agent_result = planner.run(user_query)
        except Exception as error:
            agent_result = {
                "agent": "Error",
                "tool_used": "none",
                "result": {"error": str(error)},
                "final_answer": f"Demo error: {error}",
            }

        print(f"Planner-selected agent: {agent_result['agent']}")
        print(f"Skill/tool used: {agent_result['tool_used']}")
        print("Result:")
        pprint(agent_result["result"])
        print("Final answer:")
        print(agent_result["final_answer"])
        print()
