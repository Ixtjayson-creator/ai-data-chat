from typing import List, Dict, Any
from vector_db.qdrant_client import QdrantClientHandler

class Retriever:
    def __init__(self, embedding_model, qdrant_handler: QdrantClientHandler = None):
        """
        Initializes the retriever with an embedding model and a Qdrant client handler.
        """
        self.embedding_model = embedding_model
        self.qdrant = qdrant_handler if qdrant_handler else QdrantClientHandler()

    def retrieve(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves top similar documents for a given query.
        Returns a list of dictionaries containing text chunk, similarity score, and metadata.
        """
        # 1. Receive user query & 2. Generate query embedding
        query_vector = self.embedding_model.encode([query])[0].tolist()

        # 3. Search Qdrant for top similar vectors
        search_results = self.qdrant.search_similar(query_vector=query_vector, limit=limit)

        results = []
        # 4. Retrieve the associated text chunks and 5. Return results
        for hit in search_results:
            results.append({
                "text_chunk": hit.payload.get("text_chunk", ""),
                "score": hit.score,
                "metadata": hit.payload.get("metadata", {}),
                "source": hit.payload.get("source", "Unknown Document")
            })

        return results
