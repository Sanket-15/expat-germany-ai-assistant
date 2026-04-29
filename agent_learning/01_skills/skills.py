"""Learning-only mock skills for a future Expat Germany Agent Lab.

Skills are just normal Python functions.
A future agent can inspect the registry, choose a skill, and call it.

These functions do not call Gemini, FAISS, Streamlit, or the main app.
They use simple mock logic so the agent/tool concept is easy to learn.
"""

from __future__ import annotations

from pprint import pprint


def search_docs_mock(query: str) -> dict:
    """Return a mock RAG-style result from saved Germany documents."""
    # Represents a future RAG search tool that would call FAISS.
    return {
        "skill": "search_docs_mock",
        "query": query,
        "answer": "Mock result: found relevant saved Germany documents.",
        "sources": ["tax_id_germany.txt", "anmeldung_registration.txt"],
    }


def translate_text_mock(text: str, target_language: str = "English") -> dict:
    """Return a mock translation result."""
    # Represents a future translation helper.
    return {
        "skill": "translate_text_mock",
        "input_text": text,
        "target_language": target_language,
        "translation": f"Mock translation into {target_language}: {text}",
    }


def draft_polite_reply_mock(message: str, context: str = "") -> dict:
    """Return a polite German reply draft."""
    # Represents a future reply-writing tool for emails or letters.
    return {
        "skill": "draft_polite_reply_mock",
        "message": message,
        "context": context,
        "draft": (
            "Sehr geehrte Damen und Herren,\n\n"
            "vielen Dank für Ihre Nachricht. Ich werde die fehlenden Unterlagen "
            "so bald wie möglich nachreichen.\n\n"
            "Mit freundlichen Grüßen"
        ),
    }


def explain_official_text_mock(text: str, language: str = "English") -> dict:
    """Explain a German official or bureaucratic sentence simply."""
    # Represents a future official-letter explanation tool.
    return {
        "skill": "explain_official_text_mock",
        "text": text,
        "language": language,
        "explanation": (
            f"Mock explanation in {language}: this official text is asking you "
            "to check or provide information."
        ),
    }


def create_first_month_checklist_mock(user_situation: str) -> dict:
    """Create a checklist for someone who recently moved to Germany."""
    # Represents a future planning/checklist skill.
    return {
        "skill": "create_first_month_checklist_mock",
        "user_situation": user_situation,
        "checklist": [
            "Register your address Anmeldung.",
            "Check your Tax ID letter.",
            "Set up health insurance.",
            "Open a bank account if needed.",
            "Save important emergency numbers.",
        ],
    }


def summarize_sources_mock(sources: list[str]) -> dict:
    """Summarize source filenames or URLs."""
    # Represents a future source-summary tool.
    return {
        "skill": "summarize_sources_mock",
        "source_count": len(sources),
        "summary": [f"Source available: {source}" for source in sources],
    }


def classify_intent_mock(user_query: str) -> dict:
    """Classify the user query into a simple intent label."""
    # Represents the first step an agent might take before choosing a tool.
    text = user_query.lower()

    if any(word in text for word in ("hi", "hello", "hallo", "thanks", "danke")):
        intent = "small_talk"
    elif any(word in text for word in ("translate", "übersetze")):
        intent = "translation"
    elif any(word in text for word in ("draft", "reply", "formuliere")):
        intent = "drafting"
    elif any(word in text for word in ("explain", "bedeutet", "erkläre")):
        intent = "explanation"
    elif any(word in text for word in ("checklist", "first month", "erste monat")):
        intent = "checklist"
    elif any(word in text for word in ("court", "stock", "medical", "weather today")):
        intent = "high_risk"
    elif any(word in text for word in ("visa", "tax", "anmeldung", "blue card")):
        intent = "rag_factual"
    else:
        intent = "out_of_scope"

    return {
        "skill": "classify_intent_mock",
        "query": user_query,
        "intent": intent,
    }


