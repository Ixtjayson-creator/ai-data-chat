// script.js - Defensive Browser Control Center
(function() {
    "use strict";

    function updateStatus(text, type = 'info') {
        const statusText = document.getElementById('status-text');
        if (statusText) {
            statusText.innerText = text;
            statusText.style.color = type === 'error' ? '#EF4444' : '#64748B';
        }
    }

    try {
        if (!window.Worker) {
            throw new Error("Web Workers are not supported in this browser.");
        }

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

        const aiWorker = new Worker('worker.js', { type: 'module' });
        let vectorStore = [];
        let history = [];
        let isReady = false;

        // Ensure input is interactive immediately
        if (elements.input) {
            elements.input.disabled = false;
            elements.input.style.cursor = 'text';
            elements.input.placeholder = "Engine initializing... but you can type now";
        }

        // 1. Worker Handlers
        aiWorker.onmessage = (e) => {
            const { status, message, progress, embeddings, answer } = e.data;

            if (status === 'loading') {
                updateStatus(message);
                if (elements.progressBar) elements.progressBar.style.display = 'block';
                if (elements.progress) elements.progress.style.width = '10%';
            }

            if (status === 'info') {
                updateStatus(message);
                console.info("AI Engine Info:", message);
            }

            if (status === 'ready') {
                isReady = true;
                updateStatus("Local Intelligence Ready");
                if (elements.engineStatus) elements.engineStatus.innerText = "Online";
                if (elements.onlineDot) elements.onlineDot.classList.add('active');
                if (elements.input) {
                    elements.input.placeholder = "Ask about your data...";
                }
                if (elements.sendBtn) elements.sendBtn.disabled = false;
                if (elements.progressBar) elements.progressBar.style.display = 'none';
                appendMessage("System initialised. You can now chat or upload data.", "ai");
            }

            if (status === 'indexing') {
                if (elements.progressBar) elements.progressBar.style.display = 'block';
                if (elements.progress) elements.progress.style.width = `${progress}%`;
                updateStatus(`Indexing: ${progress}%`);
            }

            if (status === 'indexed') {
                vectorStore.push(...embeddings);
                if (elements.progressBar) elements.progressBar.style.display = 'none';
                updateStatus("Document Indexed Successfully");
                appendMessage(`Finished indexing document. I'm ready to answer questions about it.`, 'ai');
            }

            if (status === 'answer') {
                removeThinking();
                appendMessage(answer, 'ai');
                history.push({ role: 'assistant', content: answer });
            }

            if (status === 'error') {
                updateStatus("Initialization Error", 'error');
                if (elements.input) elements.input.placeholder = "AI Engine error. See status bar.";
                appendMessage(`⚠ AI Worker Error: ${message}`, 'ai');
            }
        };

        aiWorker.onerror = (e) => {
            console.error("Worker Error:", e);
            updateStatus("Worker Failed to Initialize", 'error');
            appendMessage("⚠ The AI Worker crashed. Try Chrome or Edge.", "ai");
        };

        // 2. Data Loader
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

                const chunks = text.split(/\n\n+/).filter(c => c.length > 10).map(c => c.trim());
                aiWorker.postMessage({ type: 'embed', data: { chunks, source: file.name } });
                
                if (elements.filesList) {
                    const item = document.createElement('div');
                    item.className = 'file-item';
                    item.innerHTML = `<span>📄</span> ${file.name}`;
                    elements.filesList.appendChild(item);
                }

            } catch (err) {
                console.error(err);
                appendMessage(`Failed to parse ${file.name}`, 'ai');
            }
        }

        // 3. UI Interactions
        function appendMessage(text, role) {
            if (!elements.chat) return;
            const div = document.createElement('div');
            div.className = `message ${role}`;
            const avatar = role === 'user' ? 'U' : 'AI';
            div.innerHTML = `
                <div class="avatar ${role}-avatar">${avatar}</div>
                <div class="content">${typeof marked !== 'undefined' ? marked.parse(text) : text}</div>
            `;
            elements.chat.appendChild(div);
            elements.chat.scrollTop = elements.chat.scrollHeight;
            if (typeof hljs !== 'undefined') {
                div.querySelectorAll('pre code').forEach(el => hljs.highlightElement(el));
            }
        }

        function showThinking() {
            if (!elements.chat) return;
            const div = document.createElement('div');
            div.id = 'thinking';
            div.className = 'message ai';
            div.innerHTML = `
                <div class="avatar ai-avatar">AI</div>
                <div class="content"><div class="thinking"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div></div>
            `;
            elements.chat.appendChild(div);
            elements.chat.scrollTop = elements.chat.scrollHeight;
        }

        function removeThinking() {
            const el = document.getElementById('thinking');
            if (el) el.remove();
        }

        async function handleChat() {
            if (!elements.input) return;
            const query = elements.input.value.trim();
            if (!query) return;

            if (!isReady) {
                appendMessage("AI engine is still starting up. Please wait...", "ai");
                return;
            }

            appendMessage(query, 'user');
            history.push({ role: 'user', content: query });
            elements.input.value = '';
            elements.input.style.height = 'auto'; 
            showThinking();

            aiWorker.postMessage({ 
                type: 'query', 
                data: { query, vectorStore, history: history.slice(-5) } 
            });
        }

        // Events
        if (elements.sendBtn) elements.sendBtn.onclick = handleChat;
        if (elements.input) {
            elements.input.oninput = function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
            };
            elements.input.onkeydown = (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleChat();
                }
            };
        }

        if (elements.dropZone) elements.dropZone.onclick = () => elements.fileInput && elements.fileInput.click();
        if (elements.fileInput) elements.fileInput.onchange = (e) => Array.from(e.target.files).forEach(parseFile);
        if (elements.clearBtn) elements.clearBtn.onclick = () => {
            vectorStore = [];
            history = [];
            if (elements.filesList) elements.filesList.innerHTML = '';
            if (elements.chat) elements.chat.innerHTML = '';
            appendMessage("Workspace cleared.", "ai");
        };

        // Drag & Drop
        if (elements.dropZone) {
            elements.dropZone.ondragover = (e) => (e.preventDefault(), elements.dropZone.style.background = '#EFF6FF');
            elements.dropZone.ondragleave = () => elements.dropZone.style.background = '#F1F5F9';
            elements.dropZone.ondrop = (e) => {
                e.preventDefault();
                elements.dropZone.style.background = '#F1F5F9';
                Array.from(e.dataTransfer.files).forEach(parseFile);
            };
        }

        // Trigger init
        aiWorker.postMessage({ type: 'init' });

    } catch (criticalErr) {
        console.error("Script Crash:", criticalErr);
        const statusText = document.getElementById('status-text');
        if (statusText) {
            statusText.innerText = `Script Error: ${criticalErr.message}`;
            statusText.style.color = '#EF4444';
        }
    }
})();
