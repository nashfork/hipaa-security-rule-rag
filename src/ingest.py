import fitz  # PyMuPDF - PDF parsing
from sentence_transformers import SentenceTransformer
from src.config import collection, EMBEDDING_MODEL_NAME

# Initialize embedding model
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

def ingest_document(pdf_path, source_label):
    """
    Load a PDF, chunk by page, embed chunks, and store in ChromaDB.
    source_label identifies which document the chunks came from.
    """
    # Open PDF and extract text page by page
    doc = fitz.open(pdf_path)

    # Create empty lists
    chunks = []
    metadatas = []
    ids = []

    # Loop through individual pages, chunk by page
    for page_num, page in enumerate(doc):
        text = page.get_text()

        # Skip pages with very little text (headers, footers, blank pages)
        if len(text.strip()) < 100:
            continue

        chunks.append(text)
        metadatas.append({
            'source': source_label,
            'page': page_num + 1
        })
        ids.append(f'{source_label}_page_{page_num + 1}')

    # Embed all chunks
    print(f'Embedding {len(chunks)} pages from {source_label}...')
    embeddings = embedding_model.encode(chunks).tolist()

    # Store in ChromaDB
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

    print(f'Done. {len(chunks)} chunks stored for {source_label}')