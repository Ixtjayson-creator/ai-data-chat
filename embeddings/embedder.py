import uuid
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from vector_db.qdrant_client import QdrantClientHandler

class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initializes the Embedding model and Qdrant connection.
        """
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.qdrant = QdrantClientHandler()

    def chunk_document(self, text: str, source: str, metadata: Dict[str, Any] = None, chunk_size: int = 200) -> List[Dict[str, Any]]:
        """
        Splits a document's text into smaller chunks based on word count.
        Returns a list of chunk dictionaries structured with text, source, and metadata.
        """
        if metadata is None:
            metadata = {}
            
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk_text = " ".join(words[i:i+chunk_size])
            chunks.append({
                "text": chunk_text,
                "source": source,
                "metadata": metadata
            })
            
        return chunks

    def process_and_store(self, chunks_data: List[Dict[str, Any]]):
        """
        Generates embeddings for each chunk and stores them into Qdrant.
        chunks_data must follow the format:
        {
            "text": "...",
            "source": "...",
            "metadata": {...}
        }
        """
        if not chunks_data:
            return

        print(f"Generating embeddings for {len(chunks_data)} chunks...")
        # Extract the pure text for generating the vectors
        texts = [chunk["text"] for chunk in chunks_data]
        embeddings = self.model.encode(texts).tolist()

        print("Storing embeddings in Qdrant...")
        for chunk, vector in zip(chunks_data, embeddings):
            # Create a unique UUID for each point
            point_id = str(uuid.uuid4())
            
            # Formulate the payload properly for Qdrant storage
            payload = {
                "text_chunk": chunk["text"],
                "source": chunk["source"],
                "metadata": chunk.get("metadata", {})
            }
            
            # Using the existing QdrantClientHandler method to insert
            self.qdrant.insert_embedding(id=point_id, vector=vector, payload=payload)
            
        print("Storage complete.")
