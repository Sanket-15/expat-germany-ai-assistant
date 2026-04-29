# Agent Learning: 01 Skills

This folder is a learning-only sandbox for the future **Expat Germany Agent Lab**.

It does not change the main Streamlit app, the RAG chatbot, deployment files, or production behavior.

## What Is a Skill or Tool?

A skill is a normal Python function that does one clear job.

Examples:

- search documents
- translate text
- draft a polite reply
- classify intent
- check safety
- format an answer with sources

In this folder, skills are simple mock functions. They do not call Gemini, FAISS, or the main chatbot yet.

## How Skills Are Different From an Agent

Skills are functions.

An agent is a decision-maker.

The agent decides:

1. What does the user want?
2. Which skill should be used?
3. What input should be passed to the skill?
4. What should happen after the skill returns a result?

So the relationship is:

```text
Skills = functions
Skill registry = menu of available tools
Agent = decision-maker that chooses from the menu
```

## Why Agents Need Skills

Without tools, an agent can only produce text.

With skills, an agent can take actions such as:

- searching documents
- translating text
- drafting replies
- checking safety
- extracting action items
- formatting final answers

This makes the agent more useful and easier to control.

## What Is a Skill Registry?

The skill registry is a dictionary that lists all available skills.

Each registry entry includes:

- function reference
- description
- expected intent
- input arguments
- example user query

The function reference is callable, which means a future agent can choose a skill from the registry and run it.

## Why the Registry Helps Future Agents

The registry acts like a tool menu.

A future single-agent tool selector can:

1. classify the user intent
2. inspect the registry
3. choose the best skill
4. call the selected Python function
5. use the returned dictionary to decide the next step

## Skills Included

- `search_docs_mock`: returns a mock RAG-style document search result
- `translate_text_mock`: returns a mock translation
- `draft_polite_reply_mock`: drafts a polite German reply
- `explain_official_text_mock`: explains official/bureaucratic text simply
- `create_first_month_checklist_mock`: creates a first-month Germany checklist
- `summarize_sources_mock`: summarizes source filenames or URLs
- `classify_intent_mock`: classifies a query into a simple intent
- `safety_check_mock`: detects legal, financial, medical, or live-data risk
- `format_answer_with_sources_mock`: formats an answer with sources
- `extract_action_items_mock`: extracts action items from a message
- `recommend_next_skill_mock`: recommends which skill should run next
- `create_learning_summary_mock`: explains RAG, agents, tools, or MCP simply
- `ask_clarifying_question_mock`: asks a clarifying question for vague requests

## How to Run the Demo

From the project root, run:

```bash
python agent_learning/01_skills/skills.py
```

The demo prints:

- available skills from the registry
- one example call for each skill
- how normal Python functions can behave like tools
- how the registry acts like a menu for a future agent

## Next Learning Step

Later, a single agent can be added that:

1. reads the user query
2. calls `classify_intent_mock`
3. asks `recommend_next_skill_mock` which skill to use
4. calls the chosen function from `SKILL_REGISTRY`
5. formats a final answer
