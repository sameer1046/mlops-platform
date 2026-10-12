from __future__ import annotations

CHAT_UI_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MLOps Platform - AI Gateway Chat</title>
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #38bdf8;
      --primary-hover: #0284c7;
      --user-msg: #0369a1;
      --assistant-msg: #1e293b;
      --badge-bg: #334155;
      --badge-green: #065f46;
      --badge-green-text: #6ee7b7;
      --badge-orange: #7c2d12;
      --badge-orange-text: #fdba74;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
    }
    header {
      background: var(--card-bg);
      border-bottom: 1px solid var(--border);
      padding: 12px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-shrink: 0;
    }
    .header-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .header-title {
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--text);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .header-badge {
      font-size: 0.75rem;
      padding: 3px 8px;
      border-radius: 9999px;
      background: var(--badge-green);
      color: var(--badge-green-text);
      font-weight: 600;
    }
    .header-links {
      display: flex;
      gap: 16px;
      align-items: center;
    }
    .header-link {
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.85rem;
      transition: color 0.15s;
    }
    .header-link:hover {
      color: var(--primary);
    }
    main {
      flex: 1;
      overflow-y: auto;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      max-width: 900px;
      width: 100%;
      margin: 0 auto;
    }
    .welcome-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 12px;
    }
    .welcome-card h2 {
      font-size: 1.1rem;
      margin-bottom: 8px;
      color: var(--primary);
    }
    .welcome-card p {
      font-size: 0.9rem;
      color: var(--text-muted);
      line-height: 1.5;
      margin-bottom: 14px;
    }
    .chips {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .chip {
      background: var(--border);
      border: none;
      color: var(--text);
      padding: 6px 12px;
      border-radius: 9999px;
      font-size: 0.8rem;
      cursor: pointer;
      transition: background 0.15s;
    }
    .chip:hover {
      background: var(--primary);
      color: #0f172a;
    }
    .message {
      display: flex;
      flex-direction: column;
      max-width: 85%;
      gap: 6px;
      animation: fadeIn 0.2s ease-in;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .message.user {
      align-self: flex-end;
    }
    .message.assistant {
      align-self: flex-start;
    }
    .bubble {
      padding: 12px 16px;
      border-radius: 14px;
      font-size: 0.92rem;
      line-height: 1.55;
      word-wrap: break-word;
      white-space: pre-wrap;
    }
    .message.user .bubble {
      background: var(--user-msg);
      color: #ffffff;
      border-bottom-right-radius: 4px;
    }
    .message.assistant .bubble {
      background: var(--assistant-msg);
      color: var(--text);
      border: 1px solid var(--border);
      border-bottom-left-radius: 4px;
    }
    .meta-bar {
      display: flex;
      gap: 8px;
      align-items: center;
      font-size: 0.75rem;
      color: var(--text-muted);
      flex-wrap: wrap;
      padding: 0 4px;
    }
    .meta-tag {
      background: var(--badge-bg);
      padding: 2px 8px;
      border-radius: 6px;
      font-family: monospace;
    }
    .meta-tag.success {
      background: var(--badge-green);
      color: var(--badge-green-text);
    }
    .meta-tag.fallback {
      background: var(--badge-orange);
      color: var(--badge-orange-text);
    }
    .meta-tag a {
      color: inherit;
      text-decoration: underline;
    }
    .loading-bubble {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 14px 18px;
    }
    .dot {
      width: 7px;
      height: 7px;
      background: var(--primary);
      border-radius: 50%;
      animation: bounce 1.4s infinite ease-in-out;
    }
    .dot:nth-child(1) { animation-delay: -0.32s; }
    .dot:nth-child(2) { animation-delay: -0.16s; }
    @keyframes bounce {
      0%, 80%, 100% { transform: scale(0); opacity: 0.4; }
      40% { transform: scale(1); opacity: 1; }
    }
    footer {
      background: var(--card-bg);
      border-top: 1px solid var(--border);
      padding: 16px 24px;
      flex-shrink: 0;
    }
    .input-form {
      max-width: 900px;
      margin: 0 auto;
      display: flex;
      gap: 12px;
      align-items: flex-end;
    }
    textarea {
      flex: 1;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      color: var(--text);
      padding: 12px 14px;
      font-size: 0.95rem;
      font-family: inherit;
      resize: none;
      min-height: 48px;
      max-height: 140px;
      outline: none;
      transition: border-color 0.15s;
    }
    textarea:focus {
      border-color: var(--primary);
    }
    button.send-btn {
      background: var(--primary);
      color: #0f172a;
      border: none;
      border-radius: 10px;
      padding: 12px 20px;
      font-size: 0.95rem;
      font-weight: 700;
      cursor: pointer;
      transition: background 0.15s, opacity 0.15s;
      height: 48px;
    }
    button.send-btn:hover:not(:disabled) {
      background: var(--primary-hover);
    }
    button.send-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  </style>
</head>
<body>
  <header>
    <div class="header-left">
      <div class="header-title">
        <span>⚡</span>
        <span>MLOps AI Gateway</span>
      </div>
      <span class="header-badge" id="model-badge">meta/llama-3.2-11b-vision-instruct</span>
    </div>
    <div class="header-links">
      <a class="header-link" href="http://localhost:5000" target="_blank" rel="noopener">📊 MLflow UI</a>
      <a class="header-link" href="/docs" target="_blank" rel="noopener">📖 OpenAPI Docs</a>
    </div>
  </header>

  <main id="messages">
    <div class="welcome-card" id="welcome-card">
      <h2>Welcome to the MLOps Gateway Chat</h2>
      <p>
        Inference requests submitted here route through the resilient <strong>AI Gateway</strong> to the NVIDIA NIM API with automated provider fallback and real-time <strong>MLflow Tracing</strong>.
      </p>
      <div class="chips">
        <button class="chip" onclick="fillPrompt('Explain MLOps in 2 sentences.')">💡 What is MLOps?</button>
        <button class="chip" onclick="fillPrompt('Compare Blue/Green vs Canary deployment strategies.')">🚀 Deployment Strategies</button>
        <button class="chip" onclick="fillPrompt('How does an LLM AI Gateway improve resilience and cost control?')">🛡️ AI Gateway Benefits</button>
      </div>
    </div>
  </main>

  <footer>
    <form class="input-form" id="chat-form">
      <textarea id="prompt-input" placeholder="Type a message... (Press Enter to send, Shift+Enter for new line)" rows="1"></textarea>
      <button type="submit" class="send-btn" id="send-btn">Send</button>
    </form>
  </footer>

  <script>
    const messagesContainer = document.getElementById('messages');
    const chatForm = document.getElementById('chat-form');
    const promptInput = document.getElementById('prompt-input');
    const sendBtn = document.getElementById('send-btn');
    const welcomeCard = document.getElementById('welcome-card');

    function fillPrompt(text) {
      promptInput.value = text;
      promptInput.focus();
    }

    promptInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
      }
    });

    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const prompt = promptInput.value.trim();
      if (!prompt) return;

      if (welcomeCard) welcomeCard.style.display = 'none';

      appendMessage('user', prompt);
      promptInput.value = '';
      sendBtn.disabled = true;

      const loadingMsg = appendLoading();
      const startTime = performance.now();

      try {
        const res = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tenant_id: 'web-ui',
            prompt: prompt,
            max_tokens: 512,
            temperature: 0.2
          })
        });

        const elapsed = Math.round(performance.now() - startTime);
        loadingMsg.remove();

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          appendMessage('assistant', `⚠️ Error ${res.status}: ${errData.detail || 'Request failed'}`);
          return;
        }

        const data = await res.json();
        appendMessage('assistant', data.completion, {
          provider: data.provider,
          model: data.model_id,
          traceId: data.trace_id,
          fallbackUsed: data.fallback_used,
          latencyMs: elapsed
        });
      } catch (err) {
        loadingMsg.remove();
        appendMessage('assistant', `⚠️ Network error: ${err.message}`);
      } finally {
        sendBtn.disabled = false;
        promptInput.focus();
      }
    });

    function appendMessage(role, text, meta) {
      const msgDiv = document.createElement('div');
      msgDiv.className = `message ${role}`;

      const bubble = document.createElement('div');
      bubble.className = 'bubble';
      bubble.textContent = text;
      msgDiv.appendChild(bubble);

      if (meta) {
        const metaBar = document.createElement('div');
        metaBar.className = 'meta-bar';

        const providerTag = document.createElement('span');
        providerTag.className = `meta-tag ${meta.fallbackUsed ? 'fallback' : 'success'}`;
        providerTag.textContent = meta.fallbackUsed ? 'fallback' : meta.provider;
        metaBar.appendChild(providerTag);

        const modelTag = document.createElement('span');
        modelTag.className = 'meta-tag';
        modelTag.textContent = meta.model;
        metaBar.appendChild(modelTag);

        const timeTag = document.createElement('span');
        timeTag.className = 'meta-tag';
        timeTag.textContent = `${meta.latencyMs}ms`;
        metaBar.appendChild(timeTag);

        const traceTag = document.createElement('span');
        traceTag.className = 'meta-tag';
        traceTag.innerHTML = `trace: <a href="http://localhost:5000" target="_blank">${meta.traceId.slice(0, 8)}...</a>`;
        metaBar.appendChild(traceTag);

        msgDiv.appendChild(metaBar);
      }

      messagesContainer.appendChild(msgDiv);
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
      return msgDiv;
    }

    function appendLoading() {
      const msgDiv = document.createElement('div');
      msgDiv.className = 'message assistant';
      const bubble = document.createElement('div');
      bubble.className = 'bubble loading-bubble';
      bubble.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
      msgDiv.appendChild(bubble);
      messagesContainer.appendChild(msgDiv);
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
      return msgDiv;
    }
  </script>
</body>
</html>
"""
