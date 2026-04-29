"""Learning-only single-agent demo.

This file shows the simplest possible agent loop:

1. Receive a user query.
2. Classify the intent.
3. Choose a skill.
4. Call the skill.
5. Return a final answer.

It does not call Gemini, FAISS, Streamlit, or the production chatbot.
"""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint


# Allow this learning script to import skills.py from the previous folder.
CURRENT_DIR = Path(__file__).resolve().parent
SKILLS_DIR = CURRENT_DIR.parent / "01_skills"
sys.path.append(str(SKILLS_DIR))

from skills import (  # noqa: E402
    SKILL_REGISTRY,
    classify_intent_mock,
    recommend_next_skill_mock,
)


def build_skill_arguments(skill_name: str, user_query: str) -> dict:
    """Create simple arguments for the selected skill.

    A real agent would reason more deeply here. For learning, we use small
    if/elif rules so the flow is easy to understand.
    """
    if skill_name == "search_docs_mock":
        return {"query": user_query}

    if skill_name == "translate_text_mock":
        return {"text": user_query, "target_language": "English"}

    if skill_name == "draft_polite_reply_mock":
        return {"message": user_query}

    if skill_name == "explain_official_text_mock":
        return {"text": user_query, "language": "English"}

    if skill_name == "create_first_month_checklist_mock":
        return {"user_situation": user_query}

    if skill_name == "safety_check_mock":
        return {"user_query": user_query}

    if skill_name == "ask_clarifying_question_mock":
        return {"user_query": user_query}

    return {"user_query": user_query}


def create_final_answer(skill_name: str, skill_result: dict) -> str:
    """Turn a skill result dictionary into a simple final answer."""
    if skill_name == "search_docs_mock":
        return skill_result["answer"]

    if skill_name == "translate_text_mock":
        return skill_result["translation"]

    if skill_name == "draft_polite_reply_mock":
        return skill_result["draft"]

    if skill_name == "explain_official_text_mock":
        return skill_result["explanation"]

    if skill_name == "create_first_month_checklist_mock":
        return "\n".join(f"- {item}" for item in skill_result["checklist"])

    if skill_name == "safety_check_mock":
        if skill_result["is_high_risk"]:
            return "This looks high-risk. I would avoid giving direct advice and ask for a safer next step."
        return "No obvious high-risk topic detected."

    if skill_name == "ask_clarifying_question_mock":
        return skill_result["clarifying_question"]

    return "Skill completed."


def run_agent(user_query: str) -> dict:
    """Run one simple agent turn."""
    # Step 1: classify what the user wants.
    intent_result = classify_intent_mock(user_query)
    detected_intent = intent_result["intent"]

    # Step 2: ask the registry helper which skill should handle this intent.
    recommendation = recommend_next_skill_mock(detected_intent)
    selected_skill_name = recommendation["recommended_skill"]

    # Step 3: look up the actual callable function from SKILL_REGISTRY.
    selected_skill = SKILL_REGISTRY[selected_skill_name]["function"]

    # Step 4: build arguments and execute the selected skill.
    skill_arguments = build_skill_arguments(selected_skill_name, user_query)
    skill_result = selected_skill(**skill_arguments)

    # Step 5: create a final user-facing answer.
    final_answer = create_final_answer(selected_skill_name, skill_result)

    return {
        "user_query": user_query,
        "detected_intent": detected_intent,
        "selected_skill": selected_skill_name,
        "skill_result": skill_result,
        "final_answer": final_answer,
    }


if __name__ == "__main__":
    example_queries = [
        "How do I get a tax ID in Germany?",
        "Translate this: Ich brauche einen Termin.",
        "Draft a polite reply saying I will send the documents tomorrow.",
        "Which German stock should I buy this month?",
        "I need help.",
    ]

    for query in example_queries:
        print("=" * 70)
        result = run_agent(query)
        print(f"User query: {result['user_query']}")
        print(f"Detected intent: {result['detected_intent']}")
        print(f"Selected skill: {result['selected_skill']}")
        print("\nSkill result:")
        pprint(result["skill_result"])
        print("\nFinal answer:")
        print(result["final_answer"])
        print()
