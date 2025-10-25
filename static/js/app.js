// Zypher AI - ChatGPT-Style Interface JavaScript

// State
let currentSettings = {
    use_lora: false,
    num_steps: 4,
    width: 1024,
    height: 1024,
    use_ip_adapter: false,
    ip_adapter_scale: 0.5,
    reference_image: null
};

let conversationHistory = [];
let mistralConversationHistory = [];

// Return Authorization headers if an auth token is available
function getAuthHeaders() {
    const token = localStorage.getItem('authToken');
    if (token) {
        return { 'Authorization': 'Bearer ' + token };
    }
    return {};
}

// Initialize
let userProfile = null;
document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
    loadUserProfile();
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
    mistralConversationHistory = [];
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
    
    // Show typing indicator instead of full loading overlay
    const typingIndicator = addTypingIndicator();
    
    try {
        // First, try to chat with Mistral AI
        const authHeaders = getAuthHeaders();
        const chatResponse = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...authHeaders
            },
            body: JSON.stringify({
                message: prompt,
                conversation_history: mistralConversationHistory
            })
        });
        
        const chatData = await chatResponse.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        if (chatData.success) {
            // Add user message to Mistral conversation history
            mistralConversationHistory.push({
                role: 'user',
                content: prompt
            });
            
            // If Mistral detected an image generation request and generated it
            if (chatData.is_image_request && chatData.image) {
                // Add assistant response message with streaming effect
                const responseMsg = addStreamingMessage('assistant', '');
                await streamText(chatData.response, responseMsg);
                finalizeStreamingMessage();
                
                // Add the generated image
                addMessage('assistant', '', chatData.image, chatData.metadata, chatData.filename);
                
                // Add to conversation history
                conversationHistory.push({
                    user: prompt,
                    assistant: chatData.filename,
                    timestamp: new Date().toISOString()
                });
                
                // Add to Mistral conversation history
                mistralConversationHistory.push({
                    role: 'assistant',
                    content: chatData.response
                });
                
                updateHistoryList();
            } 
            // If Mistral wants to generate but there was an error or limit reached
            else if (chatData.is_image_request) {
                const responseMsg = addStreamingMessage('assistant', '');
                await streamText(chatData.response, responseMsg);
                finalizeStreamingMessage();
                
                mistralConversationHistory.push({
                    role: 'assistant',
                    content: chatData.response
                });
                
                // Show upgrade message if needed
                if (chatData.needs_upgrade) {
                    // User can manually upgrade
                }
            }
            // Normal chat response with streaming
            else {
                const responseMsg = addStreamingMessage('assistant', '');
                await streamText(chatData.response, responseMsg);
                finalizeStreamingMessage();
                
                mistralConversationHistory.push({
                    role: 'assistant',
                    content: chatData.response
                });
            }
        } else {
            addErrorMessage(chatData.error || 'Chat failed. Please try again.');
        }
        
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator();
        addErrorMessage('Network error. Please check your connection and try again.');
    } finally {
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
                ${metadata.ip_adapter ? `
                <div class="metadata-row">
                    <span class="metadata-label">IP-Adapter Scale:</span>
                    <span>${(metadata.ip_adapter_scale * 100).toFixed(0)}%</span>
                </div>
                ` : ''}
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
    
    return messageDiv;
}

