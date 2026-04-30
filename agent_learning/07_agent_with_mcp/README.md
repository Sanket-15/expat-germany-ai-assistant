# Agent Learning: 07 Agent With MCP

This folder is a learning-only demo for an agent client that uses MCP-exposed tools.

It does not change the main Streamlit app, deployment files, or production RAG chatbot.

## What Is an MCP Client?

An MCP client is the side that discovers and calls tools exposed by an MCP server.

In a full MCP setup:

```text
MCP client -> MCP server -> tool function
```

This demo keeps things simple by importing helper functions from the MCP-style server in `06_mcp_server`.

## How This Differs From Directly Importing Skills

Earlier demos imported skills directly from:

```text
agent_learning/01_skills/skills.py
```

This demo imports from the MCP server layer instead:

```text
agent_learning/06_mcp_server/server.py
```

That means the agent sees tools through the server's MCP-style definitions, not directly as raw Python skill functions.

## How the Agent Uses MCP-Exposed Tools

The agent:

1. lists available tools using `tool_definitions()`
2. chooses a tool with simple rules
3. builds arguments for that tool
4. calls the tool through `call_tool(...)`
5. turns the tool result into a final answer

## Why This Is Still Rule-Based

This version does not use Gemini.

The goal is to learn the MCP client idea before adding an LLM planner.

Rule-based routing makes it easy to see:

- which tool was available
- why a tool was selected
- what arguments were sent
- what result came back

## Routing Rules

- factual Germany question -> `search_docs_mock`
- translation request -> `translate_text_mock`
- polite reply request -> `draft_polite_reply_mock`
- financial/legal/medical/live/current query -> `safety_check_mock`

## How to Run

From the project root:

```bash
python agent_learning/07_agent_with_mcp/agent_with_mcp.py
```

## What to Observe

For each example query, the script prints:

- user query
- available tools
- selected MCP tool
- tool arguments
- tool result
- final answer

This is the learning bridge between local skills and MCP-style tool access.
