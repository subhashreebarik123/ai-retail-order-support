from pathlib import Path

import chromadb


BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
POLICY_FILE = KNOWLEDGE_BASE_DIR / "retail_policies.txt"
CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "retail_policies"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def split_text(text: str) -> list[str]:
    """Split text into overlapping character-based chunks."""
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


def build_knowledge_base():
    """Read the policy file and store its chunks in ChromaDB."""
    if not POLICY_FILE.exists():
        raise FileNotFoundError(f"Policy file not found: {POLICY_FILE}")

    policy_text = POLICY_FILE.read_text(encoding="utf-8")
    chunks = split_text(policy_text)

    if not chunks:
        raise ValueError("The policy file is empty.")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    # Rebuild this collection so repeated runs do not duplicate chunks.
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    collection.add(
        ids=[f"policy-{i}" for i in range(len(chunks))],
        documents=chunks,
        metadatas=[
            {"source": POLICY_FILE.name, "chunk": i}
            for i in range(len(chunks))
        ],
    )

    return len(chunks)
def ensure_knowledge_base():
    """Create the policy collection only if it does not exist."""
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    existing_collections = [
        collection.name for collection in client.list_collections()
    ]

    if COLLECTION_NAME not in existing_collections:
        count = build_knowledge_base()
        print(f"Knowledge base initialized with {count} chunks.")
    else:
        collection = client.get_collection(name=COLLECTION_NAME)
        print(
            f"Knowledge base already exists with "
            f"{collection.count()} chunks."
        )

def search_policies(question: str, n_results: int = 2) -> list[str]:
    """Retrieve the most relevant policy chunks for a question."""
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_collection(name=COLLECTION_NAME)

    result = collection.query(
        query_texts=[question],
        n_results=min(n_results, collection.count()),
    )

    return result["documents"][0] if result["documents"] else []


if __name__ == "__main__":
    count = build_knowledge_base()
    print(f"Knowledge base created with {count} chunks.")

    question = "When can a customer cancel an order?"
    results = search_policies(question)

    print(f"\nQuestion: {question}")
    print("\nRetrieved policy content:")

    for i, result in enumerate(results, start=1):
        print(f"\n--- Result {i} ---")
        print(result)
