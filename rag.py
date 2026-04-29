import json
import re

import faiss
import numpy as np
from google.genai import types

from config import (
    EMBEDDING_BATCH_SIZE,
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL,
    VECTORSTORE_DIR,
)


VECTOR_STORE_DIR = VECTORSTORE_DIR
INDEX_PATH = VECTOR_STORE_DIR / "faiss.index"
CHUNKS_PATH = VECTOR_STORE_DIR / "chunks.json"


def split_into_sections(text):
    sections = []
    current_section = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        is_heading = (
            len(line) <= 90
            and not line.endswith(".")
            and not line.endswith(",")
            and not line.startswith(("-", "*", "•"))
            and not line.lower().startswith(("title:", "source:"))
        )

        if is_heading and current_section:
            sections.append("\n".join(current_section))
            current_section = [line]
        else:
            current_section.append(line)

    if current_section:
        sections.append("\n".join(current_section))

    return sections


def split_sentences(text):
    return re.split(r"(?<=[.!?])\s+", text)


def get_overlap_text(text, overlap):
    if len(text) <= overlap:
        return text

    overlap_text = text[-overlap:]
    sentence_start = re.search(r"(?<=[.!?])\s+", overlap_text)
    if sentence_start:
        return overlap_text[sentence_start.end():].strip()

    return overlap_text.strip()


def split_large_section(section, chunk_size, overlap):
    chunks = []
    current_chunk = ""

    for sentence in split_sentences(section):
        sentence = sentence.strip()
        if not sentence:
            continue

        next_chunk = f"{current_chunk} {sentence}".strip()
        if len(next_chunk) > chunk_size and current_chunk:
            chunks.append(current_chunk)
            overlap_text = get_overlap_text(current_chunk, overlap)
            current_chunk = f"{overlap_text} {sentence}".strip()
        else:
            current_chunk = next_chunk

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def split_text(text, chunk_size=1000, overlap=200):
    chunks = []

    for section in split_into_sections(text):
        if len(section) <= chunk_size:
            chunks.append(section)
            continue

        chunks.extend(split_large_section(section, chunk_size, overlap))

    return chunks


def embed_texts(client, texts):
    embeddings = []

    for start in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        batch = texts[start:start + EMBEDDING_BATCH_SIZE]
        print(f"Embedding chunks {start + 1}-{start + len(batch)} of {len(texts)}...")
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=batch,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=EMBEDDING_DIMENSIONS,
            ),
        )

        embeddings.extend(embedding.values for embedding in result.embeddings)

    embeddings = np.array(embeddings, dtype="float32")
    faiss.normalize_L2(embeddings)

    return embeddings


def embed_query(client, question):
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=question,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=EMBEDDING_DIMENSIONS,
        ),
    )

    embedding = np.array([result.embeddings[0].values], dtype="float32")
    faiss.normalize_L2(embedding)

    return embedding


def save_vector_store(index, chunks):
    VECTOR_STORE_DIR.mkdir(exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))
    CHUNKS_PATH.write_text(json.dumps(chunks, indent=2), encoding="utf-8")


def load_vector_store():
    if not INDEX_PATH.exists() or not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            "Vector database not found. Run: python ingest.py"
        )

    index = faiss.read_index(str(INDEX_PATH))
    chunks = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))

    return index, chunks


def search_documents(client, question, top_k=5, min_score=0.3):
    index, chunks = load_vector_store()
    query_embedding = embed_query(client, question)

    scores, indexes = index.search(query_embedding, top_k)

    results = []
    for score, chunk_index in zip(scores[0], indexes[0]):
        if chunk_index == -1 or score < min_score:
            continue

        chunk = chunks[chunk_index]
        chunk["score"] = float(score)
        results.append(chunk)

    return results


def format_context(results):
    context_parts = []

    for number, result in enumerate(results, start=1):
        source_urls = result.get("source_urls", [])
        if not source_urls and result.get("source_url"):
            source_urls = [result["source_url"]]

        source = result["filename"]
        if source_urls:
            source = f"{source} ({'; '.join(source_urls)})"

        context_parts.append(
            f"[Source {number}: {source}]\n{result['text']}"
        )

    return "\n\n".join(context_parts)


def format_sources(results):
    sources = []

    for result in results:
        source_urls = result.get("source_urls", [])
        if not source_urls and result.get("source_url"):
            source_urls = [result["source_url"]]

        if source_urls:
            source = f"{result['filename']} - {'; '.join(source_urls)}"
        else:
            source = result["filename"]

        if source not in sources:
            sources.append(source)

    return sources
