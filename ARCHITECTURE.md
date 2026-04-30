# Architecture

## 1. Problem Statement

Expats in Germany often need practical answers about visas, Anmeldung, tax IDs, housing, health insurance, family benefits, work, and daily life. Reliable information exists, but it is spread across official websites, public services, and trusted information portals.

The Expat Germany AI Assistant helps by answering common expat questions from saved, source-backed documents. It is designed to stay grounded in retrieved context, show sources, and avoid unsupported advice.

## 2. High-Level Architecture

Main flow:

```text
user query -> intent routing -> RAG or non-RAG skill -> Gemini answer -> sources or fallback
```

The assistant first decides whether the request needs document retrieval. Factual Germany questions use RAG. Translation, drafting, greetings, small talk, live-weather guardrails, and high-risk fallbacks bypass RAG when appropriate.

For factual questions, the system retrieves relevant document chunks from FAISS, sends the context to Gemini, and appends source filenames/URLs. If context is weak or missing, it returns a fallback instead of guessing.

## 3. Main App Components

- `streamlit_app.py`: Streamlit chat UI. It calls the shared chatbot logic and displays answers plus expandable sources.
- `scrape_sources.py`: Downloads selected reliable webpages, cleans readable text, and saves topic files into `data/`.
- `ingest.py`: Loads documents from `data/`, chunks them, creates Gemini embeddings, and builds the FAISS vectorstore.
- `data/`: Saved `.txt` source documents. Each document includes title, source URL, and content.
- `vectorstore/`: Generated FAISS index and chunk metadata used at runtime.
- `eval_runner.py`: Runs standard evaluation questions through the assistant and saves results to CSV.
- `EVALUATION_SUMMARY.md`: Portfolio-friendly summary of evaluation goals, checks, improvements, and results.
- `agent_learning/`: Learning lab for skills, agents, RAG-as-tool, multi-agent patterns, and MCP concepts.

## 4. RAG Pipeline

The RAG pipeline has five main steps:

1. **Scraped/source documents**: `scrape_sources.py` collects reliable documents from official or trusted sources.
2. **Chunking**: `rag.py` splits text into sentence-aware chunks with overlap so retrieval has useful context.
3. **Gemini embeddings**: `ingest.py` uses Gemini embeddings to convert chunks into vectors.
4. **FAISS vectorstore**: vectors are stored in `vectorstore/faiss.index`, while metadata is stored in `vectorstore/chunks.json`.
5. **Retrieval and generation**: user questions retrieve relevant chunks, Gemini answers only from that context, and sources are shown at the end.

## 5. Intent Routing

Intent routing in `app.py` separates request types before retrieval:

- **Factual RAG questions**: visa, Blue Card, residence permit, Anmeldung, Tax ID, housing, health insurance, Kindergeld, jobs, bureaucracy.
- **Translation**: bypasses RAG and translates user-provided text.
- **Drafting**: bypasses RAG and drafts polite German or English replies from user instructions.
- **Explanation**: short official-text explanations bypass RAG when based only on user-provided text.
- **Greetings/small talk**: answered locally without Gemini or FAISS.
- **High-risk/out-of-scope queries**: legal court strategy, financial recommendations, medical advice, and live/current-data questions trigger safe fallback responses.

## 6. Evaluation

`eval_runner.py` runs standard questions from `evaluation_questions.md` through the assistant and saves results to:

```text
eval_results/eval_results.csv
```

The evaluation checks:

- whether an answer was generated
- whether factual RAG answers include sources
- whether translation and drafting bypass RAG
- whether language behavior matches English/German expectations
- whether safe fallback responses trigger for high-risk or out-of-scope questions
- whether possible hallucination risk is flagged

## 7. Deployment

The app is prepared for Streamlit Cloud deployment.

Deployment requirements:

- `GEMINI_API_KEY` is provided through Streamlit Cloud secrets.
- `vectorstore/faiss.index` and `vectorstore/chunks.json` are included so the app can answer RAG questions at runtime.
- `.env` is ignored and should not be committed.

Local rebuild command:

```bash
python ingest.py
```

If source documents change, rebuild the vectorstore locally and commit the updated generated vectorstore files.

## 8. Agent Learning Lab

`agent_learning/` is a separate learning area and does not change the main app.

It includes:

- **Skills/tools**: plain Python functions and a skill registry.
- **Single agent**: rule-based agent that chooses a skill.
- **LLM tool agent**: Gemini chooses a mock tool to call.
- **RAG as a tool**: existing RAG pipeline is wrapped as a callable tool.
- **Multi-agent demo**: PlannerAgent routes to specialist agents.
- **MCP server**: exposes selected skills through an MCP-style stdio server.
- **Agent with MCP tools**: rule-based client discovers and calls MCP-exposed tools.

## 9. Limitations

- The assistant is not legal, tax, immigration, medical, or financial advice.
- It does not provide live/current data unless explicitly implemented.
- It depends on saved documents in `data/` and the generated `vectorstore/`.
- Gemini API usage depends on API availability, limits, and cost.
- Source webpages may change, so documents should be refreshed periodically.

## 10. Future Improvements

- Improve retrieval ranking and topic filtering.
- Add optional live web lookup for current information.
- Expand automated evaluation coverage.
- Add real MCP integration with an MCP client.
- Add an optional agent-mode UI.
- Improve multilingual retrieval and answer quality further.
