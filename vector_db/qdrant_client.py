import qdrant_client
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http import models

class QdrantClientHandler:
    def __init__(self, host="localhost", port=6333, collection_name="rag_documents", vector_size=384):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.client = qdrant_client.QdrantClient(host=self.host, port=self.port)
        self.create_collection()

    def create_collection(self):
        try:
            # Check if collection exists
            self.client.get_collection(self.collection_name)
            print(f"Collection '{self.collection_name}' already exists.")
        except Exception:
            # Collection does not exist, create it
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )
            print(f"Collection '{self.collection_name}' created successfully.")

    def insert_embedding(self, id, vector, payload):
        """
        Inserts a single embedding into Qdrant.
        payload must be a dict containing:
        - text_chunk (the original text chunk)
        - source (document source)
        - metadata fields
        """
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=id,
                    vector=vector,
                    payload=payload
                )
            ]
        )

    def search_similar(self, query_vector, limit=5):
        """
        Search for similar vectors in the collection.
        """
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit
        )
        return search_result.points
