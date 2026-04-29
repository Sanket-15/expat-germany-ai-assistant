from pathlib import Path


DATA_DIR = Path("data")
VECTORSTORE_DIR = Path("vectorstore")

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
EMBEDDING_BATCH_SIZE = 100

MODEL_NAMES = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

DEBUG = False

INSUFFICIENT_MESSAGE = (
    "I don\u2019t have enough information from the current documents to answer "
    "this reliably."
)

IMPORTANT_NOTE = (
    "Important note: This is an informational answer based on the available "
    "documents. For personal cases, check the official source or contact the "
    "relevant authority."
)
