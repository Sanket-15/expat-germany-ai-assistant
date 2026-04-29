# Expat Germany AI Assistant

A beginner-friendly bilingual RAG chatbot for common expat questions in Germany — including visas, work, housing, taxes, health insurance, family life, studying, transport, daily life, travel, hobbies, German culture, rules, holidays, weather basics, work environment, and Indian community topics. It understands and replies in English and German. Answers are based on the documents currently available in the knowledge base. It supports both a terminal chatbot and a simple Streamlit chat interface.

## Features

- Terminal chatbot with multi-turn style interaction
- Streamlit chat UI
- Bilingual English/German questions and answers
- Gemini API for answer generation
- Gemini embeddings for document search
- FAISS vector database for retrieval
- Official-source document scraper
- Answers grounded only in retrieved documents
- Source filenames and URLs shown with answers
- Simple local responses for greetings, thanks, and help questions
- German and English translation/reply-writing support for user-provided text

## Tech Stack

- Python
- Google Gemini API with `google-genai`
- FAISS
- Streamlit
- Requests
- BeautifulSoup
- python-dotenv

## Project Architecture

```text
expat-ai-assistant/
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

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Add Gemini API Key

1. Create a `.env` file in the project folder.
2. Add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

You can copy the format from `.env.example`.

## Scrape Documents

Run the scraper to download selected official or reliable webpages into `data/`:

```bash
python scrape_sources.py
```

Each document is saved as a separate `.txt` file with:

- `Title:`
- `Source:`
- `Content:`

## Build FAISS Index

After scraping documents, build the vector database:

```bash
python ingest.py
```

This creates the generated FAISS files inside `vectorstore/`.

## Run Terminal Chatbot

```bash
python app.py
```

Type `exit` or `quit` to stop the terminal chatbot.

## Run Streamlit UI

```bash
streamlit run streamlit_app.py
```

## Example Questions

- How do I apply for an EU Blue Card?
- What documents are needed for Anmeldung?
- How does health insurance work in Germany?
- What is the difference between cold rent and warm rent?
- How do I get a German tax ID?
- What should I know about naturalisation?
- Can my spouse and children join me in Germany?
- What is the Deutschlandticket?

## Limitations

- The assistant only answers from documents in `data/`.
- It does not replace legal, tax, immigration, or financial advice.
- If the retrieved context is weak or missing, it should say that it does not have enough information.
- Source webpages may change, so scraped documents should be refreshed periodically.
- The generated `vectorstore/` folder is ignored by Git and should be rebuilt locally.

## Future Improvements

- Add automated document freshness checks
- Improve chunk ranking and filtering
- Add tests for retrieval and prompt behavior
- Add document upload support
- Add deployment after the local version is stable
- Add multilingual support for German and English
