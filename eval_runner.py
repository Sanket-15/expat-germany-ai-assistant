import csv
import os
import re
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from app import (
    INSUFFICIENT_MESSAGE,
    INSUFFICIENT_MESSAGE_DE,
    answer_user_input,
    get_detected_intent,
    get_response_language,
)


EVALUATION_FILE = Path("evaluation_questions.md")
RESULTS_DIR = Path("eval_results")
RESULTS_FILE = RESULTS_DIR / "eval_results.csv"


FALLBACK_QUESTIONS = [
    "How do I apply for an EU Blue Card in Germany?",
    "Kann ich mit der Blue Card den Job wechseln?",
    "What are the basic requirements for a settlement permit in Germany?",
    "Wie mache ich die Anmeldung in Deutschland?",
    "How do I get a German tax ID after Anmeldung?",
    "What is the radio tax or Rundfunkbeitrag in Germany?",
    "What documents do I usually need to rent an apartment in Germany?",
    "How does health insurance work in Germany?",
    "Wie funktioniert Kindergeld in Deutschland?",
    'Translate this into English: "Bitte reichen Sie die fehlenden Unterlagen bis zum 15. Mai ein."',
    "Draft a polite German reply to my landlord saying I will send the missing documents tomorrow.",
    'Explain this in English: "Ihr Antrag wurde abgelehnt, weil Unterlagen fehlen."',
    "What is the weather in Berlin today?",
    "I was denied a visa. What exact legal argument should I use in court?",
    "Which German stock should I buy this month?",
]


def load_questions():
    if not EVALUATION_FILE.exists():
        return FALLBACK_QUESTIONS

    text = EVALUATION_FILE.read_text(encoding="utf-8")
    questions = re.findall(r"- \*\*Question:\*\* (.+)", text)

    return questions or FALLBACK_QUESTIONS


def split_answer_and_sources(answer):
    source_markers = ["\n\nSources:\n", "\n\nQuellen:\n"]
    marker = next((item for item in source_markers if item in answer), None)

    if marker is None:
        return answer, []

    main_answer, source_text = answer.split(marker, 1)
    sources = [
        line.removeprefix("- ").strip()
        for line in source_text.splitlines()
        if line.strip()
    ]

    return main_answer, sources


def says_not_enough_context(answer):
    return (
        INSUFFICIENT_MESSAGE in answer
        or INSUFFICIENT_MESSAGE_DE in answer
        or "not enough information" in answer.lower()
        or "nicht gen\u00fcgend informationen" in answer.lower()
    )


def language_check_notes(question, answer):
    expected_language = get_response_language(question)

    if expected_language == "German":
        german_markers = (" der ", " die ", " das ", " ich ", " sie ", " ist ", " kann ", "quellen")
        answer_lower = f" {answer.lower()} "
        if any(char in answer_lower for char in ("ä", "ö", "ü", "ß")) or any(
            marker in answer_lower for marker in german_markers
        ):
            return "Expected German; answer appears German."
        return "Expected German; check manually."

    if "Quellen:" in answer:
        return "Expected English; answer contains German source heading."

    return "Expected English; answer appears acceptable."


def create_client():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY. Add it to your .env file first.")

    return genai.Client(api_key=api_key)


def run_evaluation():
    client = create_client()
    questions = load_questions()
    timestamp = datetime.now().isoformat(timespec="seconds")
    rows = []

    for number, question in enumerate(questions, start=1):
        print(f"Evaluating {number}/{len(questions)}: {question}")

        try:
            answer = answer_user_input(client, question)
        except Exception as error:
            answer = f"Error: {error}"

        main_answer, sources = split_answer_and_sources(answer)
        detected_intent = get_detected_intent(question)
        expected_sources_required = detected_intent == "rag_factual"
        has_answer = bool(main_answer.strip())
        has_sources = bool(sources)
        answer_length = len(main_answer)
        possible_hallucination_risk = (
            answer_length > 300 and not has_sources and expected_sources_required
        )

        rows.append(
            {
                "timestamp": timestamp,
                "question": question,
                "answer": answer,
                "retrieved_sources": " | ".join(sources),
                "sources_shown": has_sources,
                "source_count": len(sources),
                "answer_length": answer_length,
                "detected_or_expected_intent": detected_intent,
                "expected_sources_required": expected_sources_required,
                "has_answer": has_answer,
                "has_sources": has_sources,
                "says_not_enough_context": says_not_enough_context(answer),
                "possible_hallucination_risk": possible_hallucination_risk,
                "language_check_notes": language_check_notes(question, answer),
            }
        )

    RESULTS_DIR.mkdir(exist_ok=True)

    with RESULTS_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp",
                "question",
                "answer",
                "retrieved_sources",
                "sources_shown",
                "source_count",
                "answer_length",
                "detected_or_expected_intent",
                "expected_sources_required",
                "has_answer",
                "has_sources",
                "says_not_enough_context",
                "possible_hallucination_risk",
                "language_check_notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved evaluation results to {RESULTS_FILE}")


if __name__ == "__main__":
    run_evaluation()
