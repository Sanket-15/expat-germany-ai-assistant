"""Learning-only rule-based agent that uses MCP-exposed tools.

This demo does not start a separate MCP subprocess. To keep learning simple,
it imports the helper functions from the MCP-style server in 06_mcp_server.

The important idea is still the same:
- the agent discovers tools from the MCP server shape
- the agent chooses one MCP tool
- the agent calls the MCP tool through the server helper
- the agent turns the tool result into a final answer
"""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint


CURRENT_DIR = Path(__file__).resolve().parent
MCP_SERVER_DIR = CURRENT_DIR.parent / "06_mcp_server"
sys.path.append(str(MCP_SERVER_DIR))

from server import call_tool, tool_definitions  # noqa: E402


def contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    """Return True if any keyword appears in the text."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)


def list_mcp_tool_names() -> list[str]:
    """Discover available MCP tools from the server's tool definitions."""
    return [tool["name"] for tool in tool_definitions()]


def choose_mcp_tool(user_query: str) -> str:
    """Choose a tool with simple rule-based routing."""
    if contains_any(user_query, ("translate", "übersetze")):
        return "translate_text_mock"

    if contains_any(user_query, ("draft", "reply", "polite reply", "formuliere")):
        return "draft_polite_reply_mock"

    if contains_any(
        user_query,
        (
            "stock",
            "investment",
            "court",
            "legal argument",
            "medical",
            "diagnose",
            "weather",
            "today",
            "weather today",
            "current weather",
            "live",
        ),
    ):
        return "safety_check_mock"

    return "search_docs_mock"


def build_tool_arguments(tool_name: str, user_query: str) -> dict:
    """Build simple arguments for the selected MCP tool."""
    if tool_name == "search_docs_mock":
        return {"query": user_query}

    if tool_name == "translate_text_mock":
        return {
            "text": user_query,
            "target_language": "English",
        }

    if tool_name == "draft_polite_reply_mock":
        return {
            "message": user_query,
            "context": "",
        }

    if tool_name == "safety_check_mock":
        return {"user_query": user_query}

    return {"user_query": user_query}


def create_final_answer(tool_result: dict) -> str:
    """Create a simple final answer from an MCP tool result."""
    for key in ("answer", "translation", "draft", "clarifying_question"):
        if tool_result.get(key):
            return str(tool_result[key])

    if tool_result.get("is_high_risk"):
        risks = ", ".join(tool_result.get("risks", []))
        return f"This looks high-risk ({risks}). Please avoid direct advice and use a qualified/current source."

    if tool_result.get("error"):
        return str(tool_result["error"])

    return f"Tool completed with result: {tool_result}"


def run_agent_turn(user_query: str) -> dict:
    """Run one MCP-agent turn."""
    available_tools = list_mcp_tool_names()
    selected_tool = choose_mcp_tool(user_query)
    tool_arguments = build_tool_arguments(selected_tool, user_query)

    # The MCP server helper handles the actual tool call.
    tool_result = call_tool(selected_tool, tool_arguments)
    final_answer = create_final_answer(tool_result)

    return {
        "user_query": user_query,
        "available_tools": available_tools,
        "selected_tool": selected_tool,
        "tool_arguments": tool_arguments,
        "tool_result": tool_result,
        "final_answer": final_answer,
    }


if __name__ == "__main__":
    example_queries = [
        "How do I get a tax ID in Germany?",
        "Translate this: Ich brauche einen Termin.",
        "Draft a polite reply saying I will send the documents tomorrow.",
        "Which German stock should I buy this month?",
        "What is the weather in Berlin today?",
    ]

    for query in example_queries:
        print("=" * 80)
        result = run_agent_turn(query)

        print(f"User query: {result['user_query']}")
        print(f"Available tools: {', '.join(result['available_tools'])}")
        print(f"Selected MCP tool: {result['selected_tool']}")
        print("Tool arguments:")
        pprint(result["tool_arguments"])
        print("Tool result:")
        pprint(result["tool_result"])
        print("Final answer:")
        print(result["final_answer"])
        print()
