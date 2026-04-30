"""Learning-only MCP server demo.

This file exposes a few existing Python skills as MCP-style tools over stdio.

It is intentionally small and beginner-friendly:
- no HTTP server
- no Gemini calls
- no changes to the main Streamlit app
- no changes to the production RAG chatbot

MCP normally uses JSON-RPC messages over stdio. This demo implements the small
subset needed to list tools, call tools, list resources, and read one resource.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from pprint import pprint
from typing import Any


CURRENT_DIR = Path(__file__).resolve().parent
SKILLS_DIR = CURRENT_DIR.parent / "01_skills"
sys.path.append(str(SKILLS_DIR))

from skills import (  # noqa: E402
    SKILL_REGISTRY,
    draft_polite_reply_mock,
    list_available_skills,
    safety_check_mock,
    search_docs_mock,
    translate_text_mock,
)


SERVER_NAME = "expat-germany-learning-mcp"
SERVER_VERSION = "0.1.0"


def log(message: str) -> None:
    """Write logs to stderr so stdout can stay reserved for MCP messages."""
    print(f"[{SERVER_NAME}] {message}", file=sys.stderr, flush=True)


def read_message() -> dict[str, Any] | None:
    """Read one JSON-RPC message from stdio using Content-Length framing."""
    headers = {}

    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None

        line_text = line.decode("utf-8").strip()
        if not line_text:
            break

        key, value = line_text.split(":", 1)
        headers[key.lower()] = value.strip()

    content_length = int(headers.get("content-length", "0"))
    if content_length <= 0:
        return None

    body = sys.stdin.buffer.read(content_length)
    return json.loads(body.decode("utf-8"))


def write_message(message: dict[str, Any]) -> None:
    """Write one JSON-RPC message to stdio using Content-Length framing."""
    body = json.dumps(message, ensure_ascii=False).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")
    sys.stdout.buffer.write(header + body)
    sys.stdout.buffer.flush()


def make_text_content(data: Any) -> list[dict[str, str]]:
    """Return MCP text content from any JSON-serializable Python value."""
    return [
        {
            "type": "text",
            "text": json.dumps(data, indent=2, ensure_ascii=False),
        }
    ]


def tool_definitions() -> list[dict[str, Any]]:
    """Describe the Python skills as MCP tools."""
    return [
        {
            "name": "search_docs_mock",
            "description": "Search saved Germany-related documents using mock RAG logic.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The Germany-related question to search for.",
                    }
                },
                "required": ["query"],
            },
        },
        {
            "name": "translate_text_mock",
            "description": "Translate user-provided text using mock translation logic.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to translate.",
                    },
                    "target_language": {
                        "type": "string",
                        "description": "The target language.",
                        "default": "English",
                    },
                },
                "required": ["text"],
            },
        },
        {
            "name": "draft_polite_reply_mock",
            "description": "Draft a polite German reply using mock drafting logic.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "What the reply should say.",
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context for the reply.",
                        "default": "",
                    },
                },
                "required": ["message"],
            },
        },
        {
            "name": "safety_check_mock",
            "description": "Detect high-risk legal, financial, medical, or live-data requests.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_query": {
                        "type": "string",
                        "description": "The user query to safety-check.",
                    }
                },
                "required": ["user_query"],
            },
        },
    ]


def resource_definitions() -> list[dict[str, str]]:
    """Expose one MCP resource listing available skills."""
    return [
        {
            "uri": "learning://available_skills",
            "name": "available_skills",
            "description": "List of mock skills available in the learning registry.",
            "mimeType": "application/json",
        }
    ]


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Call the matching Python skill and return its dictionary result."""
    log(f"Tool called: {name}")
    log(f"Arguments: {arguments}")

    if name == "search_docs_mock":
        result = search_docs_mock(query=arguments["query"])
    elif name == "translate_text_mock":
        result = translate_text_mock(
            text=arguments["text"],
            target_language=arguments.get("target_language", "English"),
        )
    elif name == "draft_polite_reply_mock":
        result = draft_polite_reply_mock(
            message=arguments["message"],
            context=arguments.get("context", ""),
        )
    elif name == "safety_check_mock":
        result = safety_check_mock(user_query=arguments["user_query"])
    else:
        result = {
            "error": f"Unknown tool: {name}",
            "available_tools": [tool["name"] for tool in tool_definitions()],
        }

    log(f"Result: {result}")
    return result


def read_resource(uri: str) -> dict[str, Any]:
    """Return the available_skills resource."""
    log(f"Resource requested: {uri}")

    if uri != "learning://available_skills":
        return {"error": f"Unknown resource: {uri}"}

    return {
        "registry_size": len(SKILL_REGISTRY),
        "skills": list_available_skills(),
    }


def handle_request(request: dict[str, Any]) -> dict[str, Any] | None:
    """Handle one JSON-RPC request or notification."""
    method = request.get("method")
    request_id = request.get("id")
    params = request.get("params", {})

    # Notifications have no id and do not need a response.
    if request_id is None:
        log(f"Notification received: {method}")
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION,
                },
                "capabilities": {
                    "tools": {},
                    "resources": {},
                },
            },
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tool_definitions()},
        }

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        result = call_tool(tool_name, arguments)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": make_text_content(result),
                "isError": "error" in result,
            },
        }

    if method == "resources/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"resources": resource_definitions()},
        }

    if method == "resources/read":
        uri = params.get("uri", "")
        result = read_resource(uri)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(result, indent=2, ensure_ascii=False),
                    }
                ]
            },
        }

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": -32601,
            "message": f"Method not found: {method}",
        },
    }


def main() -> None:
    """Run the stdio MCP server loop."""
    if "--demo" in sys.argv:
        run_demo()
        return

    if sys.stdin.isatty():
        print(
            "This is an MCP stdio server. It waits for an MCP client to send "
            "JSON-RPC messages over stdin, so running it directly will look "
            "like it is hanging.\n\n"
            "For a simple learning demo, run:\n"
            "python agent_learning/06_mcp_server/server.py --demo\n\n"
            "To use it as an MCP server, configure an MCP client to launch:\n"
            "python agent_learning/06_mcp_server/server.py"
        )
        return

    log("Starting MCP learning server over stdio.")

    while True:
        request = read_message()
        if request is None:
            log("No more input. Server stopped.")
            break

        response = handle_request(request)
        if response is not None:
            write_message(response)


def run_demo() -> None:
    """Run a simple local demo without requiring an MCP client."""
    print("MCP learning server demo")
    print("\nAvailable tools:")
    pprint(tool_definitions())

    print("\nAvailable resources:")
    pprint(resource_definitions())

    print("\nCalling search_docs_mock:")
    pprint(call_tool("search_docs_mock", {"query": "How do I get a tax ID?"}))

    print("\nCalling translate_text_mock:")
    pprint(
        call_tool(
            "translate_text_mock",
            {
                "text": "Ich brauche einen Termin.",
                "target_language": "English",
            },
        )
    )

    print("\nReading available_skills resource:")
    pprint(read_resource("learning://available_skills"))


if __name__ == "__main__":
    main()
