# Expat Germany AI Assistant

## Live Demo

Try the app here: https://expat-germany-ai-assistant.streamlit.app

A beginner-friendly bilingual RAG chatbot for common expat questions in Germany - including visas, work, housing, taxes, health insurance, family life, studying, transport, daily life, travel, hobbies, German culture, rules, holidays, weather basics, work environment, and Indian community topics.

This project explores how to build a reliable, document-grounded AI assistant for real-world expat problems using Retrieval-Augmented Generation (RAG).

It understands and replies in English and German.
Answers are based on the documents currently available in the knowledge base.

Built end-to-end: data collection -> embedding -> vector search -> grounded answer generation.

Supports both:

- Terminal chatbot
- Streamlit chat interface

## Features

- Terminal chatbot with multi-turn interaction
- Streamlit chat UI
- Bilingual English/German questions and answers
- Gemini API for answer generation
- Gemini embeddings for document search
- FAISS vector database for retrieval
- Official-source document scraper
- Answers grounded only in retrieved documents (no hallucination)
- Source filenames and URLs shown with answers
- Local handling for greetings, thanks, and help questions
- German <-> English translation and reply-writing support

## Tech Stack

- Python
- Google Gemini API (`google-genai`)
- FAISS
- Streamlit
- Requests
- BeautifulSoup
- python-dotenv

## Project Architecture

```text
expat-germany-ai-assistant/
  app.py              # Terminal chatbot
  streamlit_app.py    # Streamlit UI
  scrape_sources.py   # Downloads and cleans source documents
  ingest.py           # Builds the FAISS vector database
  rag.py              # Chunking, embeddings, retrieval, and source formatting
  config.py           # Shared settings and paths
  data/               # Scraped text documents
  vectorstore/        # Generated FAISS index and metadata
  requirements.txt
  README.md
  .env.example
  .gitignore
```

## How it works

1. Documents are scraped from reliable sources
2. Text is split into chunks and converted into embeddings
3. FAISS stores embeddings for fast similarity search
4. User question retrieves relevant chunks
5. Gemini generates an answer grounded in retrieved context

Retrieval uses sentence-aware chunks with overlap and preserves metadata such as filename, title, source URL, topic, and language. The assistant displays only the most relevant sources for factual RAG answers and falls back when saved documents do not provide enough context.

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

## Add Gemini API Key

Create a `.env` file in the project folder.

Add your API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

You can copy the format from `.env.example`.

## Scrape Documents

Run the scraper to download selected official or reliable webpages into `data/`:

```bash
python scrape_sources.py
```

Each document is saved as a `.txt` file with:

- Title
- Source
- Content

## Build FAISS Index

```bash
python ingest.py
```

This creates the vector database inside `vectorstore/`.

## Run Terminal Chatbot

```bash
python app.py
```

Type `exit` or `quit` to stop.

## Run Streamlit UI

```bash
streamlit run streamlit_app.py
```

## Streamlit Cloud Deployment

This app can run on Streamlit Cloud as a simple Streamlit app.

### 1. Add your Gemini API key

In Streamlit Cloud, open your app settings and add this under **Secrets**:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```

Do not commit `.env` or any real API keys to GitHub.

### 2. Vectorstore requirement

Streamlit Cloud needs the generated vectorstore files to answer RAG questions:

- `vectorstore/faiss.index`
- `vectorstore/chunks.json`

These two files are allowed in Git because Streamlit Cloud needs them at runtime. Other vectorstore cache/temp files should stay ignored.

If source documents change, rebuild the vectorstore locally and commit the updated generated files:

```bash
python scrape_sources.py
python ingest.py
```

Before deployment, make sure these files exist in the repository:

```text
vectorstore/faiss.index
vectorstore/chunks.json
```

### 3. Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### 4. Run evaluation locally

```bash
python eval_runner.py
```

## Example Questions

- How do I apply for an EU Blue Card?
- What documents are needed for Anmeldung?
- How does health insurance work in Germany?
- What is the difference between cold rent and warm rent?
- How do I get a German tax ID?
- Was muss ich über die Einbürgerung wissen?
- Kann ich mit der Blue Card den Job wechseln?

## Demo

### App overview

![App overview](screenshots/streamlit_ui.png)

### Example question and answer

![Example question and answer](screenshots/streamlit_ui_demo.png)

## Evaluation

This project includes a lightweight evaluation setup for checking RAG behavior without any paid external evaluation framework.

See [EVALUATION_SUMMARY.md](EVALUATION_SUMMARY.md) for details.

[eval_runner.py](eval_runner.py) runs standard questions from [evaluation_questions.md](evaluation_questions.md) through the assistant and saves results to:

```text
eval_results/eval_results.csv
```

The evaluation checks:

- source grounding for factual RAG answers
- relevance of displayed sources after source filtering
- whether translation, sentence explanation, drafting, greetings, and small talk bypass document retrieval
- English/German language behavior
- safe fallback behavior for high-risk or out-of-scope questions
- possible hallucination risk when factual answers are long but have no sources

Translation and drafting tasks intentionally bypass document retrieval because they are based on the user-provided text, not the document knowledge base.

Run the evaluation with:

```bash
python eval_runner.py
```

## Limitations

- The assistant only answers from documents in `data/`
- It does not replace legal, tax, immigration, or financial advice
- If context is missing, it explicitly says so
- Source webpages may change, so documents should be refreshed
- `vectorstore/` is ignored by Git and must be rebuilt locally

## Future Improvements

- Improve bilingual retrieval quality and German response fluency
- Add automated document freshness checks
- Improve chunk ranking and filtering
- Add evaluation tests for retrieval and responses
- Support document upload
- Deploy as a hosted application
