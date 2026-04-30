# Agent Learning: 06 MCP Server

This folder is a learning-only demo for exposing Python skills through a simple MCP-style server.

It does not change the main Streamlit app, deployment files, or production RAG chatbot.

## What Is MCP?

MCP means Model Context Protocol.

In simple terms, MCP is a standard way for an AI system to discover and call external tools or read external resources.

Instead of hard-coding tools directly inside one chatbot, MCP lets tools be exposed by a small server.

## How This Server Exposes Tools

The server exposes selected mock skills from:

```text
agent_learning/01_skills/skills.py
```

Exposed tools:

- `search_docs_mock`
- `translate_text_mock`
- `draft_polite_reply_mock`
- `safety_check_mock`

Each MCP tool has:

- name
- description
- input schema
- Python function behind it

When a client calls a tool, the server:

1. receives the tool name and arguments
2. logs what was called
3. calls the matching Python function
4. returns the result as MCP text content

## Resource Exposed

The server also exposes one resource:

```text
learning://available_skills
```

This resource returns the list of skills from `SKILL_REGISTRY`.

## Local Python Functions vs MCP Tools

A local Python function can only be called from Python code that imports it.

An MCP tool is exposed through a protocol, so an AI client that understands MCP can discover it and call it.

Conceptually:

```text
Python function = local tool
MCP tool = protocol-accessible tool
```

## How to Run

From the project root:

```bash
python agent_learning/06_mcp_server/server.py
```

The server listens on stdio, not HTTP.

That means it waits for MCP-style JSON-RPC messages from a client over standard input and returns responses over standard output.

Debug logs are written to stderr so they do not interfere with protocol responses.

If you run the server directly in a normal terminal, it may look like it is hanging because it is waiting for an MCP client. That is expected for stdio servers.

For a simple learning demo that does not require an MCP client, run:

```bash
python agent_learning/06_mcp_server/server.py --demo
```

## Why This Is Useful

This is the bridge from local skills to MCP-based tool systems.

Previous steps:

- `01_skills`: skills are plain Python functions
- `02_single_agent`: a rule-based agent chooses skills
- `03_llm_tool_agent`: Gemini chooses mock skills
- `04_agent_with_rag`: RAG becomes a tool
- `05_multi_agent`: multiple specialist agents choose tools

This step:

- exposes skills through an MCP-style server
- prepares the project for future MCP clients
