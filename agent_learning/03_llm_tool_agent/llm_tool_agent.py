"""Learning-only Gemini tool-using agent demo.

This script shows the next step after the rule-based agent:

1. We describe available Python skills as Gemini tools.
2. Gemini decides whether it wants to call a tool.
3. Python executes the selected skill.
4. The tool result is sent back to Gemini.
5. Gemini writes the final answer.

This does not change the main Streamlit app or production RAG chatbot.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from pprint import pprint

from dotenv import load_dotenv
from google import genai
from google.genai import types


# Allow this learning script to import skills.py from the previous folder.
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parents[1]
SKILLS_DIR = CURRENT_DIR.parent / "01_skills"
sys.path.append(str(SKILLS_DIR))

from skills import (  # noqa: E402
    ask_clarifying_question_mock,
    draft_polite_reply_mock,
    explain_official_text_mock,
    safety_check_mock,
    search_docs_mock,
    translate_text_mock,
)


MODEL_NAME = "gemini-2.5-flash-lite"


# This dictionary maps Gemini tool names to real Python functions.
# Gemini chooses the name; Python does the actual execution.
AVAILABLE_TOOLS = {
    "search_docs_mock": search_docs_mock,
    "translate_text_mock": translate_text_mock,
    "draft_polite_reply_mock": draft_polite_reply_mock,
    "explain_official_text_mock": explain_official_text_mock,
    "safety_check_mock": safety_check_mock,
    "ask_clarifying_question_mock": ask_clarifying_question_mock,
}


def get_client() -> genai.Client:
    """Create a Gemini client from .env or environment variables."""
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "Missing GEMINI_API_KEY. Add it to .env or set it as an environment variable."
        )

    return genai.Client(api_key=api_key)


def build_tool_declarations() -> list[types.Tool]:
    """Declare Python skills as tools Gemini can choose from.

    A tool declaration is a schema: it tells the LLM the tool name, what the
    tool does, and which arguments the tool expects.
    """
    return [
        types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name="search_docs_mock",
                    description="Search saved Germany-related documents.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The factual Germany question to search for.",
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
                            "text": {
                                "type": "string",
                                "description": "The text to translate.",
                            },
                            "target_language": {
                                "type": "string",
                                "description": "The language to translate into.",
                            },
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
                            "message": {
                                "type": "string",
                                "description": "What the reply should say.",
                            },
                            "context": {
                                "type": "string",
                                "description": "Optional extra context for the reply.",
                            },
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
                            "text": {
                                "type": "string",
                                "description": "The official text to explain.",
                            },
                            "language": {
                                "type": "string",
                                "description": "The language for the explanation.",
                            },
                        },
                        "required": ["text"],
                    },
                ),
                types.FunctionDeclaration(
                    name="safety_check_mock",
                    description="Check for high-risk legal, financial, medical, or live-data requests.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "user_query": {
                                "type": "string",
                                "description": "The user query to safety-check.",
                            }
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
                            "user_query": {
                                "type": "string",
                                "description": "The vague user query.",
                            }
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

    parts = response.candidates[0].content.parts or []
    for part in parts:
        if getattr(part, "function_call", None):
            return part.function_call

    return None


def run_tool(function_call) -> dict:
    """Execute the Python skill selected by Gemini."""
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

    tool_function = AVAILABLE_TOOLS[tool_name]
    return tool_function(**tool_args)


def run_agent_turn(client: genai.Client, user_query: str) -> None:
    """Run one LLM tool-agent turn."""
    print("=" * 80)
    print(f"User query: {user_query}")

    system_instruction = (
        "You are a learning-only tool-using agent for an Expat Germany assistant. "
        "Choose exactly one tool when a tool would help. "
        "Use search_docs_mock for factual Germany document questions. "
        "Use translate_text_mock for translation. "
        "Use draft_polite_reply_mock for reply drafting. "
        "Use explain_official_text_mock for explaining official text. "
        "Use safety_check_mock for legal, financial, medical, or live/current-data risk. "
        "Use ask_clarifying_question_mock when the request is vague. "
        "After receiving a tool result, write a short final answer."
    )

    user_content = types.Content(
        role="user",
        parts=[types.Part(text=user_query)],
    )

    # Gemini sees the tool declarations and decides if one should be called.
    first_response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[user_content],
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=build_tool_declarations(),
        ),
    )

    function_call = get_first_function_call(first_response)

    if function_call is None:
        print("Gemini did not request a tool call.")
        print("Direct answer:")
        print(first_response.text or "(No direct text returned.)")
        return

    # Python executes the selected skill locally.
    tool_result = run_tool(function_call)
    print("Tool result:")
    pprint(tool_result)

    # The tool result is returned to Gemini so it can produce a final answer.
    tool_response_part = types.Part.from_function_response(
        name=function_call.name,
        response={"result": tool_result},
    )

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

    print("Final answer:")
    print(final_response.text or "(No final text returned.)")


if __name__ == "__main__":
    example_queries = [
        "How do I get a tax ID in Germany?",
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
