/**
 * DIT 2026 — Chat interface logic.
 * Handles conversation with LLM provider via RAG.
 * Supports dynamic model selection and reasoning/thinking controls.
 */

(function() {
    'use strict';

    const messagesEl = document.getElementById('chatMessages');
    const inputEl = document.getElementById('chatInput');
    const formEl = document.getElementById('chatForm');
    const sendBtn = document.getElementById('sendBtn');
    const providerSelect = document.getElementById('providerSelect');
    const modelSelect = document.getElementById('modelSelect');
    const reasoningSelect = document.getElementById('reasoningSelect');
    const reasoningGroup = document.getElementById('reasoningGroup');
    const reasoningLabel = document.getElementById('reasoningLabel');
    const metaEl = document.getElementById('chatMeta');
    const suggestionsEl = document.getElementById('suggestions');

    let conversationHistory = [];
    let isLoading = false;
    let modelCatalog = {};  // {model_id: {provider, label, reasoning_param, ...}}
    let providerDefaults = {};  // {provider_name: default_model_id}

    // ---- Model Catalog ----

    async function refreshModels() {
        try {
            const resp = await fetch('/api/models');
            const data = await resp.json();
            modelCatalog = data.models || {};
            onProviderChange();
        } catch (e) {
            console.error('Failed to load model catalog:', e);
        }
    }

    function onProviderChange() {
        const provider = providerSelect.value;
        const models = Object.entries(modelCatalog).filter(
            ([_, info]) => info.provider === provider
        );

        modelSelect.innerHTML = '';
        if (models.length === 0) {
            const opt = document.createElement('option');
            opt.value = '';
            opt.textContent = 'No models available';
            modelSelect.appendChild(opt);
        } else {
            models.forEach(([id, info]) => {
                const opt = document.createElement('option');
                opt.value = id;
                opt.textContent = `${info.label}`;
                if (info.description) opt.title = info.description;
                modelSelect.appendChild(opt);
            });
            // Select provider's default model
            const defaultModel = providerDefaults[provider];
            if (defaultModel) modelSelect.value = defaultModel;
        }
        onModelChange();
    }

    function onModelChange() {
        const modelId = modelSelect.value;
        const info = modelCatalog[modelId];

        if (!info || !info.reasoning_param) {
            reasoningGroup.style.display = 'none';
            return;
        }

        reasoningGroup.style.display = '';

        // Set label based on param type
        const paramType = info.reasoning_param;
        if (paramType === 'effort') {
            reasoningLabel.textContent = 'Reasoning';
        } else if (paramType === 'thinking' || paramType === 'thinking_budget') {
            reasoningLabel.textContent = 'Thinking';
        } else if (paramType === 'thinking_level') {
            reasoningLabel.textContent = 'Think Level';
        } else {
            reasoningLabel.textContent = 'Reasoning';
        }

        // Populate options
        const options = info.reasoning_options || [];
        const labels = info.reasoning_labels || {};
        const defaultVal = info.reasoning_default;

        reasoningSelect.innerHTML = '';
        options.forEach(val => {
            const opt = document.createElement('option');
            opt.value = val;
            opt.textContent = labels[val] || val.charAt(0).toUpperCase() + val.slice(1);
            if (val === defaultVal) opt.selected = true;
            reasoningSelect.appendChild(opt);
        });
    }

    const simpleMode = !providerSelect;

    if (!simpleMode) {
        providerSelect.addEventListener('change', onProviderChange);
        modelSelect.addEventListener('change', onModelChange);
    }

    // ---- Message Rendering ----

    function addMessage(role, content) {
        const div = document.createElement('div');
        div.className = `message ${role}`;
        div.setAttribute('role', 'article');
        div.setAttribute('aria-label', (role === 'user' ? 'You' : 'Assistant') + ' message');

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = formatMarkdown(content);

        div.appendChild(contentDiv);
        messagesEl.appendChild(div);

        if (role === 'user') {
            messagesEl.scrollTop = messagesEl.scrollHeight;
        } else {
            const offset = Math.max(0, div.offsetTop - 12);
            messagesEl.scrollTo({ top: offset, behavior: 'smooth' });
        }
    }

    function addTypingIndicator() {
        const div = document.createElement('div');
        div.className = 'message assistant';
        div.id = 'typingIndicator';
        div.setAttribute('role', 'status');
        div.setAttribute('aria-label', 'Assistant is typing');
        div.setAttribute('aria-live', 'polite');
        div.innerHTML = `
            <div class="message-content">
                <div class="typing-indicator" aria-hidden="true">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
                <span class="sr-only">Generating response...</span>
            </div>
        `;
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function removeTypingIndicator() {
        const el = document.getElementById('typingIndicator');
        if (el) el.remove();
    }

    function formatMarkdown(text) {
        const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        const inline = (s) => {
            return esc(s)
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/`(.*?)`/g, '<code>$1</code>');
        };
        const lines = text.split('\n');
        const out = [];
        let inTable = false, headerDone = false;
        let listType = null;

        function closeList() {
            if (listType) { out.push('</' + listType + '>'); listType = null; }
        }

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];

            // Table rows
            if (line.trim().startsWith('|')) {
                closeList();
                const cells = line.split('|').slice(1, -1).map(c => c.trim());
                if (cells.every(c => /^[-:\s]+$/.test(c))) { headerDone = true; continue; }
                if (!inTable) { out.push('<table class="chunk-table">'); inTable = true; headerDone = false; }
                if (!headerDone) {
                    out.push('<thead><tr>' + cells.map(c => `<th>${esc(c)}</th>`).join('') + '</tr></thead><tbody>');
                } else {
                    out.push('<tr>' + cells.map(c => `<td>${esc(c)}</td>`).join('') + '</tr>');
                }
                continue;
            }
            if (inTable) { out.push('</tbody></table>'); inTable = false; headerDone = false; }

            if (line.trim() === '') { closeList(); out.push('<br>'); continue; }

            const ulMatch = line.match(/^(\s*)[-*]\s+(.*)/);
            if (ulMatch) {
                if (listType !== 'ul') { closeList(); out.push('<ul>'); listType = 'ul'; }
                out.push('<li>' + inline(ulMatch[2]) + '</li>');
                continue;
            }

            const olMatch = line.match(/^(\s*)\d+\.\s+(.*)/);
            if (olMatch) {
                if (listType !== 'ol') { closeList(); out.push('<ol>'); listType = 'ol'; }
                out.push('<li>' + inline(olMatch[2]) + '</li>');
                continue;
            }

            closeList();
            out.push('<p>' + inline(line) + '</p>');
        }
        closeList();
        if (inTable) out.push('</tbody></table>');

        return out.join('\n');
    }

    function showMeta(data) {
        const parts = [];
        if (data.provider) parts.push(`Provider: ${data.provider}`);
        if (data.model) parts.push(`Model: ${data.model}`);
        if (data.latency_ms) parts.push(`${Math.round(data.latency_ms)}ms`);
        if (data.input_tokens && data.output_tokens) {
            parts.push(`${data.input_tokens}+${data.output_tokens} tok`);
        }
        if (data.usage && data.usage.budget) {
            const pct = Math.round((data.usage.tokens_used / data.usage.budget) * 100);
            parts.push(`Daily: ${pct}%`);
        }
        metaEl.textContent = parts.join(' | ');
    }

    function showSources(sources) {
        if (!sources || sources.length === 0) return;
        const panel = document.getElementById('sourcesPanel');
        const list = document.getElementById('sourcesList');
        list.innerHTML = sources.map(s =>
            `<div style="margin-bottom: 0.25rem;">${s.file} &mdash; ${s.section}</div>`
        ).join('');
        panel.style.display = 'block';
    }

    // ---- Sending Messages ----

    async function sendMessage(text) {
        if (isLoading || !text.trim()) return;

        isLoading = true;
        sendBtn.disabled = true;
        sendBtn.setAttribute('aria-busy', 'true');
        inputEl.disabled = true;

        suggestionsEl.style.display = 'none';
        addMessage('user', text);
        conversationHistory.push({role: 'user', content: text});
        addTypingIndicator();

        // Build request body with model + reasoning
        const body = {
            message: text,
            provider: simpleMode ? 'auto' : providerSelect.value,
            model: simpleMode ? undefined : (modelSelect.value || undefined),
            history: conversationHistory.slice(-10),
        };
        // Include reasoning value if the control is visible
        if (!simpleMode && reasoningGroup && reasoningGroup.style.display !== 'none' && reasoningSelect.value) {
            body.reasoning = reasoningSelect.value;
        }

        try {
            const resp = await fetch('/chat/api/message', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body),
            });

            removeTypingIndicator();

            if (!resp.ok) {
                const err = await resp.json().catch(() => ({error: 'Unknown error'}));
                addMessage('assistant', `Error: ${err.error || resp.statusText}. Please try again.`);
                return;
            }

            const data = await resp.json();

            addMessage('assistant', data.response);
            conversationHistory.push({role: 'assistant', content: data.response});

            showMeta(data);

        } catch (e) {
            removeTypingIndicator();
            addMessage('assistant', `Connection error: ${e.message}. Please check the server is running.`);
        } finally {
            isLoading = false;
            sendBtn.disabled = false;
            sendBtn.removeAttribute('aria-busy');
            inputEl.disabled = false;
            inputEl.focus();
        }
    }

    // ---- Event Handlers ----

    formEl.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = inputEl.value.trim();
        if (text) {
            inputEl.value = '';
            sendMessage(text);
        }
    });

    document.querySelectorAll('.suggestion').forEach(btn => {
        btn.addEventListener('click', () => {
            const q = btn.dataset.q;
            if (q) sendMessage(q);
        });
    });

    // Refresh provider dropdown from server (picks up keys added in Settings)
    function refreshProviders() {
        fetch('/api/providers')
            .then(r => r.json())
            .then(data => {
                const current = providerSelect.value;
                providerSelect.innerHTML = '';
                let hasAvailable = false;
                data.providers.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p.name;
                    opt.textContent = p.name.charAt(0).toUpperCase() + p.name.slice(1);
                    opt.disabled = !p.available;
                    if (!p.available) opt.textContent += ' — unavailable';
                    providerSelect.appendChild(opt);
                    if (p.available) hasAvailable = true;
                    if (p.model) providerDefaults[p.name] = p.model;
                });
                // Restore selection if still available
                if (current) providerSelect.value = current;
                // Auto-select first available
                if (providerSelect.selectedOptions[0] && providerSelect.selectedOptions[0].disabled) {
                    const first = [...providerSelect.options].find(o => !o.disabled);
                    if (first) providerSelect.value = first.value;
                }
                // Hide warning if providers now available
                const warning = document.querySelector('.alert-warning');
                if (warning && hasAvailable) warning.style.display = 'none';
            })
            .catch(() => {});
    }

    // Initialize: load providers, then models (skip in simple mode)
    if (!simpleMode) {
        refreshProviders();
        refreshModels();
    }

    if (inputEl) inputEl.focus();

})();
