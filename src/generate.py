import google.genai as genai
from src.config import gemini_client, GEMINI_MODEL_NAME

def generate_response(query, results):
    """
    Build context from retrieved chunks and generate a grounded, cited response using Gemini.

    Args:
        query (str): The user's plain-English question.
        results (dict): ChromaDB query results returned by retrieve_chunks().

    Returns:
        str: A cited response grounded in the provided regulatory text.
    """
    system_prompt = """
    -You are a helpful healthcare privacy assistant with legal knowledge.
    -You are helping someone with knowledge of healthcare privacy and healthcare IT, but not strong legal knowledge.
    -You are helping an organization that is compliant with current HIPAA regulations but is unsure of how the proposed changes will mean for them.

    Core Rules:
    -Answer questions using only the provided context and cite your sources in responses.
    -Never provide incomplete answers or hallucinate answers.
    -Do not provide answers that are not supported by the provided context.
    -Where appropriate, identify specific changes from the current rule to the proposed new rule.
    -Only answer questions that can be answered with the context.
    -If the question cannot be answered with the context, respond "I am not allowed to answer that question."
    -Your response may include directions to implement the specific proposed changes.
    -All responses with directions must help accomplish a specific goal in the proposed changes.

    Output Rules:
    -Responses should include a brief summary (1-2 sentences) responding to the question.
    -Responses should identify actionable steps for implementing proposed changes.
    -If the query does not require actionable steps, end your response with "No actions are required."
    """

    # Extract documents and metadata from retrieval results
    documents = results['documents'][0]
    metadata_list = results['metadatas'][0]

    # Parse results into context for Gemini
    context = ""
    for document, metadata in zip(documents, metadata_list):
        context += f"[Source: {metadata['source']}, Page: {metadata['page']}]\n{document}\n\n"

    # Pass context and query to Gemini and return cited response
    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL_NAME,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt
        ),
        contents=f'Context:\n{context}\n\nQuestion: {query}'
    )

    return response.text