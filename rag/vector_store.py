import hashlib
from pathlib import Path

import chromadb


# --------------------------------------------------
# Chroma persistent database
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "chroma_db"

DB_PATH.mkdir(parents=True, exist_ok=True)


client = chromadb.PersistentClient(
    path=str(DB_PATH)
)


# IMPORTANT:
# v2 starts with a fresh collection.
# This prevents old embeddings from the previous
# version of VidyānVaya AI from interfering.
collection = client.get_or_create_collection(
    name="academic_documents_v2"
)


# --------------------------------------------------
# Generate a stable ID for every chunk
# --------------------------------------------------

def create_chunk_id(file_id, index):
    return f"{file_id}_chunk_{index}"


# --------------------------------------------------
# Store embeddings
# --------------------------------------------------

def store_embeddings(
    chunks,
    embeddings,
    source_name,
    file_id
):
    """
    Store document chunks and their embeddings.

    Each chunk stores:
    - source filename
    - file ID
    - chunk index
    """

    if not chunks:
        return

    # Remove the previous version of this filename.
    # This prevents duplicate/stale chunks when the
    # same document is uploaded again.
    collection.delete(
        where={
            "source": source_name
        }
    )

    ids = []
    metadatas = []

    for index, chunk in enumerate(chunks):

        chunk_id = create_chunk_id(
            file_id,
            index
        )

        ids.append(chunk_id)

        metadatas.append(
            {
                "source": source_name,
                "file_id": file_id,
                "chunk_index": index
            }
        )

    # Convert numpy array to normal Python list
    if hasattr(embeddings, "tolist"):
        embeddings_list = embeddings.tolist()
    else:
        embeddings_list = embeddings

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings_list,
        metadatas=metadatas
    )


# --------------------------------------------------
# Number of stored chunks
# --------------------------------------------------

def get_collection_count():

    result = collection.get()

    return len(result["ids"])


# --------------------------------------------------
# Get all uploaded document names
# --------------------------------------------------

def get_document_names():

    result = collection.get()

    metadatas = result.get("metadatas", [])

    documents = set()

    for metadata in metadatas:

        if metadata and "source" in metadata:

            documents.add(
                metadata["source"]
            )

    return sorted(documents)


# --------------------------------------------------
# Delete a complete document
# --------------------------------------------------

def delete_document(source_name):

    collection.delete(
        where={
            "source": source_name
        }
    )


# --------------------------------------------------
# Create a file ID from its contents
# --------------------------------------------------

def create_file_id(file_bytes):

    return hashlib.sha256(
        file_bytes
    ).hexdigest()[:16]