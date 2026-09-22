document.addEventListener('DOMContentLoaded', () => {
    const chatWindow = document.getElementById('chat-window');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const connStatusBadge = document.getElementById('conn-status');

    let currentStatusMsg = null;
    
    // 🧠 This array acts as the chatbot's memory for the current session
    let chatHistory = []; 

    // --- WebSockets ---
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socket = new WebSocket(`${wsProtocol}//${window.location.host}/ws`);

    socket.onopen = () => {
        connStatusBadge.innerHTML = '<span class="dot green"></span> Connected';
    };

    socket.onclose = () => {
        connStatusBadge.innerHTML = '<span class="dot red"></span> Disconnected';
    };

    // --- UI Helpers ---
    const appendMessage = (sender, text, isStatus = false) => {
        const row = document.createElement('div');
        row.className = `message-row ${sender}`;
        
        let avatarHTML = sender === 'bot' 
            ? `<div class="avatar bot-avatar"><span class="material-symbols-rounded">smart_toy</span></div>` 
            : `<div class="avatar user-avatar">U</div>`;

        const textClass = isStatus ? 'status-text' : '';
        
        // 👇 FIXED: Removed the <p> tags so Markdown headers and lists can render correctly
        row.innerHTML = `
            ${avatarHTML}
            <div class="message-content ${textClass}">
                ${text}
            </div>
        `;

        chatWindow.appendChild(row);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        return row;
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "status") {
            if (currentStatusMsg) currentStatusMsg.remove();
            currentStatusMsg = appendMessage('bot', `🔄 ${data.message}`, true);
        } 
        else if (data.type === "result") {
            if (currentStatusMsg) currentStatusMsg.remove();
            
            // 👇 FIXED: Parse the Markdown into beautiful HTML before showing it
            // (Checks if marked is loaded, otherwise falls back to raw text)
            const formattedHTML = typeof marked !== 'undefined' ? marked.parse(data.result) : data.result;
            appendMessage('bot', formattedHTML);
            
            // Save the raw response to the history
            chatHistory.push({ role: "bot", content: data.result });

            sendBtn.disabled = false;
            sendBtn.innerHTML = '<span class="material-symbols-rounded">send</span>';
            userInput.disabled = false;
            userInput.focus();
        }
        else if (data.type === "error") {
            if (currentStatusMsg) currentStatusMsg.remove();
            appendMessage('bot', `⚠️ Error: ${data.message}`);
            sendBtn.disabled = false;
            userInput.disabled = false;
        }
    };

    const sendMessage = () => {
        const text = userInput.value.trim();
        if (!text) return;

        // Render user message (User messages don't need markdown parsing)
        appendMessage('user', text);
        
        // Save the user's message to the history
        chatHistory.push({ role: "user", content: text });

        userInput.value = '';
        userInput.style.height = 'auto';
        sendBtn.disabled = true;
        
        sendBtn.innerHTML = '<span class="material-symbols-rounded" style="animation: spin 1s linear infinite;">hourglass_empty</span>';
        userInput.disabled = true;

        // Send BOTH the latest prompt AND the conversation history
        socket.send(JSON.stringify({ 
            prompt: text,
            history: chatHistory 
        }));
    };

    userInput.addEventListener('input', () => {
        sendBtn.disabled = userInput.value.trim().length === 0;
        userInput.style.height = 'auto';
        userInput.style.height = (userInput.scrollHeight) + 'px';
    });

    sendBtn.addEventListener('click', sendMessage);

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!sendBtn.disabled) sendMessage();
        }
    });
});