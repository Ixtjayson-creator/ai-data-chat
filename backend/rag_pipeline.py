import logging
from backend.chunking import chunk_text
from backend.embedding import embed_documents, embed_query
from vector_store.faiss_store import create_index, add_embeddings, search

# Dimension for all-MiniLM-L6-v2 embeddings
EMBEDDING_DIMENSION = 384

def index_document(text: str, source: str = "Unknown"):
    """
    RAG Indexing Pipeline:
    1. Splits document text into chunks.
    2. Generates embeddings for chunks.
    3. Stores embeddings, text, and source metadata in FAISS.
    """
    if not text:
        logging.warning("Received empty text for indexing.")
        return

    try:
        # 1. Split into chunks
        chunks = chunk_text(text)
        
        # 2. Generate embeddings
        embeddings = embed_documents(chunks)
        
        if not embeddings:
            logging.error("Failed to generate embeddings.")
            return

        # 3. Store in FAISS with source metadata
        add_embeddings(embeddings, chunks, source=source)
        
        logging.info(f"Successfully indexed '{source}' with {len(chunks)} chunks.")
        
    except Exception as e:
        logging.error(f"Error in indexing pipeline: {e}")

def retrieve_context(query: str) -> str:
    """
    RAG Query Pipeline:
    1. Embeds user question.
    2. Retrieves top relevant chunks + metadata from FAISS.
    3. Returns formatted context with source citations.
    """
    if not query:
        return ""

    try:
        # 1. Embed user query
        query_vector = embed_query(query)

        # 2. Retrieve top relevant chunks (increased k for better context)
        relevant_matches = search(query_vector, top_k=8)
        
        # 3. Format as a citation-rich context block
        context_parts = []
        for match in relevant_matches:
            # match is now a dict: {'text': str, 'source': str}
            text = match.get('text', '')
            source = match.get('source', 'Unknown Document')
            context_parts.append(f"[Source: {source}]\n{text}")
            
        return "\n\n---\n\n".join(context_parts)
        
    except Exception as e:
        logging.error(f"Error in retrieval pipeline: {e}")
        return ""

if __name__ == "__main__":
    # Test simulation
    sample_doc = "The capital of France is Paris. It is known for the Eiffel Tower. The city is a major center for fashion and art."
    print("Indexing test document...")
    index_document(sample_doc)
    
    test_q = "What is the capital of France?"
    print(f"Querying: {test_q}")
    result = retrieve_context(test_q)
    print(f"Retrieved Context:\n{result}")
