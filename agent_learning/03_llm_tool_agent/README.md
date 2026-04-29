# Agent Learning: 03 LLM Tool Agent

This folder is a learning-only demo for an LLM-based tool-using agent.

It does not change the main Streamlit app, deployment files, or production RAG chatbot.

## What Is an LLM Tool-Using Agent?

An LLM tool-using agent is an agent where the language model helps decide which tool should be called.

The flow is:

```text
User query -> Gemini chooses a tool -> Python runs the tool -> Gemini writes final answer
```

## How This Differs From the Rule-Based Agent

The previous demo in `02_single_agent` used simple Python rules:

```text
if query contains "translate" -> call translate_text_mock
```

This demo lets Gemini choose the tool from declared options.

So:

```text
02_single_agent = Python rules choose the tool
03_llm_tool_agent = Gemini chooses the tool
```

## What Function Calling / Tool Use Means

Function calling means we describe Python functions to Gemini using tool declarations.

A tool declaration tells Gemini:

- tool name
- what the tool does
- expected input parameters
- parameter types

Gemini does not execute Python itself. It only requests a tool call.

Python then:

1. reads the requested tool name
2. reads the tool arguments
3. finds the matching Python function
4. executes it
5. sends the result back to Gemini

## Tools Exposed

This demo exposes these mock skills from `agent_learning/01_skills/skills.py`:

- `search_docs_mock`
- `translate_text_mock`
- `draft_polite_reply_mock`
- `explain_official_text_mock`
- `safety_check_mock`
- `ask_clarifying_question_mock`

## How the Script Works

For each example query, the script:

1. sends the user query to Gemini with tool declarations
2. checks whether Gemini requested a tool call
3. prints the selected tool name
4. prints the tool arguments
5. executes the matching Python mock skill
6. prints the tool result
7. sends the tool result back to Gemini
8. prints Gemini's final answer

If Gemini does not request a tool call, the script prints Gemini's direct answer.

If one example fails, the script prints the error and continues to the next example.

## API Key

The script reads `GEMINI_API_KEY` from:

- `.env`
- environment variable

Example `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

## How to Run

From the project root:

```bash
python agent_learning/03_llm_tool_agent/llm_tool_agent.py
```

## What to Observe

Watch for:

- which tool Gemini selects
- what arguments Gemini passes
- how Python executes the selected skill
- how the tool result is returned to Gemini
- how the final answer differs from the raw tool result

This is the bridge between simple skills and future real agent systems.
