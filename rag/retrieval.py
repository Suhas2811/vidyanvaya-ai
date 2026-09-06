from rag.embeddings import create_embeddings
from rag.vector_store import collection


def retrieve_relevant_chunks(
    query,
    source_name,
    n_results=5
):
    """
    Retrieve relevant chunks ONLY from the
    selected academic document.
    """

    # Create embedding for the student's question
    query_embedding = create_embeddings(
        [query]
    )

    if hasattr(query_embedding, "tolist"):
        query_embedding = query_embedding.tolist()

    # Find how many chunks belong to this document
    document_chunks = collection.get(
        where={
            "source": source_name
        }
    )

    total_chunks = len(
        document_chunks["ids"]
    )

    if total_chunks == 0:

        return {
            "documents": [[]],
            "distances": [[]],
            "metadatas": [[]]
        }

    # Never request more results than available
    n_results = min(
        n_results,
        total_chunks
    )

    results = collection.query(

        query_embeddings=query_embedding,

        n_results=n_results,

        # THIS IS THE IMPORTANT FIX
        where={
            "source": source_name
        }
    )

    return results