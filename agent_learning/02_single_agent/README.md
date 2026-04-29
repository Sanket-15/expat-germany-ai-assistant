# Agent Learning: 02 Single Agent

This folder is a learning-only demo for a simple single-agent workflow.

It does not change the main Streamlit app, deployment files, or production RAG chatbot.

## What Is an Agent?

An agent is a decision-maker.

It receives a user query, decides what the user wants, chooses a tool or skill, runs that skill, and turns the result into a final answer.

In simple terms:

```text
User query -> Agent -> Skill choice -> Skill result -> Final answer
```

## How This Agent Uses the Skill Registry

The agent imports `SKILL_REGISTRY` from:

```text
agent_learning/01_skills/skills.py
```

The registry acts like a menu of available tools.

The agent flow is:

1. Receive a user query
2. Call `classify_intent_mock(user_query)`
3. Call `recommend_next_skill_mock(intent)`
4. Look up the selected function in `SKILL_REGISTRY`
5. Build simple arguments for that function
6. Execute the function
7. Print the final answer

## How This Differs From the Skills-Only Demo

The previous folder, `01_skills`, only showed individual tools.

This folder adds the decision-making layer.

Difference:

```text
01_skills = functions and registry
02_single_agent = small agent that chooses and calls a function
```

The skills are still mock functions. The point here is to learn the agent loop before adding real Gemini, RAG, multi-agent systems, or MCP.

## How to Run

From the project root, run:

```bash
python agent_learning/02_single_agent/simple_agent.py
```

The demo runs five example queries:

- How do I get a tax ID in Germany?
- Translate this: Ich brauche einen Termin.
- Draft a polite reply saying I will send the documents tomorrow.
- Which German stock should I buy this month?
- I need help.

For each query, it prints:

- user query
- detected intent
- selected skill
- skill result
- final answer

## Next Learning Step

Later, this simple agent can be extended to:

- use real RAG search instead of mock search
- call Gemini for reasoning
- maintain short-term memory
- use multiple agents
- expose tools through MCP
