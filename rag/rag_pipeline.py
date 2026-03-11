from rag.retriever import Retriever
from models.llama_runner import LlamaRunner

class RAGPipeline:
    def __init__(self, retriever: Retriever, llama_runner: LlamaRunner):
        """
        Initializes the unified RAG pipeline.
        """
        self.retriever = retriever
        self.llama_runner = llama_runner

    def ask(self, question: str, top_k: int = 5) -> str:
        """
        Executes the full RAG pipeline:
        1. Receive user question
        2. Generate embedding (via retriever)
        3. Search Qdrant (via retriever)
        4. Retrieve top relevant chunks (via retriever)
        5. Construct context block
        6. Send context + question to llama.cpp (via runner)
        7. Return generated answer
        """
        # Steps 1-4: Retrieve top relevant chunks
        search_results = self.retriever.retrieve(query=question, limit=top_k)
        
        # Step 5: Construct context block
        context_parts = []
        for result in search_results:
            source = result.get("source", "Unknown Document")
            text = result.get("text_chunk", "")
            context_parts.append(f"[Source: {source}]\n{text}")
            
        context = "\n\n".join(context_parts)
        
        # Step 6 & 7: Send to llama.cpp and return answer
        answer = self.llama_runner.generate_response(context=context, question=question)
        
        return answer
