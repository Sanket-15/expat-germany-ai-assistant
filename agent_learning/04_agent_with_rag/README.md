# Agent Learning: 04 Agent With RAG

This folder is a learning-only demo where the existing project RAG pipeline becomes a tool.

It does not change the main Streamlit app, deployment behavior, or production chatbot.

## What "RAG as a Tool" Means

RAG normally means:

```text
question -> retrieve saved document chunks -> generate grounded answer
```

In this demo, that whole RAG workflow is wrapped as one callable tool:

```text
search_real_rag_docs(query)
```

The agent can choose this tool only when the user asks a factual Germany-related question.

## How This Agent Uses FAISS / Vectorstore

The RAG tool reuses the existing project files:

- `vectorstore/faiss.index`
- `vectorstore/chunks.json`
- `data/`
- `app.answer_user_input`

If the vectorstore files are missing, the tool returns a clear message telling you to run:

```bash
python ingest.py
```

## How This Differs From the Original Chatbot

The original chatbot directly handles routing and answers the user.

This learning demo puts an agent in front:

```text
user query -> Gemini chooses a tool -> Python runs tool -> Gemini writes final answer
```

So RAG becomes one option among several tools.

## How This Differs From the Mock Tool Agent

The previous demo, `03_llm_tool_agent`, used only mock tools.

This demo keeps mock tools for translation, drafting, explanation, safety, and clarification, but replaces mock document search with the real project RAG pipeline.

## Tools Gemini Can Choose

- `search_real_rag_docs`
- `translate_text_mock`
- `draft_polite_reply_mock`
- `explain_official_text_mock`
- `safety_check_mock`
- `ask_clarifying_question_mock`

## How to Run

From the project root:

```bash
python agent_learning/04_agent_with_rag/rag_tool_agent.py
```

## What to Observe

For each example query, the script prints:

- user query
- selected tool
- tool arguments
- tool result
- final answer

Watch when Gemini chooses real RAG versus a non-RAG tool.

If Gemini returns an empty final response after a tool call, the script falls back to a readable answer from the tool result. For example, it uses `answer`, `translation`, `draft`, `explanation`, or `clarifying_question` when those fields are available.

## Requirements

You need:

- `GEMINI_API_KEY` in `.env` or as an environment variable
- existing vectorstore files:
  - `vectorstore/faiss.index`
  - `vectorstore/chunks.json`

If vectorstore files are missing, rebuild them:

```bash
python ingest.py
```
