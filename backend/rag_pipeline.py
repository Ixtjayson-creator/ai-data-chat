import logging
from backend.chunking import chunk_text
from backend.embedding import embed_documents, embed_query
from vector_store.faiss_store import create_index, add_embeddings, search

# Dimension for all-MiniLM-L6-v2 embeddings
EMBEDDING_DIMENSION = 384

def index_document(text: str):
    """
    RAG Indexing Pipeline:
    1. Splits document text into chunks.
    2. Generates embeddings for chunks.
    3. Stores embeddings and text in FAISS.
    
    Args:
        text (str): The full text of the document to index.
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

        # 3. Initialize FAISS index if not already done
        # (In a production app, we might check if index exists or load from disk)
        create_index(EMBEDDING_DIMENSION)
        
        # 4. Store in FAISS
        add_embeddings(embeddings, chunks)
        
        logging.info(f"Successfully indexed document with {len(chunks)} chunks.")
        
    except Exception as e:
        logging.error(f"Error in indexing pipeline: {e}")

def retrieve_context(query: str) -> str:
    """
    RAG Query Pipeline:
    1. Embeds user question.
    2. Retrieves top relevant chunks from FAISS.
    3. Returns them as a single context string.
    
    Args:
        query (str): The user's query/question.
        
    Returns:
        str: Concatenated relevant chunks for LLM context.
    """
    if not query:
        return ""

    try:
        # 1. Embed user query
        query_vector = embed_query(query)

        # 2. Retrieve top relevant chunks (increased k for better context)
        relevant_chunks = search(query_vector, top_k=8)
        
        # 3. Join them into a context block
        context = "\n\n---\n\n".join(relevant_chunks)
        
        return context
        
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