// Add typing indicator (like ChatGPT)
function addTypingIndicator() {
    const messages = document.getElementById('messages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant typing-indicator';
    typingDiv.id = 'typingIndicator';
    
    typingDiv.innerHTML = `
        <div class="message-avatar">🎨</div>
        <div class="message-content">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    
    messages.appendChild(typingDiv);
    scrollToBottom();
    
    return typingDiv;
}

// Add generating indicator (for image generation)
function addGeneratingIndicator() {
    const messages = document.getElementById('messages');
    const generatingDiv = document.createElement('div');
    generatingDiv.className = 'message assistant typing-indicator';
    generatingDiv.id = 'generatingIndicator';
    
    generatingDiv.innerHTML = `
        <div class="message-avatar">🎨</div>
        <div class="message-content">
            <div class="generating-status">
                <div class="generating-spinner"></div>
                <span>Generating your logo...</span>
            </div>
        </div>
    `;
    
    messages.appendChild(generatingDiv);
    scrollToBottom();
    
    return generatingDiv;
}

// Remove generating indicator
function removeGeneratingIndicator() {
    const indicator = document.getElementById('generatingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

// Remove typing indicator
function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

// Add streaming message (for text that appears gradually)
function addStreamingMessage(role, text = '') {
    const messages = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.id = 'streamingMessage';
    
    const avatar = role === 'user' ? '👤' : '🎨';
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-text" id="streamingText">${escapeHtml(text)}</div>
        </div>
    `;
    
    messages.appendChild(messageDiv);
    scrollToBottom();
    
    return messageDiv;
}

// Update streaming message text
function updateStreamingMessage(text) {
    const streamingText = document.getElementById('streamingText');
    if (streamingText) {
        streamingText.innerHTML = escapeHtml(text);
        scrollToBottom();
    }
}

// Finalize streaming message (remove ID to prevent further updates)
function finalizeStreamingMessage() {
    const streamingMsg = document.getElementById('streamingMessage');
    if (streamingMsg) {
        streamingMsg.removeAttribute('id');
    }
    const streamingText = document.getElementById('streamingText');
    if (streamingText) {
        streamingText.removeAttribute('id');
    }
}

// Simulate streaming effect for text
async function streamText(text, messageDiv) {
    const textElement = messageDiv.querySelector('.message-text');
    if (!textElement) return;
    
    // Split into words for more natural streaming
    const words = text.split(' ');
    textElement.textContent = '';
    
    for (let i = 0; i < words.length; i++) {
        textElement.textContent += (i > 0 ? ' ' : '') + words[i];
        scrollToBottom();
        // Adjust delay for speed (lower = faster)
        await new Promise(resolve => setTimeout(resolve, 30));
    }
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
    const useLoraToggle = document.getElementById('useLoraToggle');
    const stepsSlider = document.getElementById('stepsSlider');
    const widthSlider = document.getElementById('widthSlider');
    const heightSlider = document.getElementById('heightSlider');

    if (useLoraToggle) useLoraToggle.checked = currentSettings.use_lora;
    if (stepsSlider) stepsSlider.value = currentSettings.num_steps;
    if (widthSlider) widthSlider.value = currentSettings.width;
    if (heightSlider) heightSlider.value = currentSettings.height;

    updateStepsValue(currentSettings.num_steps);
    updateWidthValue(currentSettings.width);
    updateHeightValue(currentSettings.height);

    // Populate profile fields if available
    const fnameEl = document.getElementById('fnameInput');
    const lnameEl = document.getElementById('lnameInput');
    if (userProfile) {
        if (fnameEl) fnameEl.value = userProfile.fname || '';
        if (lnameEl) lnameEl.value = userProfile.lname || '';
    } else {
        if (fnameEl) fnameEl.value = '';
        if (lnameEl) lnameEl.value = '';
    }
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

function updateIpAdapterScale(value) {
    document.getElementById('ipAdapterScaleValueInline').textContent = value;
    currentSettings.ip_adapter_scale = parseFloat(value) / 100;
}

// Toggle IP-Adapter
function toggleIpAdapter(enabled) {
    currentSettings.use_ip_adapter = enabled;
    const referenceContent = document.getElementById('referenceContent');
    referenceContent.style.display = enabled ? 'block' : 'none';
}

// Handle image upload
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file type
    if (!file.type.startsWith('image/')) {
        alert('Please upload an image file (JPG, PNG, WEBP)');
        return;
    }
    
    // Store file
    currentSettings.reference_image = file;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('previewImgInline').src = e.target.result;
        document.getElementById('uploadAreaInline').style.display = 'none';
        document.getElementById('imagePreviewInline').style.display = 'block';
    };
    reader.readAsDataURL(file);
}