def safety_check_mock(user_query: str) -> dict:
    """Detect high-risk topics like legal, financial, medical, or live data."""
    # Represents a future safety gate before tool use.
    text = user_query.lower()
    risks = []

    if any(word in text for word in ("court", "lawsuit", "legal argument", "gericht")):
        risks.append("legal_court_advice")
    if any(word in text for word in ("stock", "investment", "buy this month", "aktie")):
        risks.append("financial_advice")
    if any(word in text for word in ("diagnose", "medicine", "symptom", "medical")):
        risks.append("medical_advice")
    if any(word in text for word in ("today", "current", "live", "aktuell")):
        risks.append("live_or_current_information")

    return {
        "skill": "safety_check_mock",
        "query": user_query,
        "is_high_risk": bool(risks),
        "risks": risks,
    }


def format_answer_with_sources_mock(answer: str, sources: list[str]) -> dict:
    """Format an answer with source filenames or URLs."""
    # Represents a future answer-formatting skill.
    source_lines = "\n".join(f"- {source}" for source in sources)
    formatted_answer = f"{answer}\n\nSources:\n{source_lines}" if sources else answer

    return {
        "skill": "format_answer_with_sources_mock",
        "formatted_answer": formatted_answer,
        "source_count": len(sources),
    }


def extract_action_items_mock(text: str) -> dict:
    """Extract action items from a German letter or official message."""
    # Represents a future task extraction skill.
    return {
        "skill": "extract_action_items_mock",
        "text": text,
        "action_items": [
            "Check the deadline.",
            "Prepare missing documents.",
            "Reply politely if clarification is needed.",
        ],
    }


def recommend_next_skill_mock(intent: str) -> dict:
    """Recommend which skill should be used next for an intent."""
    # Represents a future agent's tool-selection step.
    recommendations = {
        "rag_factual": "search_docs_mock",
        "translation": "translate_text_mock",
        "drafting": "draft_polite_reply_mock",
        "explanation": "explain_official_text_mock",
        "checklist": "create_first_month_checklist_mock",
        "high_risk": "safety_check_mock",
        "out_of_scope": "ask_clarifying_question_mock",
        "small_talk": "ask_clarifying_question_mock",
    }

    return {
        "skill": "recommend_next_skill_mock",
        "intent": intent,
        "recommended_skill": recommendations.get(intent, "ask_clarifying_question_mock"),
    }


def create_learning_summary_mock(topic: str) -> dict:
    """Explain a concept such as RAG, agents, tools, or MCP simply."""
    # Represents a future teaching/learning skill.
    summaries = {
        "rag": "RAG means retrieving relevant documents before generating an answer.",
        "agents": "An agent is a decision-maker that chooses which tool or skill to use.",
        "tools": "Tools are callable functions that do specific jobs.",
        "mcp": "MCP is a protocol that can expose tools and data sources to AI systems.",
    }

    return {
        "skill": "create_learning_summary_mock",
        "topic": topic,
        "summary": summaries.get(topic.lower(), "Mock summary: this is a learning topic."),
    }


def ask_clarifying_question_mock(user_query: str) -> dict:
    """Return a clarifying question when the user request is too vague."""
    # Represents a future fallback when the agent needs more information.
    return {
        "skill": "ask_clarifying_question_mock",
        "query": user_query,
        "clarifying_question": (
            "Could you share a bit more detail about what you want to do in Germany?"
        ),
    }


