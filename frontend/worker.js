// worker.js - FastAPI RAG Engine

const API_URL = 'http://localhost:8000';

async function initModels() {
    try {
        self.postMessage({ status: 'loading', message: 'Checking backend connection...' });
        
        const res = await fetch(`${API_URL}/api/status`);
        if (!res.ok) throw new Error("Backend is not responding");
        
        const data = await res.json();
        
        self.postMessage({ status: 'info', message: `Backend Connected: ${data.message}` });
        self.postMessage({ status: 'ready', message: 'DataMind Edge Ready (Python Backend)' });
    } catch (err) {
        console.error("Init Error:", err);
        self.postMessage({ status: 'error', message: `Backend Connection Error: Make sure FastAPI and Qdrant are running on port 8000. ${err.message}` });
    }
}

self.onmessage = async (e) => {
    const { type, data } = e.data;

    if (type === 'init') {
        await initModels();
    }

    if (type === 'embed') {
        const { chunks, source } = data;
        
        try {
            self.postMessage({ status: 'loading', message: 'Sending data to Qdrant (via backend)...' });
            
            const res = await fetch(`${API_URL}/upload-documents`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chunks: chunks,
                    source: source
                })
            });
            
            if (!res.ok) {
                const errText = await res.text();
                throw new Error(`Embedding Error: ${errText}`);
            }
            
            const json = await res.json();
            
            // Return empty embeddings array since Qdrant is handling vector storage natively now
            self.postMessage({ status: 'indexed', embeddings: [] });
            self.postMessage({ status: 'info', message: `Processed ${json.chunks_processed} chunks in remote vector database.` });
        } catch (err) {
            self.postMessage({ status: 'error', message: `Indexing Error: ${err.message}` });
        }
    }

    if (type === 'query') {
        const { query, history } = data; // vectorStore is no longer sent/required locally
        
        try {
            self.postMessage({ status: 'loading', message: 'Querying local llama.cpp...' });
            
            const chatRes = await fetch(`${API_URL}/ask`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: query,
                    history: history
                })
            });

            if (!chatRes.ok) {
                const errText = await chatRes.text();
                throw new Error(`Query Error: ${errText}`);
            }
            
            const chatJson = await chatRes.json();
            
            self.postMessage({ status: 'answer', answer: chatJson.answer });
        } catch (err) {
            self.postMessage({ status: 'error', message: `Thinking Error: ${err.message}` });
        }
    }
};
