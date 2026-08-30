from rag.embeddings import create_embeddings
from rag.vector_store import collection


def retrieve_relevant_chunks(query, n_results=5):
    """
    Retrieve the most relevant document chunks
    for a user's question using semantic similarity.
    """

    query_embedding = create_embeddings([query])

    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=n_results
    )

    if not results or "documents" not in results:
        return []

    documents = results["documents"][0]

    return documents