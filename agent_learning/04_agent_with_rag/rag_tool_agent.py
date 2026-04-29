"""Learning-only agent where real RAG is exposed as a Gemini tool.

This demo keeps the main app unchanged. It wraps the existing project RAG
chatbot as one callable tool, then lets Gemini choose between that real RAG
tool and several mock non-RAG tools.

Difference from the original RAG chatbot:
- Original chatbot always routes internally and answers.
- This demo lets Gemini choose whether to call RAG or a different tool.

Difference from 03_llm_tool_agent:
- 03 used only mock tools.
- This version uses the real project RAG pipeline as one tool.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from pprint import pprint

from dotenv import load_dotenv
from google import genai
from google.genai import types


CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parents[1]
SKILLS_DIR = CURRENT_DIR.parent / "01_skills"
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(SKILLS_DIR))

from app import answer_user_input  # noqa: E402
from rag import CHUNKS_PATH, INDEX_PATH  # noqa: E402
from skills import (  # noqa: E402
    ask_clarifying_question_mock,
    draft_polite_reply_mock,
    explain_official_text_mock,
    safety_check_mock,
    translate_text_mock,
)


MODEL_NAME = "gemini-2.5-flash-lite"


def get_client() -> genai.Client:
    """Create a Gemini client from .env or environment variables."""
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "Missing GEMINI_API_KEY. Add it to .env or set it as an environment variable."
        )

    return genai.Client(api_key=api_key)


def split_answer_and_sources(answer: str) -> tuple[str, list[str]]:
    """Split app-style answers into main answer and source lines."""
    for marker in ("\n\nSources:\n", "\n\nQuellen:\n"):
        if marker in answer:
            main_answer, source_text = answer.split(marker, 1)
            sources = [
                line.removeprefix("- ").strip()
                for line in source_text.splitlines()
                if line.strip()
            ]
            return main_answer, sources

    return answer, []


def search_real_rag_docs(query: str) -> dict:
    """Search the existing FAISS/vectorstore through the project RAG pipeline."""
    # RAG is now a tool. A future agent can call it only when needed.
    if not INDEX_PATH.exists() or not CHUNKS_PATH.exists():
        return {
            "skill": "search_real_rag_docs",
            "query": query,
            "error": (
                "Vectorstore files are missing. Run python ingest.py from the "
                "project root to create vectorstore/faiss.index and "
                "vectorstore/chunks.json."
            ),
            "sources": [],
        }

    try:
        client = get_client()
        answer = answer_user_input(client, query)
        main_answer, sources = split_answer_and_sources(answer)
        return {
            "skill": "search_real_rag_docs",
            "query": query,
            "answer": main_answer,
            "sources": sources,
            "source_count": len(sources),
        }
    except Exception as error:
        return {
            "skill": "search_real_rag_docs",
            "query": query,
            "error": str(error),
            "sources": [],
        }


AVAILABLE_TOOLS = {
    "search_real_rag_docs": search_real_rag_docs,
    "translate_text_mock": translate_text_mock,
    "draft_polite_reply_mock": draft_polite_reply_mock,
    "explain_official_text_mock": explain_official_text_mock,
    "safety_check_mock": safety_check_mock,
    "ask_clarifying_question_mock": ask_clarifying_question_mock,
}


def build_tool_declarations() -> list[types.Tool]:
    """Declare the real RAG tool and mock tools to Gemini."""
    return [
        types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name="search_real_rag_docs",
                    description="Search the real saved Germany documents using the existing FAISS RAG pipeline.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The factual Germany question to answer with RAG.",
                            }
                        },
                        "required": ["query"],
                    },
                ),
                types.FunctionDeclaration(
                    name="translate_text_mock",
                    description="Translate user-provided text.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "target_language": {"type": "string"},
                        },
                        "required": ["text"],
                    },
                ),
                types.FunctionDeclaration(
                    name="draft_polite_reply_mock",
                    description="Draft a polite German reply.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "message": {"type": "string"},
                            "context": {"type": "string"},
                        },
                        "required": ["message"],
                    },
                ),
                types.FunctionDeclaration(
                    name="explain_official_text_mock",
                    description="Explain German official or bureaucratic text simply.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "language": {"type": "string"},
                        },
                        "required": ["text"],
                    },
                ),
                types.FunctionDeclaration(
                    name="safety_check_mock",
                    description="Check for legal, financial, medical, or live/current-data risk.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "user_query": {"type": "string"},
                        },
                        "required": ["user_query"],
                    },
                ),
                types.FunctionDeclaration(
                    name="ask_clarifying_question_mock",
                    description="Ask a clarifying question for vague requests.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "user_query": {"type": "string"},
                        },
                        "required": ["user_query"],
                    },
                ),
            ]
        )
    ]


def get_first_function_call(response):
    """Return the first Gemini function call, if one exists."""
    if not response.candidates:
        return None

    for part in response.candidates[0].content.parts or []:
        if getattr(part, "function_call", None):
            return part.function_call

    return None


def run_tool(function_call) -> dict:
    """Execute whichever tool Gemini selected."""
    tool_name = function_call.name
    tool_args = dict(function_call.args or {})

    print(f"Selected tool: {tool_name}")
    print("Tool arguments:")
    pprint(tool_args)

    if tool_name not in AVAILABLE_TOOLS:
        return {
            "error": f"Unknown tool requested: {tool_name}",
            "available_tools": list(AVAILABLE_TOOLS),
        }

    try:
        return AVAILABLE_TOOLS[tool_name](**tool_args)
    except Exception as error:
        return {"error": str(error), "tool": tool_name}


def build_fallback_final_answer(tool_result: dict) -> str:
    """Create a readable final answer if Gemini returns no final text.

    Some learning demos can produce a valid tool result but an empty second
    Gemini response. This fallback keeps the terminal demo useful and clear.
    """
    for key in (
        "answer",
        "translation",
        "draft",
        "explanation",
        "clarifying_question",
    ):
        if tool_result.get(key):
            return str(tool_result[key])

    return f"Tool completed with this result:\n{tool_result}"


def run_agent_turn(client: genai.Client, user_query: str) -> None:
    """Run one agent turn where Gemini chooses between RAG and non-RAG tools."""
    print("=" * 80)
    print(f"User query: {user_query}")

    system_instruction = (
        "You are a learning-only tool-using agent for an Expat Germany assistant. "
        "Choose exactly one tool when a tool would help. "
        "Use search_real_rag_docs for factual Germany questions about visas, tax ID, Anmeldung, housing, health insurance, jobs, and bureaucracy. "
        "Use translate_text_mock for translation. "
        "Use draft_polite_reply_mock for reply drafting. "
        "Use explain_official_text_mock for explaining official German text. "
        "Use safety_check_mock for legal, financial, medical, or live/current-data risk. "
        "Use ask_clarifying_question_mock when the request is vague. "
        "After receiving a tool result, write a short final answer."
    )

    user_content = types.Content(
        role="user",
        parts=[types.Part(text=user_query)],
    )

    try:
        first_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[user_content],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=build_tool_declarations(),
            ),
        )
    except Exception as error:
        print(f"Gemini request failed: {error}")
        return

    function_call = get_first_function_call(first_response)

    if function_call is None:
        print("Gemini did not request a tool call.")
        print("Direct answer:")
        print(first_response.text or "(No direct text returned.)")
        return

    tool_result = run_tool(function_call)
    print("Tool result:")
    pprint(tool_result)

    tool_response_part = types.Part.from_function_response(
        name=function_call.name,
        response={"result": tool_result},
    )

    try:
        final_response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                user_content,
                first_response.candidates[0].content,
                types.Content(role="tool", parts=[tool_response_part]),
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=build_tool_declarations(),
            ),
        )
    except Exception as error:
        print(f"Final Gemini response failed: {error}")
        return

    print("Final answer:")
    print(final_response.text or build_fallback_final_answer(tool_result))


if __name__ == "__main__":
    example_queries = [
        "How do I get a German tax ID after Anmeldung?",
        "Can I change jobs with an EU Blue Card?",
        "Translate this: Ich brauche einen Termin.",
        "Draft a polite reply saying I will send the documents tomorrow.",
        "Explain this in English: Ihr Antrag wurde abgelehnt, weil Unterlagen fehlen.",
        "Which German stock should I buy this month?",
        "I need help.",
    ]

    try:
        gemini_client = get_client()
    except ValueError as error:
        print(error)
        raise SystemExit(1)

    for query in example_queries:
        try:
            run_agent_turn(gemini_client, query)
        except Exception as error:
            print("=" * 80)
            print(f"Example failed but the demo will continue: {query}")
            print(f"Error: {error}")
