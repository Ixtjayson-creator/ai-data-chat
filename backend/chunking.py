from typing import List

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
    """
    Splits a long string into smaller chunks of a specified size with overlap.
    
    Why chunking is needed for RAG (Retrieval-Augmented Generation):
    1. Context Window Limits: LLMs have a limited context window. Chunks ensure we only 
       feed relevant sections to the model without exceeding its limits.
    2. Retrieval Precision: Embedding a whole document creates a "blurry" vector. 
       Chunking allows the vector store to find the exact paragraph or section 
       that matches the user's query.
    3. Cost & Performance: Processing smaller, relevant chunks is faster and more 
       cost-effective than sending entire documents to an LLM.
    4. Context Preservation: The overlap (50 characters) ensures that semantic meaning 
       is maintained even if a sentence is split between two chunks.

    Args:
        text (str): The input text to be chunked.
        chunk_size (int): Max number of characters per chunk. Default 400.
        overlap (int): Number of characters to overlap between chunks. Default 50.
        
    Returns:
        List[str]: A list of text chunks.
    """
    if not text:
        return []
        
    chunks = []
    start = 0
    
    while start < len(text):
        # Calculate the end position
        end = start + chunk_size
        
        # Get the chunk
        chunk = text[start:end]
        chunks.append(chunk)
        
        # Move the start pointer forward, subtracting the overlap
        start += (chunk_size - overlap)
        
        # Safety break for edge cases where overlap >= chunk_size
        if chunk_size <= overlap:
            break
            
    return chunks

if __name__ == "__main__":
    # Test with sample text
    sample_text = "This is a sample text used to demonstrate how chunking works in a RAG system. " * 10
    test_chunks = chunk_text(sample_text)
    print(f"Total Chunks: {len(test_chunks)}")
    for i, c in enumerate(test_chunks[:3]):
        print(f"Chunk {i+1} (Length {len(c)}): {c[:50]}...")
