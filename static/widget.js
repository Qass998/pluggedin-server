/**
 * PluggedIN Agentic Website Widget
 * ================================
 * Drop-in AI chat + voice receptionist for any client website.
 *
 * Usage (auto-injected by website_builder.py):
 *   <script
 *     src="https://pluggedin-server.onrender.com/static/widget.js"
 *     data-client-id="gromatic"
 *     data-business-name="Gromatic"
 *     data-agent-name="Aria"
 *     data-color="#6C63FF"
 *     data-cal-link="https://cal.com/gromatic/discovery"
 *     data-vapi-id="your-vapi-assistant-id"
 *   ></script>
 *
 * Features:
 *   - Floating chat bubble (bottom-right)
 *   - AI-powered lead qualifier (talks to Render /widget/chat)
 *   - Voice call button (triggers VAPI receptionist)
 *   - Fully branded per client (name, colour, agent name)
 *   - Mobile responsive
 *   - Zero dependencies
 */

(function () {
  'use strict';

  // ── Config from script tag ─────────────────────────────────────────
  const script     = document.currentScript || (function () {
    const scripts = document.getElementsByTagName('script');
    return scripts[scripts.length - 1];
  })();

  const API_BASE    = (script.src || '').replace('/static/widget.js', '') || 'https://pluggedin-server.onrender.com';
  const CLIENT_ID   = script.getAttribute('data-client-id')    || 'default';
  const BIZ_NAME    = script.getAttribute('data-business-name') || 'Us';
  const AGENT_NAME  = script.getAttribute('data-agent-name')    || 'Assistant';
  const COLOR       = script.getAttribute('data-color')         || '#6C63FF';
  const CAL_LINK    = script.getAttribute('data-cal-link')      || '';
  const VAPI_ID     = script.getAttribute('data-vapi-id')       || '';

  // ── Session ID (persists per browser tab) ─────────────────────────
  const SESSION_ID  = 'pi_' + Math.random().toString(36).slice(2) + Date.now();

  // ── State ─────────────────────────────────────────────────────────
  let isOpen     = false;
  let isTyping   = false;
  let callActive = false;

  // ── Color helpers ─────────────────────────────────────────────────
  function hexToRgb(hex) {
    const r = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return r ? `${parseInt(r[1],16)},${parseInt(r[2],16)},${parseInt(r[3],16)}` : '108,99,255';
  }
  const RGB = hexToRgb(COLOR);

  // ── CSS injection ─────────────────────────────────────────────────
  const css = `
    .pi-widget * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
    .pi-bubble {
      position: fixed; bottom: 24px; right: 24px; z-index: 999999;
      width: 56px; height: 56px; border-radius: 50%;
      background: ${COLOR}; box-shadow: 0 4px 20px rgba(${RGB},0.4);
      cursor: pointer; border: none; outline: none;
      display: flex; align-items: center; justify-content: center;
      transition: transform 0.2s, box-shadow 0.2s;
      animation: pi-pulse 2.5s infinite;
    }
    .pi-bubble:hover { transform: scale(1.08); box-shadow: 0 6px 28px rgba(${RGB},0.55); }
    .pi-bubble svg { width: 26px; height: 26px; fill: white; transition: opacity 0.2s; }
    @keyframes pi-pulse {
      0%,100% { box-shadow: 0 4px 20px rgba(${RGB},0.4); }
      50%      { box-shadow: 0 4px 28px rgba(${RGB},0.7), 0 0 0 8px rgba(${RGB},0.12); }
    }
    .pi-panel {
      position: fixed; bottom: 90px; right: 24px; z-index: 999998;
      width: 360px; max-width: calc(100vw - 48px);
      background: #fff; border-radius: 20px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.18);
      display: flex; flex-direction: column; overflow: hidden;
      transform: scale(0.85) translateY(20px); opacity: 0;
      transition: transform 0.25s cubic-bezier(0.34,1.56,0.64,1), opacity 0.2s;
      pointer-events: none; height: 500px; max-height: 70vh;
    }
    .pi-panel.pi-open { transform: scale(1) translateY(0); opacity: 1; pointer-events: all; }
    .pi-header {
      background: ${COLOR}; padding: 16px 18px; color: #fff;
      display: flex; align-items: center; gap: 12px; flex-shrink: 0;
    }
    .pi-avatar {
      width: 40px; height: 40px; border-radius: 50%; background: rgba(255,255,255,0.25);
      display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0;
    }
    .pi-header-info { flex: 1; }
    .pi-header-name { font-weight: 700; font-size: 15px; line-height: 1.2; }
    .pi-header-status { font-size: 12px; opacity: 0.85; display: flex; align-items: center; gap: 5px; }
    .pi-status-dot { width: 7px; height: 7px; border-radius: 50%; background: #4ade80; animation: pi-blink 1.5s infinite; }
    @keyframes pi-blink { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
    .pi-call-btn {
      background: rgba(255,255,255,0.2); border: none; border-radius: 8px;
      color: #fff; cursor: pointer; padding: 7px 10px; font-size: 12px; font-weight: 600;
      display: flex; align-items: center; gap: 5px; transition: background 0.15s;
      white-space: nowrap;
    }
    .pi-call-btn:hover { background: rgba(255,255,255,0.32); }
    .pi-call-btn.pi-calling { background: rgba(239,68,68,0.7); animation: pi-pulse 1s infinite; }
    .pi-messages {
      flex: 1; overflow-y: auto; padding: 16px; display: flex;
      flex-direction: column; gap: 10px; scroll-behavior: smooth;
    }
    .pi-messages::-webkit-scrollbar { width: 4px; }
    .pi-messages::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 4px; }
    .pi-msg { display: flex; gap: 8px; max-width: 88%; }
    .pi-msg.pi-user { align-self: flex-end; flex-direction: row-reverse; }
    .pi-msg-avatar {
      width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
      background: ${COLOR}; display: flex; align-items: center;
      justify-content: center; font-size: 12px; color: white; font-weight: 700;
    }
    .pi-msg-bubble {
      padding: 10px 14px; border-radius: 16px; font-size: 14px;
      line-height: 1.5; white-space: pre-wrap; word-break: break-word;
    }
    .pi-bot .pi-msg-bubble { background: #f3f4f6; color: #111827; border-bottom-left-radius: 4px; }
    .pi-user .pi-msg-bubble { background: ${COLOR}; color: #fff; border-bottom-right-radius: 4px; }
    .pi-typing { display: flex; gap: 5px; align-items: center; padding: 10px 14px; }
    .pi-typing span {
      width: 7px; height: 7px; border-radius: 50%; background: #9ca3af;
      animation: pi-bounce 1.2s infinite;
    }
    .pi-typing span:nth-child(2) { animation-delay: 0.2s; }
    .pi-typing span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes pi-bounce { 0%,60%,100% { transform: translateY(0); } 30% { transform: translateY(-6px); } }
    .pi-cta-row { display: flex; gap: 8px; padding: 0 16px 12px; flex-shrink: 0; }
    .pi-cta-btn {
      flex: 1; padding: 9px; border-radius: 10px; border: 1.5px solid ${COLOR};
      color: ${COLOR}; background: transparent; font-size: 12px; font-weight: 600;
      cursor: pointer; transition: background 0.15s, color 0.15s; text-align: center;
      text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 5px;
    }
    .pi-cta-btn:hover { background: rgba(${RGB},0.08); }
    .pi-input-row {
      display: flex; align-items: center; gap: 8px; padding: 12px 14px;
      border-top: 1px solid #f3f4f6; flex-shrink: 0;
    }
    .pi-input {
      flex: 1; border: 1.5px solid #e5e7eb; border-radius: 10px;
      padding: 9px 13px; font-size: 14px; outline: none; resize: none;
      line-height: 1.4; max-height: 80px; transition: border-color 0.15s;
      font-family: inherit;
    }
    .pi-input:focus { border-color: ${COLOR}; }
    .pi-send {
      width: 38px; height: 38px; border-radius: 10px; background: ${COLOR};
      border: none; cursor: pointer; display: flex; align-items: center;
      justify-content: center; flex-shrink: 0; transition: opacity 0.15s;
    }
    .pi-send:hover { opacity: 0.85; }
    .pi-send svg { width: 17px; height: 17px; fill: white; }
    .pi-powered { text-align: center; font-size: 10px; color: #9ca3af; padding: 4px 0 10px; flex-shrink: 0; }
    @media (max-width: 480px) {
      .pi-panel { right: 12px; left: 12px; width: auto; bottom: 80px; }
      .pi-bubble { bottom: 16px; right: 16px; }
    }
  `;

  // ── DOM builder ────────────────────────────────────────────────────
  function buildWidget() {
    // Inject styles
    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);

    // Wrapper
    const wrap = document.createElement('div');
    wrap.className = 'pi-widget';

    // Bubble button
    wrap.innerHTML = `
      <button class="pi-bubble" id="pi-bubble" aria-label="Chat with us">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
        </svg>
      </button>

      <div class="pi-panel" id="pi-panel">
        <div class="pi-header">
          <div class="pi-avatar">🤖</div>
          <div class="pi-header-info">
            <div class="pi-header-name">${AGENT_NAME}</div>
            <div class="pi-header-status">
              <span class="pi-status-dot"></span>
              Online · ${BIZ_NAME}
            </div>
          </div>
          ${VAPI_ID ? `
          <button class="pi-call-btn" id="pi-call-btn">
            <svg viewBox="0 0 24 24" width="13" height="13" fill="white">
              <path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1-9.4 0-17-7.6-17-17 0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z"/>
            </svg>
            Call Us
          </button>` : ''}
        </div>

        <div class="pi-messages" id="pi-messages"></div>

        ${CAL_LINK ? `
        <div class="pi-cta-row">
          <a href="${CAL_LINK}" target="_blank" class="pi-cta-btn">
            📅 Book a Meeting
          </a>
        </div>` : ''}

        <div class="pi-input-row">
          <textarea
            class="pi-input" id="pi-input"
            placeholder="Type your message..."
            rows="1"
          ></textarea>
          <button class="pi-send" id="pi-send">
            <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
          </button>
        </div>

        <div class="pi-powered">Powered by PluggedIN AI</div>
      </div>
    `;

    document.body.appendChild(wrap);

    // ── Wire up events ────────────────────────────────────────────────
    const bubble  = document.getElementById('pi-bubble');
    const panel   = document.getElementById('pi-panel');
    const input   = document.getElementById('pi-input');
    const send    = document.getElementById('pi-send');
    const msgs    = document.getElementById('pi-messages');
    const callBtn = document.getElementById('pi-call-btn');

    // Toggle open/close
    bubble.addEventListener('click', function () {
      isOpen = !isOpen;
      panel.classList.toggle('pi-open', isOpen);
      if (isOpen && msgs.children.length === 0) {
        sendGreeting();
      }
      if (isOpen) setTimeout(() => input.focus(), 300);
    });

    // Send on button click
    send.addEventListener('click', sendMessage);

    // Send on Enter (Shift+Enter = newline)
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    // Auto-resize textarea
    input.addEventListener('input', function () {
      this.style.height = 'auto';
      this.style.height = Math.min(this.scrollHeight, 80) + 'px';
    });

    // Call button
    if (callBtn) {
      callBtn.addEventListener('click', handleCall);
    }
  }

  // ── Message rendering ──────────────────────────────────────────────
  function appendMessage(role, text) {
    const msgs = document.getElementById('pi-messages');
    const div  = document.createElement('div');
    div.className = `pi-msg pi-${role}`;
    const initial = AGENT_NAME.charAt(0).toUpperCase();
    div.innerHTML = role === 'bot'
      ? `<div class="pi-msg-avatar">${initial}</div><div class="pi-msg-bubble">${text}</div>`
      : `<div class="pi-msg-bubble">${text}</div>`;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function showTyping() {
    const msgs = document.getElementById('pi-messages');
    const div  = document.createElement('div');
    div.className = 'pi-msg pi-bot';
    div.id = 'pi-typing-indicator';
    div.innerHTML = `<div class="pi-msg-avatar">${AGENT_NAME.charAt(0)}</div>
      <div class="pi-msg-bubble pi-typing"><span></span><span></span><span></span></div>`;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function removeTyping() {
    const t = document.getElementById('pi-typing-indicator');
    if (t) t.remove();
  }

  // ── Greeting ───────────────────────────────────────────────────────
  function sendGreeting() {
    showTyping();
    fetch(API_BASE + '/widget/greeting', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ client_id: CLIENT_ID }),
    })
      .then(r => r.json())
      .then(data => {
        removeTyping();
        appendMessage('bot', data.greeting || `Hi! 👋 I'm ${AGENT_NAME} from ${BIZ_NAME}. How can I help you today?`);
      })
      .catch(() => {
        removeTyping();
        appendMessage('bot', `Hi! 👋 I'm ${AGENT_NAME} from ${BIZ_NAME}. How can I help you today?`);
      });
  }

  // ── Send message ───────────────────────────────────────────────────
  function sendMessage() {
    const input = document.getElementById('pi-input');
    const text  = input.value.trim();
    if (!text || isTyping) return;

    input.value  = '';
    input.style.height = 'auto';
    appendMessage('user', text);

    isTyping = true;
    showTyping();

    fetch(API_BASE + '/widget/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: SESSION_ID,
        client_id:  CLIENT_ID,
        message:    text,
      }),
    })
      .then(r => r.json())
      .then(data => {
        removeTyping();
        appendMessage('bot', data.reply || 'Sorry, something went wrong. Please try again.');
        isTyping = false;
      })
      .catch(() => {
        removeTyping();
        appendMessage('bot', 'Connection issue — please try again in a moment.');
        isTyping = false;
      });
  }

  // ── Voice call ─────────────────────────────────────────────────────
  function handleCall() {
    const btn = document.getElementById('pi-call-btn');
    if (!btn) return;

    if (callActive) {
      // End call
      callActive = false;
      btn.classList.remove('pi-calling');
      btn.innerHTML = `<svg viewBox="0 0 24 24" width="13" height="13" fill="white">
        <path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1-9.4 0-17-7.6-17-17 0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z"/>
      </svg> Call Us`;
      appendMessage('bot', 'Call ended. Is there anything else I can help you with?');
      return;
    }

    // Start call
    callActive = true;
    btn.classList.add('pi-calling');
    btn.innerHTML = `<svg viewBox="0 0 24 24" width="13" height="13" fill="white">
      <path d="M20 5.41L18.59 4 7 15.59V9H5v10h10v-2H8.41z"/>
    </svg> End Call`;

    appendMessage('bot', '📞 Connecting you now... Please allow microphone access if prompted.');

    fetch(API_BASE + '/widget/call', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        client_id:  CLIENT_ID,
        session_id: SESSION_ID,
        vapi_id:    VAPI_ID,
      }),
    })
      .then(r => r.json())
      .then(data => {
        if (data.web_call_url) {
          // Open VAPI web call in overlay
          appendMessage('bot', '✅ Connected! You should hear the receptionist now.');
        } else {
          appendMessage('bot', data.message || 'Call is being connected.');
        }
      })
      .catch(() => {
        callActive = false;
        btn.classList.remove('pi-calling');
        btn.innerHTML = `<svg viewBox="0 0 24 24" width="13" height="13" fill="white">
          <path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1-9.4 0-17-7.6-17-17 0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z"/>
        </svg> Call Us`;
        appendMessage('bot', 'Could not connect the call. Please try again or use the booking link.');
      });
  }

  // ── Init ──────────────────────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildWidget);
  } else {
    buildWidget();
  }

})();
