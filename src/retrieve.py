from sentence_transformers import SentenceTransformer
from src.config import collection, EMBEDDING_MODEL_NAME, RETRIEVAL_K

# Initialize embedding model
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

def retrieve_chunks(query, k=RETRIEVAL_K):
    """
    Embed the query and retrieve the k most similar chunks from ChromaDB.
    Returns raw ChromaDB results including documents and metadata.

    Args:
        query (str): The user's plain-English question.
        k (int): Number of nearest neighbor chunks to retrieve. Defaults to RETRIEVAL_K.

    Returns:
        dict: ChromaDB query results containing documents and metadata.
    """
    # Embed the query using the same model used during ingestion
    embeddings = embedding_model.encode(query)

    # Query ChromaDB for k nearest neighbors by cosine similarity
    results = collection.query(
        query_embeddings=[embeddings.tolist()],
        n_results=k
    )

    # Return results to be passed to generate_response
    return results