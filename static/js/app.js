// Zypher AI - ChatGPT-Style Interface JavaScript

// State
let currentSettings = {
    use_lora: false,
    num_steps: 4,
    width: 1024,
    height: 1024
};

let conversationHistory = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
    focusInput();
});

// Focus input on load
function focusInput() {
    document.getElementById('promptInput').focus();
}

// Auto-resize textarea
function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

// Handle key press
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Use example prompt
function usePrompt(button) {
    const promptText = button.querySelector('.prompt-text').textContent;
    document.getElementById('promptInput').value = promptText;
    document.getElementById('welcomeScreen').style.display = 'none';
    focusInput();
}

// New chat
function newChat() {
    conversationHistory = [];
    document.getElementById('messages').innerHTML = '';
    document.getElementById('welcomeScreen').style.display = 'flex';
    document.getElementById('promptInput').value = '';
    focusInput();
}

// Send message
async function sendMessage() {
    const input = document.getElementById('promptInput');
    const prompt = input.value.trim();
    
    if (!prompt) return;
    
    // Hide welcome screen
    document.getElementById('welcomeScreen').style.display = 'none';
    
    // Add user message
    addMessage('user', prompt);
    
    // Clear input
    input.value = '';
    input.style.height = 'auto';
    
    // Disable send button
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;
    
    // Show loading
    showLoading();
    
    try {
        // Send request
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: prompt,
                use_lora: currentSettings.use_lora,
                num_steps: currentSettings.num_steps,
                width: currentSettings.width,
                height: currentSettings.height
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Add assistant message with image
            addMessage('assistant', '', data.image, data.metadata, data.filename);
            
            // Add to conversation history
            conversationHistory.push({
                user: prompt,
                assistant: data.filename,
                timestamp: new Date().toISOString()
            });
            
            // Update history list
            updateHistoryList();
        } else {
            addErrorMessage(data.error || 'Generation failed');
        }
    } catch (error) {
        console.error('Error:', error);
        addErrorMessage('Network error. Please check your connection and try again.');
    } finally {
        hideLoading();
        sendBtn.disabled = false;
        focusInput();
    }
}

