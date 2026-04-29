# Agent Learning: 05 Multi-Agent

This folder is a learning-only demo for a simple multi-agent system.

It does not change the main Streamlit app, deployment files, or production RAG chatbot.

## What Is a Multi-Agent System?

A multi-agent system uses more than one agent. Each agent has a specific role.

In this demo:

- `PlannerAgent` receives the user query
- specialist agents handle different topic areas
- factual specialists use the real RAG tool
- communication and safety specialists use mock skills

## How This Differs From a Single Agent

A single agent handles every query by itself.

A multi-agent system separates responsibilities:

```text
PlannerAgent -> chooses specialist -> specialist uses a tool -> final answer
```

This makes the design easier to understand and extend.

## Specialist Agents

- `VisaAgent`: Blue Card, visa, residence permit, settlement permit, opportunity card, job seeker visa
- `TaxAgent`: Tax ID, tax class, Finanzamt, tax bureaucracy
- `HousingAgent`: Anmeldung, renting, landlord, apartment documents, Wohnungsgeberbestätigung
- `HealthAgent`: health insurance, statutory/private insurance, doctor visits, medical system basics
- `FamilyAgent`: Kindergeld, Elterngeld, family reunification, spouse/family support
- `SchoolKitaAgent`: Kita, school, childcare, kindergarten, education
- `TravelLeisureAgent`: day trips, hiking, festivals, must-see places, travel in Germany
- `JobsAgent`: finding jobs, applications, recognition of qualifications, Bundesagentur für Arbeit, unemployment basics
- `CommunicationAgent`: translation, polite German replies, official text explanation, action items
- `SafetyAgent`: legal court advice, financial advice, medical advice, live/current data, vague requests, out-of-scope questions

## How PlannerAgent Routes Queries

`PlannerAgent` is rule-based.

It checks `SafetyAgent` first so high-risk or vague requests are not routed into normal RAG answers.

Then it checks each specialist agent with:

```python
can_handle(query)
```

The first matching specialist handles the query.

## How RAG Is Used

Factual specialist agents call:

```python
search_real_rag_docs(query)
```

That function reuses the existing RAG pipeline from `agent_learning/04_agent_with_rag/`.

So factual agents do not know the details of Gemini embeddings, FAISS, or vectorstore files. They simply call the RAG tool.

## Why This Version Is Rule-Based First

This version keeps planning simple and transparent.

Rule-based routing makes it easy to see:

- why an agent was selected
- which tool was used
- what result came back
- how the final answer was created

Later, this planner could be replaced with an LLM planner.

## How to Run

From the project root:

```bash
python agent_learning/05_multi_agent/multi_agent_demo.py
```

## Requirements

For factual RAG examples, you need:

- `GEMINI_API_KEY` in `.env` or as an environment variable
- `vectorstore/faiss.index`
- `vectorstore/chunks.json`

If vectorstore files are missing, rebuild them:

```bash
python ingest.py
```

## What to Observe

For each example query, the demo prints:

- user query
- planner-selected agent
- skill/tool used
- result
- final answer

This is the first learning step toward more advanced multi-agent systems.
