import logging
from typing import List, Any
from sentence_transformers import SentenceTransformer

# Initialize the model globally to avoid reloading it on every function call.
# 'all-MiniLM-L6-v2' is a lightweight and efficient model for RAG.
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    logging.error(f"Failed to load sentence-transformer model: {e}")
    model = None

def embed_documents(chunks: List[str]) -> List:
    """
    Generates embeddings for a list of text chunks.
    
    Args:
        chunks (List[str]): List of document chunks to embed.
        
    Returns:
        List: A list of embedding vectors (numpy arrays or lists).
    """
    if not model:
        logging.error("Model not initialized. Cannot embed documents.")
        return []
    
    if not chunks:
        return []
        
    try:
        # model.encode returns a numpy array by default
        embeddings = model.encode(chunks)
        # Convert to list if needed for serialization, but usually numpy arrays are fine for vector stores
        return embeddings.tolist()
    except Exception as e:
        logging.error(f"Error embedding documents: {e}")
        return []

def embed_query(query: str) -> List:
    """
    Generates an embedding for a single user query.
    
    Args:
        query (str): The user query text.
        
    Returns:
        List: The embedding vector for the query.
    """
    if not model:
        logging.error("Model not initialized. Cannot embed query.")
        return []
        
    if not query:
        return []
        
    try:
        embedding = model.encode([query])
        return embedding[0].tolist()
    except Exception as e:
        logging.error(f"Error embedding query: {e}")
        return []

if __name__ == "__main__":
    # Test block
    test_chunks = ["This is a test document chunk.", "Another piece of data."]
    doc_embeddings = embed_documents(test_chunks)
    print(f"Number of document embeddings: {len(doc_embeddings)}")
    
    test_query = "What is the test document about?"
    query_embedding = embed_query(test_query)
    print(f"Query embedding length: {len(query_embedding)}")
