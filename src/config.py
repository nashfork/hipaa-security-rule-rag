import os
import chromadb
import google.genai as genai


# API key
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# Model configuration
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
GEMINI_MODEL_NAME = 'gemini-2.5-flash'

# ChromaDB configuration
CHROMA_PATH = './chroma_db'
COLLECTION_NAME = 'hipaa_docs'
RETRIEVAL_K = 5

# Initialize ChromaDB client and collection
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={'hnsw:space': 'cosine'}
)

# Initialize Gemini client
gemini_client = genai.Client(api_key=GOOGLE_API_KEY)