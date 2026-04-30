# Agent Learning Path

This folder is a learning lab for agents, tools, RAG, multi-agent systems, and MCP.

It does not modify the main Expat Germany AI Assistant app.

## 1. Skills

Folder: `01_skills`

Run:

```bash
python agent_learning/01_skills/skills.py
```

Demonstrates:

- skills are normal Python functions
- each skill does one clear job
- `SKILL_REGISTRY` works like a menu of tools

Understand:

- skills = callable functions
- registry = list of available tools
- future agents can choose from the registry

## 2. Rule-Based Single Agent

Folder: `02_single_agent`

Run:

```bash
python agent_learning/02_single_agent/simple_agent.py
```

Demonstrates:

- one agent receives a query
- the agent classifies intent
- the agent chooses a skill from the registry
- the selected skill is executed

Understand:

- an agent is a decision-maker
- rule-based agents use simple if/else logic
- this is the first step beyond standalone skills

## 3. LLM Tool-Using Agent

Folder: `03_llm_tool_agent`

Run:

```bash
python agent_learning/03_llm_tool_agent/llm_tool_agent.py
```

Demonstrates:

- Gemini receives tool declarations
- Gemini chooses which mock tool to call
- Python executes the selected tool
- the tool result is sent back to Gemini

Understand:

- function calling lets an LLM request tools
- the LLM chooses, but Python executes
- this differs from rule-based routing

## 4. Agent With RAG as a Tool

Folder: `04_agent_with_rag`

Run:

```bash
python agent_learning/04_agent_with_rag/rag_tool_agent.py
```

Demonstrates:

- the existing RAG pipeline becomes a callable tool
- Gemini can choose real RAG for factual Germany questions
- mock tools still handle translation, drafting, safety, and clarification

Understand:

- RAG can be one tool among many
- agents can choose when retrieval is needed
- this separates tool choice from answer generation

## 5. Multi-Agent System

Folder: `05_multi_agent`

Run:

```bash
python agent_learning/05_multi_agent/multi_agent_demo.py
```

Demonstrates:

- `PlannerAgent` routes queries to specialist agents
- specialist agents handle visas, taxes, housing, health, family, jobs, travel, communication, and safety
- factual specialists use RAG as a tool

Understand:

- multi-agent systems split responsibility
- a planner chooses the right specialist
- rule-based planning is easier to debug before adding LLM planning

## 6. MCP Server

Folder: `06_mcp_server`

Run demo mode:

```bash
python agent_learning/06_mcp_server/server.py --demo
```

Run server mode:

```bash
python agent_learning/06_mcp_server/server.py
```

Demonstrates:

- selected skills are exposed as MCP-style tools
- an `available_skills` resource is exposed
- the server listens over stdio for MCP-style messages

Understand:

- MCP exposes tools through a protocol
- MCP tools are different from direct Python imports
- running the server directly waits for an MCP client unless using `--demo`

## 7. Agent Using MCP Tools

Folder: `07_agent_with_mcp`

Run:

```bash
python agent_learning/07_agent_with_mcp/agent_with_mcp.py
```

Demonstrates:

- an agent discovers tools from the MCP-style server
- the agent chooses a tool with simple rules
- the agent calls the MCP-exposed tool and formats a final answer

Understand:

- an MCP client discovers and calls server-exposed tools
- the agent no longer imports skills directly
- this is a bridge toward real MCP-based agent systems

## Big Picture

The learning path builds gradually:

```text
skills -> single agent -> LLM tool agent -> RAG tool agent -> multi-agent system -> MCP server -> MCP client agent
```

The core idea:

```text
Skills = functions
Registry = menu of tools
Agent = decision-maker
RAG = one possible tool
MCP = protocol for exposing tools
```