# The registry is a menu of tools a future agent can inspect and choose from.
SKILL_REGISTRY = {
    "search_docs_mock": {
        "function": search_docs_mock,
        "description": "Search saved Germany-related documents.",
        "intent": "rag_factual",
        "args": ["query"],
        "example": "How do I get a tax ID in Germany?",
    },
    "translate_text_mock": {
        "function": translate_text_mock,
        "description": "Translate user-provided text.",
        "intent": "translation",
        "args": ["text", "target_language"],
        "example": 'Translate this into English: "Bitte reichen Sie die Unterlagen ein."',
    },
    "draft_polite_reply_mock": {
        "function": draft_polite_reply_mock,
        "description": "Draft a polite German reply.",
        "intent": "drafting",
        "args": ["message", "context"],
        "example": "Draft a German reply to my landlord.",
    },
    "explain_official_text_mock": {
        "function": explain_official_text_mock,
        "description": "Explain official German text in simple language.",
        "intent": "explanation",
        "args": ["text", "language"],
        "example": "Explain this letter in English.",
    },
    "create_first_month_checklist_mock": {
        "function": create_first_month_checklist_mock,
        "description": "Create a first-month checklist after moving to Germany.",
        "intent": "checklist",
        "args": ["user_situation"],
        "example": "I just moved to Berlin. What should I do first?",
    },
    "summarize_sources_mock": {
        "function": summarize_sources_mock,
        "description": "Summarize source filenames or URLs.",
        "intent": "source_summary",
        "args": ["sources"],
        "example": "Summarize these sources.",
    },
    "classify_intent_mock": {
        "function": classify_intent_mock,
        "description": "Classify a user query into a simple intent.",
        "intent": "intent_classification",
        "args": ["user_query"],
        "example": "How do I apply for a Blue Card?",
    },
    "safety_check_mock": {
        "function": safety_check_mock,
        "description": "Detect high-risk legal, financial, medical, or live-data requests.",
        "intent": "safety",
        "args": ["user_query"],
        "example": "Which stock should I buy this month?",
    },
    "format_answer_with_sources_mock": {
        "function": format_answer_with_sources_mock,
        "description": "Format an answer with sources.",
        "intent": "formatting",
        "args": ["answer", "sources"],
        "example": "Format this answer with two sources.",
    },
    "extract_action_items_mock": {
        "function": extract_action_items_mock,
        "description": "Extract action items from a letter or message.",
        "intent": "action_items",
        "args": ["text"],
        "example": "What do I need to do from this letter?",
    },
    "recommend_next_skill_mock": {
        "function": recommend_next_skill_mock,
        "description": "Recommend the next skill for a detected intent.",
        "intent": "tool_selection",
        "args": ["intent"],
        "example": "Intent is translation. Which skill should run?",
    },
    "create_learning_summary_mock": {
        "function": create_learning_summary_mock,
        "description": "Explain learning concepts like RAG, agents, tools, or MCP.",
        "intent": "learning",
        "args": ["topic"],
        "example": "Explain RAG simply.",
    },
    "ask_clarifying_question_mock": {
        "function": ask_clarifying_question_mock,
        "description": "Ask a clarifying question for vague requests.",
        "intent": "clarification",
        "args": ["user_query"],
        "example": "I need help in Germany.",
    },
}


def list_available_skills() -> dict:
    """Return all skill names and descriptions without running any skills."""
    return {
        name: details["description"]
        for name, details in SKILL_REGISTRY.items()
    }


if __name__ == "__main__":
    print("Available skills:")
    pprint(list_available_skills())

    print("\nDemo: calling each skill once\n")

    demo_calls = [
        search_docs_mock("How do I get a tax ID in Germany?"),
        translate_text_mock("Bitte reichen Sie die Unterlagen ein.", "English"),
        draft_polite_reply_mock("I will send the missing documents tomorrow."),
        explain_official_text_mock("Ihr Antrag wurde abgelehnt.", "English"),
        create_first_month_checklist_mock("I just moved to Germany."),
        summarize_sources_mock(["tax_id_germany.txt", "anmeldung_registration.txt"]),
        classify_intent_mock("How do I apply for a Blue Card?"),
        safety_check_mock("Which German stock should I buy this month?"),
        format_answer_with_sources_mock("Mock answer.", ["source_one.txt"]),
        extract_action_items_mock("Bitte reichen Sie die Unterlagen bis Freitag ein."),
        recommend_next_skill_mock("translation"),
        create_learning_summary_mock("RAG"),
        ask_clarifying_question_mock("I need help."),
    ]

    for result in demo_calls:
        pprint(result)
        print("-" * 60)

    print("\nThe registry works like a menu of callable tools for a future agent.")
