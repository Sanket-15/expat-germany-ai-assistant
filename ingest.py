import os

import faiss
import numpy as np
from dotenv import load_dotenv
from google import genai

from config import DATA_DIR, EMBEDDING_DIMENSIONS, VECTORSTORE_DIR
from rag import embed_texts, load_vector_store, save_vector_store, split_text


def get_title(text, fallback):
    for line in text.splitlines()[:10]:
        if line.lower().startswith("title:"):
            return line.split(":", 1)[1].strip()

    return fallback


def get_source_urls(text):
    urls = []

    for line in text.splitlines()[:5]:
        line_lower = line.lower()
        if line_lower.startswith("source:") or line_lower.startswith("source url:"):
            source = line.split(":", 1)[1].strip()
            if source and source not in urls:
                urls.append(source)

    return urls


def normalize_chunk(text):
    return " ".join(text.lower().split())


def load_documents():
    documents = []

    for path in DATA_DIR.glob("*.txt"):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue

        documents.append(
            {
                "filename": path.name,
                "title": get_title(text, path.stem.replace("_", " ").title()),
                "source_urls": get_source_urls(text),
                "text": text,
            }
        )

    return documents


def load_existing_embeddings():
    try:
        existing_index, existing_chunks = load_vector_store()
    except FileNotFoundError:
        return {}

    embedding_cache = {}

    for index_number, chunk in enumerate(existing_chunks):
        chunk_key = normalize_chunk(chunk["text"])
        embedding_cache[chunk_key] = existing_index.reconstruct(index_number)

    print(f"Reusing embeddings for {len(embedding_cache)} existing chunks when possible.")
    return embedding_cache


def build_chunks(documents):
    chunks = []
    seen_chunks = set()

    for document in documents:
        for text_chunk in split_text(document["text"]):
            chunk_key = normalize_chunk(text_chunk)
            if chunk_key in seen_chunks:
                continue

            seen_chunks.add(chunk_key)
            chunks.append(
                {
                    "filename": document["filename"],
                    "title": document["title"],
                    "source_urls": document["source_urls"],
                    "text": text_chunk,
                }
            )

    return chunks


def create_embeddings(client, chunks):
    embedding_cache = load_existing_embeddings()
    embeddings = [None] * len(chunks)
    new_texts = []
    new_indexes = []

    for index_number, chunk in enumerate(chunks):
        chunk_key = normalize_chunk(chunk["text"])
        if chunk_key in embedding_cache:
            embeddings[index_number] = embedding_cache[chunk_key]
        else:
            new_indexes.append(index_number)
            new_texts.append(chunk["text"])

    if new_texts:
        print(f"Creating embeddings for {len(new_texts)} new chunks...")
        new_embeddings = embed_texts(client, new_texts)

        for index_number, embedding in zip(new_indexes, new_embeddings):
            embeddings[index_number] = embedding
    else:
        print("No new embeddings needed.")

    return np.array(embeddings, dtype="float32")


def main():
    load_dotenv()

    documents = load_documents()
    if not documents:
        print("No .txt files found in data/. Run python scrape_sources.py first.")
        return

    chunks = build_chunks(documents)
    print(f"Creating embeddings for {len(chunks)} chunks...")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Missing GEMINI_API_KEY. Add it to your .env file first.")
        return

    client = genai.Client(api_key=api_key)
    embeddings = create_embeddings(client, chunks)

    index = faiss.IndexFlatIP(EMBEDDING_DIMENSIONS)
    index.add(embeddings)

    save_vector_store(index, chunks)
    print(f"Vector database saved in {VECTORSTORE_DIR}/")


if __name__ == "__main__":
    main()
