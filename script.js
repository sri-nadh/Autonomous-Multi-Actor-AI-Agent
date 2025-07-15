// Configuration
const API_BASE_URL = 'http://localhost:8000';
const AGENT_MAPPING = {
    'web_researcher': 'web-badge',
    'rag': 'rag-badge',
    'nl2sql': 'sql-badge'
};

// Global state
let currentSessionId = null;
let isLoading = false;

// DOM elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const messageForm = document.getElementById('messageForm');
const typingIndicator = document.getElementById('typingIndicator');
const sessionIdDisplay = document.getElementById('sessionId');
const clearChatBtn = document.getElementById('clearChat');
const loadingOverlay = document.getElementById('loadingOverlay');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Event listeners
    messageForm.addEventListener('submit', handleSubmit);
    clearChatBtn.addEventListener('click', clearChat);
    messageInput.addEventListener('keypress', handleKeyPress);
    messageInput.addEventListener('input', handleInputChange);
    
    // Focus on input
    messageInput.focus();
    
    // Initialize session
    generateNewSession();
    
    console.log('Multi-Agent Chat initialized');
}

function generateNewSession() {
    currentSessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    sessionIdDisplay.textContent = currentSessionId;
    console.log('New session created:', currentSessionId);
}

function handleSubmit(e) {
    e.preventDefault();
    const message = messageInput.value.trim();
    
    if (message && !isLoading) {
        sendMessage(message);
    }
}

function handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit(e);
    }
}

function handleInputChange() {
    const message = messageInput.value.trim();
    sendButton.disabled = !message || isLoading;
}

async function sendMessage(message) {
    if (isLoading) return;
    
    try {
        setLoading(true);
        
        // Add user message to chat
        addMessage('user', message);
        
        // Clear input
        messageInput.value = '';
        sendButton.disabled = true;
        
        // Show typing indicator
        showTypingIndicator();
        
        // Send message to API
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: currentSessionId
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Update session ID if changed
        if (data.session_id !== currentSessionId) {
            currentSessionId = data.session_id;
            sessionIdDisplay.textContent = currentSessionId;
        }
        
        // Highlight active agents
        highlightActiveAgents(data.agents_used);
        
        // Add assistant response
        addMessage('assistant', data.response, data.agents_used, data.timestamp);
        
    } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();
        
        // Show error message
        addMessage('assistant', 
            'Sorry, I encountered an error while processing your message. Please check if the server is running and try again.',
            [],
            new Date().toISOString(),
            true
        );
    } finally {
        setLoading(false);
        messageInput.focus();
    }
}

function addMessage(role, content, agentsUsed = [], timestamp = null, isError = false) {
    // Remove welcome message if it exists
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    if (isError) {
        bubble.style.background = '#fee';
        bubble.style.borderColor = '#fcc';
        bubble.style.color = '#c33';
    }
    bubble.textContent = content;
    
    messageContent.appendChild(bubble);
    
    // Add metadata for assistant messages
    if (role === 'assistant') {
        const meta = document.createElement('div');
        meta.className = 'message-meta';
        
        const time = document.createElement('span');
        time.textContent = formatTime(timestamp || new Date().toISOString());
        meta.appendChild(time);
        
        if (agentsUsed && agentsUsed.length > 0) {
            const agentsContainer = document.createElement('div');
            agentsContainer.className = 'agents-used';
            
            agentsUsed.forEach(agent => {
                const agentTag = document.createElement('span');
                agentTag.className = 'agent-tag';
                agentTag.textContent = formatAgentName(agent);
                agentsContainer.appendChild(agentTag);
            });
            
            meta.appendChild(agentsContainer);
        }
        
        messageContent.appendChild(meta);
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function formatTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function formatAgentName(agent) {
    const agentNames = {
        'web_researcher': 'Web Search',
        'rag': 'Knowledge Base',
        'nl2sql': 'SQL Query'
    };
    return agentNames[agent] || agent;
}

function highlightActiveAgents(agentsUsed) {
    // Reset all agent badges
    Object.values(AGENT_MAPPING).forEach(badgeId => {
        const badge = document.getElementById(badgeId);
        if (badge) {
            badge.classList.remove('active');
        }
    });
    
    // Highlight active agents
    agentsUsed.forEach(agent => {
        const badgeId = AGENT_MAPPING[agent];
        if (badgeId) {
            const badge = document.getElementById(badgeId);
            if (badge) {
                badge.classList.add('active');
            }
        }
    });
    
    // Remove highlighting after 3 seconds
    setTimeout(() => {
        Object.values(AGENT_MAPPING).forEach(badgeId => {
            const badge = document.getElementById(badgeId);
            if (badge) {
                badge.classList.remove('active');
            }
        });
    }, 3000);
}

function showTypingIndicator() {
    typingIndicator.classList.add('show');
    scrollToBottom();
}

function hideTypingIndicator() {
    typingIndicator.classList.remove('show');
}

function setLoading(loading) {
    isLoading = loading;
    sendButton.disabled = loading || !messageInput.value.trim();
    
    if (loading) {
        sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        messageInput.disabled = true;
    } else {
        sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
        messageInput.disabled = false;
    }
}

function scrollToBottom() {
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100);
}

function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        // Clear messages
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-content">
                    <i class="fas fa-sparkles"></i>
                    <h2>Welcome to your Multi-Agent AI Assistant!</h2>
                    <p>I can help you with web searches, knowledge base queries, and SQL operations. Just ask me anything!</p>
                </div>
            </div>
        `;
        
        // Generate new session
        generateNewSession();
        
        // Reset UI
        hideTypingIndicator();
        messageInput.value = '';
        messageInput.focus();
        
        console.log('Chat cleared');
    }
}

// Utility functions
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #dc3545;
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 1001;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    successDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 1001;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

// Handle connection errors
window.addEventListener('online', () => {
    showSuccess('Connection restored');
});

window.addEventListener('offline', () => {
    showError('Connection lost. Please check your internet connection.');
});

// Handle visibility change (tab switching)
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        messageInput.focus();
    }
});

// Auto-resize input (if needed for multi-line support in future)
function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + L to clear chat
    if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
        e.preventDefault();
        clearChat();
    }
    
    // Escape to focus input
    if (e.key === 'Escape') {
        messageInput.focus();
    }
});

console.log('Multi-Agent Chat UI loaded successfully');