// Add message to chat
function addMessage(role, text, imageUrl = null, metadata = null, filename = null) {
    const messages = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatar = role === 'user' ? '👤' : '🎨';
    
    let messageHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
    `;
    
    if (text) {
        messageHTML += `<div class="message-text">${escapeHtml(text)}</div>`;
    }
    
    if (imageUrl) {
        messageHTML += `
            <div class="message-image">
                <img src="${imageUrl}" alt="Generated logo">
            </div>
        `;
    }
    
    if (metadata) {
        messageHTML += `
            <div class="message-metadata">
                <div class="metadata-row">
                    <span class="metadata-label">Model:</span>
                    <span>${metadata.model}</span>
                </div>
                <div class="metadata-row">
                    <span class="metadata-label">Steps:</span>
                    <span>${metadata.steps}</span>
                </div>
                <div class="metadata-row">
                    <span class="metadata-label">Dimensions:</span>
                    <span>${metadata.dimensions}</span>
                </div>
                <div class="metadata-row">
                    <span class="metadata-label">Generated:</span>
                    <span>${metadata.timestamp}</span>
                </div>
                ${filename ? `
                <button class="download-btn" onclick="downloadImage('${imageUrl}', '${filename}')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                    Download
                </button>
                ` : ''}
            </div>
        `;
    }
    
    messageHTML += `</div>`;
    messageDiv.innerHTML = messageHTML;
    
    messages.appendChild(messageDiv);
    scrollToBottom();
}

// Add error message
function addErrorMessage(errorText) {
    const messages = document.getElementById('messages');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message assistant';
    errorDiv.innerHTML = `
        <div class="message-avatar">⚠️</div>
        <div class="message-content">
            <div class="error-message">
                <strong>Error:</strong> ${escapeHtml(errorText)}
            </div>
        </div>
    `;
    messages.appendChild(errorDiv);
    scrollToBottom();
}

// Download image
function downloadImage(dataUrl, filename) {
    const link = document.createElement('a');
    link.href = dataUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Scroll to bottom
function scrollToBottom() {
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Show/hide loading
function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// Toggle sidebar (mobile)
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('active');
}

// Toggle settings modal
function toggleSettings() {
    const modal = document.getElementById('settingsModal');
    modal.classList.toggle('active');
    
    // Load current settings
    document.getElementById('useLoraToggle').checked = currentSettings.use_lora;
    document.getElementById('stepsSlider').value = currentSettings.num_steps;
    document.getElementById('widthSlider').value = currentSettings.width;
    document.getElementById('heightSlider').value = currentSettings.height;
    
    updateStepsValue(currentSettings.num_steps);
    updateWidthValue(currentSettings.width);
    updateHeightValue(currentSettings.height);
}

// Update setting values
function updateStepsValue(value) {
    document.getElementById('stepsValue').textContent = value;
    currentSettings.num_steps = parseInt(value);
}

function updateWidthValue(value) {
    document.getElementById('widthValue').textContent = value;
    currentSettings.width = parseInt(value);
}

function updateHeightValue(value) {
    document.getElementById('heightValue').textContent = value;
    currentSettings.height = parseInt(value);
}

// Save settings
document.addEventListener('change', (e) => {
    if (e.target.id === 'useLoraToggle') {
        currentSettings.use_lora = e.target.checked;
    }
});

// Load model status
async function loadModelStatus() {
    const statusDiv = document.getElementById('modelStatus');
    statusDiv.style.display = 'block';
    statusDiv.innerHTML = '<p>Loading...</p>';
    
    try {
        const response = await fetch('/api/model/status');
        const data = await response.json();
        
        if (data.success) {
            const model = data.model;
            statusDiv.innerHTML = `
                <pre>
Base Model: ${model.base_model_loaded ? '✅ Loaded' : '❌ Not loaded'}
LoRA Model: ${model.lora_loaded ? '✅ Loaded' : '⚠️ Not loaded'}
Device: ${model.device}
Model ID: ${model.model_id || 'None'}
Status: ${model.base_model_loaded ? '🟢 Ready' : '🔴 Not ready'}
                </pre>
            `;
        } else {
            statusDiv.innerHTML = `<p class="error-message">${data.error}</p>`;
        }
    } catch (error) {
        statusDiv.innerHTML = `<p class="error-message">Failed to load model status</p>`;
    }
}

// Load history
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();
        
        if (data.success && data.history) {
            conversationHistory = data.history;
            updateHistoryList();
        }
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

// Update history list in sidebar
function updateHistoryList() {
    const historyList = document.getElementById('historyList');
    
    if (conversationHistory.length === 0) {
        historyList.innerHTML = '<p style="color: var(--text-secondary); font-size: 13px; padding: 12px;">No history yet</p>';
        return;
    }
    
    historyList.innerHTML = conversationHistory
        .slice(-10)
        .reverse()
        .map((item, index) => {
            const text = item.user || item[0] || 'Untitled';
            return `<button class="history-item" onclick="viewHistoryItem(${index})">${escapeHtml(text.substring(0, 40))}${text.length > 40 ? '...' : ''}</button>`;
        })
        .join('');
}

// View history item
function viewHistoryItem(index) {
    // This would load a previous conversation
    console.log('View history item:', index);
}

// Utility: Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modal on outside click
document.getElementById('settingsModal').addEventListener('click', (e) => {
    if (e.target.id === 'settingsModal') {
        toggleSettings();
    }
});

// Close sidebar on outside click (mobile)
document.addEventListener('click', (e) => {
    const sidebar = document.getElementById('sidebar');
    const menuBtn = document.querySelector('.menu-btn');
    
    if (window.innerWidth <= 768 && 
        sidebar.classList.contains('active') && 
        !sidebar.contains(e.target) && 
        !menuBtn.contains(e.target)) {
        sidebar.classList.remove('active');
    }
});
