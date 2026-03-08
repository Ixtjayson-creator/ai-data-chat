// script.js - Browser Control Center
const aiWorker = new Worker('worker.js', { type: 'module' });

const elements = {
    chat: document.getElementById('chat-container'),
    input: document.getElementById('query-input'),
    sendBtn: document.getElementById('send-btn'),
    fileInput: document.getElementById('file-input'),
    dropZone: document.getElementById('drop-zone'),
    filesList: document.getElementById('files-container'),
    statusText: document.getElementById('status-text'),
    progress: document.getElementById('progress-fill'),
    progressBar: document.getElementById('global-progress'),
    onlineDot: document.getElementById('online-dot'),
    engineStatus: document.getElementById('engine-status'),
    clearBtn: document.getElementById('clear-workspace')
};

let vectorStore = [];
let history = [];
let isReady = false;

// 1. Initialize AI Engine
aiWorker.postMessage({ type: 'init' });

aiWorker.onmessage = (e) => {
    const { status, message, progress, embeddings, answer } = e.data;

    if (status === 'loading') {
        elements.statusText.innerText = message;
        elements.progressBar.style.display = 'block';
        elements.progress.style.width = '10%'; // Fake progress for init
    }

    if (status === 'info') {
        elements.statusText.innerText = message;
        console.info("AI Engine Info:", message);
    }

    if (status === 'ready') {
        isReady = true;
        elements.statusText.innerText = "Local Intelligence Ready";
        elements.engineStatus.innerText = "Online";
        elements.onlineDot.classList.add('active');
        elements.input.disabled = false;
        elements.sendBtn.disabled = false;
        elements.progressBar.style.display = 'none';
        appendMessage("AI Engine ready. No data is sent to servers.", "ai");
    }

    if (status === 'indexing') {
        elements.progressBar.style.display = 'block';
        elements.progress.style.width = `${progress}%`;
        elements.statusText.innerText = `Indexing: ${progress}%`;
    }

    if (status === 'indexed') {
        vectorStore.push(...embeddings);
        elements.progressBar.style.display = 'none';
        elements.statusText.innerText = "Document Indexed Successfully";
    }

    if (status === 'answer') {
        removeThinking();
        appendMessage(answer, 'ai');
        history.push({ role: 'assistant', content: answer });
    }

    if (status === 'error') {
        elements.statusText.innerText = message;
        appendMessage(`⚠ Error: ${message}`, 'ai');
    }
};

// 2. Data Loaders (Ported chunks from Python logic)
async function parseFile(file) {
    const ext = file.name.split('.').pop().toLowerCase();
    let text = "";

    try {
        if (ext === 'pdf') {
            const arrayBuffer = await file.arrayBuffer();
            const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
            for (let i = 1; i <= pdf.numPages; i++) {
                const page = await pdf.getPage(i);
                const content = await page.getTextContent();
                text += content.items.map(item => item.str).join(' ') + "\n";
            }
        } else if (ext === 'csv') {
            text = await new Promise((resolve) => {
                Papa.parse(file, {
                    complete: (results) => {
                        const rows = results.data.map(row => 
                            Object.entries(row).map(([k, v]) => `${k}: ${v}`).join(' | ')
                        ).join('\n---\n');
                        resolve(rows);
                    },
                    header: true
                });
            });
        } else if (ext === 'xlsx' || ext === 'xls') {
            const data = await file.arrayBuffer();
            const workbook = XLSX.read(data);
            workbook.SheetNames.forEach(sheetName => {
                const sheet = workbook.Sheets[sheetName];
                text += `Sheet: ${sheetName}\n` + XLSX.utils.sheet_to_txt(sheet) + "\n";
            });
        }

        // Semantic Chunking (Simple Version)
        const chunks = text.split(/\n\n+/).filter(c => c.length > 50).map(c => c.trim());
        aiWorker.postMessage({ type: 'embed', data: { chunks, source: file.name } });
        
        const item = document.createElement('div');
        item.className = 'file-item';
        item.innerHTML = `<span>📄</span> ${file.name}`;
        elements.filesList.appendChild(item);

    } catch (err) {
        console.error(err);
        appendMessage(`Failed to parse ${file.name}`, 'ai');
    }
}

// 3. UI Interactions
function appendMessage(text, role) {
    const div = document.createElement('div');
    div.className = `message ${role}`;
    const avatar = role === 'user' ? 'U' : 'AI';
    div.innerHTML = `
        <div class="avatar ${role}-avatar">${avatar}</div>
        <div class="content">${marked.parse(text)}</div>
    `;
    elements.chat.appendChild(div);
    elements.chat.scrollTop = elements.chat.scrollHeight;
    div.querySelectorAll('pre code').forEach(el => hljs.highlightElement(el));
}

function showThinking() {
    const div = document.createElement('div');
    div.id = 'thinking';
    div.className = 'message ai';
    div.innerHTML = `
        <div class="avatar ai-avatar">AI</div>
        <div class="content"><div class="thinking"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div></div>
    `;
    elements.chat.appendChild(div);
}

function removeThinking() {
    const el = document.getElementById('thinking');
    if (el) el.remove();
}

async function handleChat() {
    const query = elements.input.value.trim();
    if (!query || !isReady) return;

    appendMessage(query, 'user');
    history.push({ role: 'user', content: query });
    elements.input.value = '';
    showThinking();

    aiWorker.postMessage({ 
        type: 'query', 
        data: { query, vectorStore, history: history.slice(-5) } 
    });
}

// Events
elements.sendBtn.onclick = handleChat;
elements.input.onkeydown = (e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleChat());
elements.dropZone.onclick = () => elements.fileInput.click();
elements.fileInput.onchange = (e) => Array.from(e.target.files).forEach(parseFile);
elements.clearBtn.onclick = () => {
    vectorStore = [];
    history = [];
    elements.filesList.innerHTML = '';
    elements.chat.innerHTML = '';
    appendMessage("Workspace cleared.", "ai");
};

// Drag & Drop
elements.dropZone.ondragover = (e) => (e.preventDefault(), elements.dropZone.style.background = '#EFF6FF');
elements.dropZone.ondragleave = () => elements.dropZone.style.background = '#F1F5F9';
elements.dropZone.ondrop = (e) => {
    e.preventDefault();
    elements.dropZone.style.background = '#F1F5F9';
    Array.from(e.dataTransfer.files).forEach(parseFile);
};
