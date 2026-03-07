from typing import List
import re

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """
    Splits long text into smaller chunks using a hierarchical approach (recursive splitting).
    
    Tries to split by double newlines (paragraphs), then single newlines, then spaces, 
    and finally characters if a segment is still too large.
    
    Args:
        text (str): The input text to be chunked.
        chunk_size (int): Target max number of characters per chunk. Default 800.
        overlap (int): Number of characters to overlap between chunks. Default 150.
        
    Returns:
        List[str]: A list of semantically preserved text chunks.
    """
    if not text:
        return []
        
    # Standardize whitespace for easier splitting
    text = re.sub(r'\r\n', '\n', text)
    
    # Recursive splitting logic:
    # 1. Try to split by paragraph
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = ""
    
    for p in paragraphs:
        if len(p) < chunk_size:
            # If current chunk + paragraph + spacing is too big
            if current_chunk and len(current_chunk) + len(p) + 2 > chunk_size:
                chunks.append(current_chunk.strip())
                # Start new chunk with some overlap from previous if possible
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + "\n\n" + p
            else:
                current_chunk = (current_chunk + "\n\n" + p).strip()
        else:
            # If a single paragraph is larger than chunk_size, split it further by line or space
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # Sub-split the large paragraph
            sub_parts = p.split('\n')
            for part in sub_parts:
                if len(part) < chunk_size:
                    if current_chunk and len(current_chunk) + len(part) + 1 > chunk_size:
                        chunks.append(current_chunk.strip())
                        overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                        current_chunk = overlap_text + "\n" + part
                    else:
                        current_chunk = (current_chunk + "\n" + part).strip()
                else:
                    # Still too large? Split by word/space
                    words = part.split(' ')
                    for word in words:
                        if current_chunk and len(current_chunk) + len(word) + 1 > chunk_size:
                            chunks.append(current_chunk.strip())
                            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                            current_chunk = overlap_text + " " + word
                        else:
                            current_chunk = (current_chunk + " " + word).strip()
                            
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return [c for c in chunks if c.strip()]

if __name__ == "__main__":
    # Test with sample text
    sample_text = ("This is a long paragraph about AI.\n\n" * 10) + ("This is another topic.\n" * 5)
    test_chunks = chunk_text(sample_text, chunk_size=200, overlap=50)
    print(f"Total Chunks: {len(test_chunks)}")
    for i, c in enumerate(test_chunks[:3]):
        print(f"--- Chunk {i+1} ---\n{c}\n")