// Remove reference image
function removeReferenceImage(event) {
    if (event) event.stopPropagation();
    currentSettings.reference_image = null;
    document.getElementById('referenceImageInput').value = '';
    document.getElementById('previewImgInline').src = '';
    document.getElementById('uploadAreaInline').style.display = 'flex';
    document.getElementById('imagePreviewInline').style.display = 'none';
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
    const response = await fetch('/api/model/status', { headers: getAuthHeaders() });
        const data = await response.json();
        
        if (data.success) {
            const model = data.model;
            statusDiv.innerHTML = `
                <pre>
Base Model: ${model.base_model_loaded ? '✅ Loaded' : '❌ Not loaded'}
LoRA Model: ${model.lora_loaded ? '✅ Loaded' : '⚠️ Not loaded'}
IP-Adapter: ${model.ip_adapter_loaded ? '✅ Loaded' : '⚠️ Not loaded'}
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
    const response = await fetch('/api/history', { headers: getAuthHeaders() });
        const data = await response.json();
        
        if (data.success && data.history) {
            conversationHistory = data.history;
            updateHistoryList();
        }
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

// Load current user's profile (fname/lname)
async function loadUserProfile() {
    try {
        const resp = await fetch('/api/user/profile', { headers: getAuthHeaders() });
        const data = await resp.json();
        if (data.success && data.profile) {
            userProfile = data.profile;
            const fname = userProfile.fname || '';
            const lname = userProfile.lname || '';
            const initials = ((fname[0] || '') + (lname[0] || '')).toUpperCase() || 'AI';
            const defaultName = userProfile.email ? userProfile.email.split('@')[0] : 'User';
            const avatarEl = document.getElementById('userAvatar');
            const nameEl = document.getElementById('userFullName');
            if (avatarEl) avatarEl.textContent = initials;
            if (nameEl) nameEl.textContent = (fname || lname) ? `${fname} ${lname}`.trim() : defaultName;
            // Show plan info: free users limited to 5 prompts
            try {
                const planEl = document.getElementById('planInfo');
                if (planEl) {
                    const isPro = !!userProfile.is_pro;
                    const used = Number(userProfile.prompt_count || 0);
                    if (isPro) {
                        planEl.textContent = 'Pro — Unlimited prompts';
                    } else {
                        planEl.innerHTML = `Free — max prompts: 5 (used ${used}/5) <a href="/upgrade" style="margin-left:8px; color: var(--accent-color); font-weight:600;">Upgrade</a>`;
                    }
                }
            } catch (e) {
                console.warn('Could not render plan info', e);
            }
        }
    } catch (err) {
        console.warn('Could not load user profile', err);
    }
}

// Save current user's profile (fname/lname)
async function saveUserProfile() {
    const fname = (document.getElementById('fnameInput') || {}).value || '';
    const lname = (document.getElementById('lnameInput') || {}).value || '';
    try {
        const resp = await fetch('/api/user/profile', {
            method: 'POST',
            headers: Object.assign({'Content-Type': 'application/json'}, getAuthHeaders()),
            body: JSON.stringify({ fname: fname || null, lname: lname || null })
        });
        const data = await resp.json();
        if (data.success && data.profile) {
            userProfile = data.profile;
            // Update UI
            const avatarEl = document.getElementById('userAvatar');
            const nameEl = document.getElementById('userFullName');
            const initials = ((userProfile.fname || '')[0] || '') + ((userProfile.lname || '')[0] || '');
            if (avatarEl) avatarEl.textContent = initials.toUpperCase() || 'AI';
            const defaultName = userProfile.email ? userProfile.email.split('@')[0] : 'User';
            if (nameEl) nameEl.textContent = (userProfile.fname || userProfile.lname) ? `${userProfile.fname || ''} ${userProfile.lname || ''}`.trim() : defaultName;
            // Close modal
            toggleSettings();
            alert('Profile saved');
        } else {
            alert('Could not save profile: ' + (data.error || 'Unknown error'));
        }
    } catch (err) {
        console.error('Failed to save profile', err);
        alert('Failed to save profile');
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
