def tag_chunk(chunk_text: str, ontology: dict) -> str:
    matched_ids = []
    for concept_id, entry in ontology.items():
        terms_to_check = entry.get("tagging_terms", entry["source_terms"])
        for term in terms_to_check:
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, chunk_text, re.IGNORECASE):
                matched_ids.append(concept_id)
                break
    return ",".join(matched_ids)

def expand_concepts(concept_ids: list, ontology: dict) -> set:
    expanded = set(concept_ids)
    for cid in concept_ids:
        related = ontology.get(cid, {}).get("relates_to")
        if related:
            expanded.add(related)
    return expanded


def retrieve_chunks(query, k=5, pool_size=20):
  """
  Embed the query and retrieve a wider pool of similar chunks from ChromaDB
  for re-ranking. Returns raw ChromaDB results including documents,
  metadata, and distances.
  """
  embeddings = embedding_model.encode(query)

  results = collection.query(
    query_embeddings=[embeddings.tolist()],
    n_results=pool_size,
    include=["documents", "metadatas", "distances"]
    )
  return results

def rerank_with_ontology(query, results, ontology, boost=0.1):
    """
    Re-rank Chroma query results using ontology-based concept overlap boosting.

    Args:
        query (str): The user's plain-English question
        results (dict): Raw ChromaDB query results, must include distances
        ontology (dict): The concept ontology
        boost (float): Flat score boost applied when concept overlap exists

    Returns:
        dict: Re-ranked results in the same shape as Chroma query results,
              so it can be passed directly into generate_response()
    """
    # Tag the query and expand via ontology relations
    query_tags = tag_chunk(query, ontology)
    query_concept_ids = query_tags.split(",") if query_tags else []
    expanded_query_concepts = expand_concepts(query_concept_ids, ontology)

    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]

    scored = []
    for doc, metadata, distance in zip(documents, metadatas, distances):
        similarity = 1 - distance
        chunk_tags = metadata.get('concept_ids', '')
        chunk_concept_ids = set(chunk_tags.split(",")) if chunk_tags else set()

        overlap = chunk_concept_ids & expanded_query_concepts
        boosted_score = similarity + boost if overlap else similarity

        scored.append((boosted_score, doc, metadata))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Rebuild in the same nested-list shape generate_response expects
    reranked_results = {
        'documents': [[doc for _, doc, _ in scored]],
        'metadatas': [[metadata for _, _, metadata in scored]]
    }

    return reranked_results