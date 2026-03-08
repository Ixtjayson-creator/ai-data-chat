// worker.js - Optimized AI Intelligence (v3 with WebGPU fallback)
import { pipeline, env } from 'https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.0.2';

// Browser-native configuration
env.allowLocalModels = false;
env.useBrowserCache = true;

let embeddingPipeline = null;
let textGenerationPipeline = null;

// Initialize models
async function initModels() {
    try {
        self.postMessage({ status: 'loading', message: 'Initializing Embedding Engine...' });
        embeddingPipeline = await pipeline('feature-extraction', 'Xenova/bge-small-en-v1.5');

        self.postMessage({ status: 'loading', message: 'Initializing LLM (Qwen-2.5)...' });
        
        try {
            // Attempt WebGPU first for maximum speed
            textGenerationPipeline = await pipeline('text-generation', 'onnx-community/Qwen2.5-0.5B-Instruct', {
                dtype: 'fp16', // WebGPU works best with fp16
                device: 'webgpu'
            });
            self.postMessage({ status: 'info', message: 'Running on WebGPU (Hardware Accelerated)' });
        } catch (gpuError) {
            console.warn("WebGPU not available, falling back to WASM/CPU:", gpuError);
            
            // Fallback to WASM (Quantized 4-bit for memory efficiency)
            textGenerationPipeline = await pipeline('text-generation', 'onnx-community/Qwen2.5-0.5B-Instruct', {
                dtype: 'q4', 
                device: 'wasm'
            });
            self.postMessage({ status: 'info', message: 'Running on WASM/CPU (Compatibility Mode)' });
        }

        self.postMessage({ status: 'ready', message: 'AI Intelligence Online' });
    } catch (err) {
        console.error("Critical Model Init Error:", err);
        self.postMessage({ status: 'error', message: `Critical Error: ${err.message}. Please try a modern browser like Chrome or Edge.` });
    }
}

// Vector Similarity Search (Cosine)
function cosineSimilarity(vecA, vecB) {
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;
    for (let i = 0; i < vecA.length; i++) {
        dotProduct += vecA[i] * vecB[i];
        normA += vecA[i] * vecA[i];
        normB += vecB[i] * vecB[i];
    }
    const similarity = dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
    return isNaN(similarity) ? 0 : similarity;
}

self.onmessage = async (e) => {
    const { type, data } = e.data;

    if (type === 'init') {
        await initModels();
    }

    if (type === 'embed') {
        const { chunks, source } = data;
        const embeddings = [];
        
        try {
            for (let i = 0; i < chunks.length; i++) {
                const output = await embeddingPipeline(chunks[i], { pooling: 'mean', normalize: true });
                embeddings.push({
                    vector: Array.from(output.data),
                    text: chunks[i],
                    source: source
                });
                self.postMessage({ status: 'indexing', progress: Math.round(((i + 1) / chunks.length) * 100) });
            }
            self.postMessage({ status: 'indexed', embeddings: embeddings });
        } catch (err) {
            self.postMessage({ status: 'error', message: `Embedding Error: ${err.message}` });
        }
    }

    if (type === 'query') {
        const { query, vectorStore, history } = data;
        
        try {
            // 1. Embed Query
            const queryOutput = await embeddingPipeline(query, { pooling: 'mean', normalize: true });
            const queryVector = Array.from(queryOutput.data);

            // 2. Similarity Search
            const matches = vectorStore
                .map(item => ({ ...item, score: cosineSimilarity(queryVector, item.vector) }))
                .sort((a, b) => b.score - a.score)
                .slice(0, 5);

            // 3. Construct Context
            const context = matches.map(m => `[Source: ${m.source}]\n${m.text}`).join('\n\n---\n\n');

            // 4. Generate Answer
            const systemPrompt = `You are a High-Performance Data Intelligence Assistant. Answer the user's question based ONLY on the provided context. Cite sources like [Source: filename]. If no context is relevant, say you don't know based on the documents.
            
            CONTEXT:
            ${context}`;

            let prompt = `<|im_start|>system\n${systemPrompt}<|im_end|>\n`;
            history.forEach(msg => {
                prompt += `<|im_start|>${msg.role}\n${msg.content}<|im_end|>\n`;
            });
            prompt += `<|im_start|>user\n${query}<|im_end|>\n<|im_start|>assistant\n`;

            const output = await textGenerationPipeline(prompt, {
                max_new_tokens: 512,
                temperature: 0.1, // Lower temperature for factual stability
                do_sample: false,
                return_full_text: false,
            });

            const answer = output[0].generated_text;
            self.postMessage({ status: 'answer', answer: answer });
        } catch (err) {
            self.postMessage({ status: 'error', message: `Query Error: ${err.message}` });
        }
    }
};
