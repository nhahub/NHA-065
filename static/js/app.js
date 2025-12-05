// Zypher AI - ChatGPT-Style Interface JavaScript

// State
let currentSettings = {
    use_lora: false,
    lora_filename: null,
    num_steps: 4,
    width: 1024,
    height: 1024,
    use_ip_adapter: false,
    ip_adapter_scale: 0.5,
    reference_image: null
};

let conversationHistory = [];
let mistralConversationHistory = [];
let availableLoras = [];
let useWebSearch = false; // Web search toggle state
let currentConversationId = null;
let activeConversationState = null;

// Generate new conversation ID
function generateConversationId() {
    return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// New chat function
function newChat() {
    conversationHistory = [];
    mistralConversationHistory = [];
    currentConversationId = generateConversationId(); // Generate new conversation ID
    document.getElementById('messages').innerHTML = '';
    document.getElementById('welcomeScreen').style.display = 'flex';
    document.getElementById('promptInput').value = '';
    focusInput();
}
// Initialize conversation ID on page load
document.addEventListener('DOMContentLoaded', () => {
    currentConversationId = generateConversationId();
    loadHistory();
    loadUserProfile();
    loadAvailableLoras();
    updateUserInfo();
    focusInput();
});

// Return Authorization headers if an auth token is available
function getAuthHeaders() {
    const token = localStorage.getItem('authToken');
    if (token) {
        return { 'Authorization': 'Bearer ' + token };
    }
    return {};
}

// Update user info and prompt count
async function updateUserInfo() {
    const token = localStorage.getItem('authToken');
    if (!token) return;

    try {
        const response = await fetch('/api/user/profile', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        if (data.success && data.profile) {
            const profile = data.profile;

            // Update plan info display in header
            const planInfo = document.getElementById('planInfo');
            if (planInfo) {
                if (profile.is_pro) {
                    planInfo.innerHTML = '<span style="color: #10a37f; font-weight: 500;">✨ Pro Plan</span> • Unlimited prompts';
                } else {
                    const remaining = Math.max(0, 5 - (profile.prompt_count || 0));
                    const color = remaining === 0 ? '#ef4444' : (remaining <= 2 ? '#f59e0b' : '#6b7280');
                    planInfo.innerHTML = `<span style="color: ${color}; font-weight: 500;">Free Plan</span> • ${remaining}/5 prompts remaining`;

                    // Show upgrade link
                    if (remaining <= 5) {
                        planInfo.innerHTML += ' • <a href="/upgrade" style="color: #10a37f; text-decoration: underline; font-weight: 600;">Upgrade</a>';
                    }
                }
            }

            // Update user avatar and name in sidebar
            const userAvatar = document.getElementById('userAvatar');
            const userFullName = document.getElementById('userFullName');

            if (profile.fname || profile.lname) {
                const initials = ((profile.fname || '')[0] || '') + ((profile.lname || '')[0] || '');
                if (userAvatar) userAvatar.textContent = initials.toUpperCase() || 'AI';
                if (userFullName) userFullName.textContent = `${profile.fname || ''} ${profile.lname || ''}`.trim();
            } else {
                const defaultName = profile.email ? profile.email.split('@')[0] : 'User';
                if (userFullName) userFullName.textContent = defaultName;
            }

            // Store profile globally
            userProfile = profile;
        }
    } catch (error) {
        console.error('Error fetching user info:', error);
    }
}

// Initialize
let userProfile = null;
document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
    loadUserProfile();
    loadAvailableLoras();
    updateUserInfo();
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
    // Save current conversation state before clearing
    if (currentConversationId && document.getElementById('messages').innerHTML.trim() !== '') {
        saveCurrentConversationState();
    }
    
    // Generate new conversation ID
    currentConversationId = generateConversationId();
    
    // Clear conversation state
    conversationHistory = [];
    mistralConversationHistory = [];
    activeConversationState = {
        conversationId: currentConversationId,
        messages: [],
        mistralHistory: []
    };
    
    // Clear UI
    document.getElementById('messages').innerHTML = '';
    document.getElementById('welcomeScreen').style.display = 'flex';
    document.getElementById('promptInput').value = '';
    
    focusInput();
}

// Save current conversation state to memory
function saveCurrentConversationState() {
    if (!currentConversationId) return;
    
    const messagesContainer = document.getElementById('messages');
    const messages = Array.from(messagesContainer.children).map(msg => ({
        html: msg.outerHTML,
        className: msg.className
    }));
    
    activeConversationState = {
        conversationId: currentConversationId,
        messages: messages,
        mistralHistory: [...mistralConversationHistory]
    };
}

// Restore conversation state from memory
function restoreConversationState(conversationId) {
    if (activeConversationState && activeConversationState.conversationId === conversationId) {
        // Restore from memory
        const messagesContainer = document.getElementById('messages');
        messagesContainer.innerHTML = '';
        
        activeConversationState.messages.forEach(msg => {
            const div = document.createElement('div');
            div.className = msg.className;
            div.innerHTML = msg.html.replace(/^<div[^>]*>/, '').replace(/<\/div>$/, '');
            messagesContainer.appendChild(div);
        });
        
        mistralConversationHistory = [...activeConversationState.mistralHistory];
        currentConversationId = conversationId;
        
        document.getElementById('welcomeScreen').style.display = 'none';
        scrollToBottom();
        
        return true;
    }
    return false;
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

    // Show typing indicator
    const typingIndicator = addTypingIndicator();

    try {
        const authHeaders = getAuthHeaders();
        const chatResponse = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...authHeaders
            },
            body: JSON.stringify({
                message: prompt,
                conversation_history: mistralConversationHistory,
                use_web_search: useWebSearch,
                conversation_id: currentConversationId
            })
        });
        const chatData = await chatResponse.json();

        removeTypingIndicator();

        if (chatData.success) {
            mistralConversationHistory.push({ role: 'user', content: prompt });

            if (chatData.is_image_request && chatData.needs_generation) {
                // Show AI acknowledgment
                const responseMsg = addStreamingMessage('assistant', '');
                await streamText(chatData.response, responseMsg);
                finalizeStreamingMessage();

                mistralConversationHistory.push({ role: 'assistant', content: chatData.response });

                // Show generating indicator
                const generatingIndicator = addGeneratingIndicator();

                try {
                    const generateResponse = await fetch('/api/generate-from-chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            ...authHeaders
                        },
                        body: JSON.stringify({
                            image_prompt: chatData.image_prompt,
                            conversation_id: currentConversationId,
                            use_lora: currentSettings.use_lora,
                            lora_filename: currentSettings.lora_filename,
                            num_steps: currentSettings.num_steps,
                            width: currentSettings.width,
                            height: currentSettings.height,
                            use_ip_adapter: currentSettings.use_ip_adapter,
                            ip_adapter_scale: currentSettings.ip_adapter_scale
                        })
                    });

                    const generateData = await generateResponse.json();
                    removeGeneratingIndicator();

                    if (generateData.success) {
                        const messages = document.getElementById('messages');
                        const messageDiv = document.createElement('div');
                        messageDiv.className = 'message assistant';
                        
                        const fullPrompt = chatData.image_prompt || '[No refined prompt available]';
                        
                        messageDiv.innerHTML = `
                            <div class="message-avatar"><img src="/photos/zypher.jpeg" alt="AI" class="avatar-logo"></div>
                            <div class="message-content">
                                <div class="message-text markdown-content">
                                    <strong>Generated Image</strong><br>
                                    <details style="margin-top: 8px;">
                                        <summary style="cursor: pointer; color: var(--text-secondary); font-size: 0.9em;">
                                            View full generation prompt
                                        </summary>
                                        <div style="margin-top: 8px; padding: 12px; background: var(--bg-secondary); border-radius: 6px; font-size: 0.85em; line-height: 1.6; white-space: pre-wrap;">
                                            ${escapeHtml(fullPrompt)}
                                        </div>
                                    </details>
                                </div>
                                <div class="message-image">
                                    <img src="${generateData.image}" alt="Generated logo">
                                </div>
                                <div class="message-metadata">
                                    <div class="metadata-row">
                                        <span class="metadata-label">Model:</span>
                                        <span>${generateData.metadata.model}</span>
                                    </div>
                                    ${generateData.metadata.lora ? `
                                    <div class="metadata-row">
                                        <span class="metadata-label">LoRA:</span>
                                        <span>${generateData.metadata.lora}</span>
                                    </div>
                                    ` : ''}
                                    <div class="metadata-row">
                                        <span class="metadata-label">Steps:</span>
                                        <span>${generateData.metadata.steps}</span>
                                    </div>
                                    <div class="metadata-row">
                                        <span class="metadata-label">Dimensions:</span>
                                        <span>${generateData.metadata.dimensions}</span>
                                    </div>
                                    ${generateData.metadata.ip_adapter_scale ? `
                                    <div class="metadata-row">
                                        <span class="metadata-label">IP-Adapter Scale:</span>
                                        <span>${generateData.metadata.ip_adapter_scale}</span>
                                    </div>
                                    ` : ''}
                                    <div class="metadata-row">
                                        <span class="metadata-label">Generated:</span>
                                        <span>${generateData.metadata.timestamp}</span>
                                    </div>
                                    <button class="download-btn" onclick="downloadImage('${generateData.image}', '${generateData.filename}')">
                                        Download
                                    </button>
                                </div>
                            </div>
                        `;
                        
                        messages.appendChild(messageDiv);
                        scrollToBottom();

                        // Save state after successful generation
                        saveCurrentConversationState();
                        
                        // Reload history to show updated conversation
                        await loadHistory();
                        await updateUserInfo();
                    } else {
                        addErrorMessage(generateData.error || 'Failed to generate image.');
                    }
                } catch (genError) {
                    console.error('Generation error:', genError);
                    removeGeneratingIndicator();
                    addErrorMessage('Failed to generate image. Please try again.');
                }
            }
            else if (chatData.is_image_request) {
                const responseMsg = addStreamingMessage('assistant', '');
                await streamText(chatData.response, responseMsg);
                finalizeStreamingMessage();
                mistralConversationHistory.push({ role: 'assistant', content: chatData.response });
                saveCurrentConversationState();
                await updateUserInfo();
            }
            else if (chatData.awaiting_photo_confirmation && chatData.photo_result) {
                const responseMsg = addStreamingMessage('assistant', '');
                await streamText(chatData.response, responseMsg);
                finalizeStreamingMessage();
                
                if (chatData.photo_result.results && chatData.photo_result.results.length > 0) {
                    addPhotoGrid(chatData.photo_result.results);
                }
                
                mistralConversationHistory.push({ role: 'assistant', content: chatData.response });
                saveCurrentConversationState();
            }
            else if (chatData.photo_confirmed) {
                const responseMsg = addStreamingMessage('assistant', '');
                await streamText(chatData.response, responseMsg);
                finalizeStreamingMessage();
                mistralConversationHistory.push({ role: 'assistant', content: chatData.response });
                saveCurrentConversationState();
            }
            else {
                const responseMsg = addStreamingMessage('assistant', '');
                await streamText(chatData.response, responseMsg);
                finalizeStreamingMessage();
                mistralConversationHistory.push({ role: 'assistant', content: chatData.response });
                saveCurrentConversationState();
            }
        } else {
            addErrorMessage(chatData.error || 'Chat failed. Please try again.');
        }

    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator();
        addErrorMessage('Network error. Please check your connection.');
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

    const avatar = role === 'user' ? '👤' : '<img src="/photos/zypher.jpeg" alt="AI" class="avatar-logo">';

    let messageHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
    `;

    if (text) {
        if (role === 'assistant' && typeof marked !== 'undefined') {
            messageHTML += `<div class="message-text markdown-content">${marked.parse(text)}</div>`;
        } else {
            messageHTML += `<div class="message-text">${escapeHtml(text)}</div>`;
        }
    } else if (imageUrl) {
        // Show "Generated:" when only image is sent
        messageHTML += `<div class="message-text" style="font-weight:500; margin-bottom:8px; color:var(--text-secondary);">Generated:</div>`;
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
                <div class="metadata-row"><span class="metadata-label">Model:</span><span>${metadata.model}</span></div>
                <div class="metadata-row"><span class="metadata-label">Steps:</span><span>${metadata.steps}</span></div>
                <div class="metadata-row"><span class="metadata-label">Dimensions:</span><span>${metadata.dimensions}</span></div>
                ${metadata.ip_adapter ? `<div class="metadata-row"><span class="metadata-label">IP-Adapter:</span><span>${(metadata.ip_adapter_scale * 100).toFixed(0)}%</span></div>` : ''}
                <div class="metadata-row"><span class="metadata-label">Generated:</span><span>${metadata.timestamp}</span></div>
                ${filename ? `<button class="download-btn" onclick="downloadImage('${imageUrl}', '${filename}')">Download</button>` : ''}
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
        <div class="message-avatar"><img src="/photos/zypher.jpeg" alt="AI" class="avatar-logo"></div>
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
        <div class="message-avatar"><img src="/photos/zypher.jpeg" alt="AI" class="avatar-logo"></div>
        <div class="message-content">
            <div class="generating-status">
                <div class="generating-spinner"></div>
                <span class="generating-text">Generating your logo<span class="dots"></span></span>
            </div>
        </div>
    `;

    messages.appendChild(generatingDiv);
    scrollToBottom();

    // Animate the dots
    animateGeneratingDots();

    return generatingDiv;
}

// Remove generating indicator
function removeGeneratingIndicator() {
    const indicator = document.getElementById('generatingIndicator');
    if (indicator) {
        indicator.remove();
    }
    // Clear the animation interval
    if (window.generatingDotsInterval) {
        clearInterval(window.generatingDotsInterval);
        window.generatingDotsInterval = null;
    }
}

// Animate generating dots
function animateGeneratingDots() {
    let dotCount = 0;
    window.generatingDotsInterval = setInterval(() => {
        const dotsElement = document.querySelector('.generating-text .dots');
        if (dotsElement) {
            dotCount = (dotCount + 1) % 4;
            dotsElement.textContent = '.'.repeat(dotCount);
        } else {
            clearInterval(window.generatingDotsInterval);
        }
    }, 500);
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

    const avatar = role === 'user' ? '👤' : '<img src="/photos/zypher.jpeg" alt="AI" class="avatar-logo">';

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-text markdown-content" id="streamingText">${text}</div>
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
        // Render as markdown for assistant messages
        if (typeof marked !== 'undefined') {
            streamingText.innerHTML = marked.parse(text);
        } else {
            streamingText.innerHTML = escapeHtml(text);
        }
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
    let currentText = '';

    for (let i = 0; i < words.length; i++) {
        currentText += (i > 0 ? ' ' : '') + words[i];

        // Render as markdown
        if (typeof marked !== 'undefined') {
            textElement.innerHTML = marked.parse(currentText);
        } else {
            textElement.textContent = currentText;
        }

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
    const loraSelect = document.getElementById('loraSelect');
    const stepsSlider = document.getElementById('stepsSlider');
    const widthSlider = document.getElementById('widthSlider');
    const heightSlider = document.getElementById('heightSlider');

    if (useLoraToggle) {
        useLoraToggle.checked = currentSettings.use_lora;
        toggleLoraSettings(); // Show/hide LoRA selection based on checkbox
    }
    if (loraSelect && currentSettings.lora_filename) {
        loraSelect.value = currentSettings.lora_filename;
    }
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

    // Reload LoRA list to get latest
    if (modal.classList.contains('active')) {
        loadAvailableLoras();
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
    reader.onload = function (e) {
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
        console.log('LoRA enabled:', currentSettings.use_lora);
        toggleLoraSettings();
    } else if (e.target.id === 'loraSelect') {
        currentSettings.lora_filename = e.target.value || null;
        console.log('LoRA filename selected:', currentSettings.lora_filename);
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

        if (data.success && data.conversations) {
            conversationHistory = data.conversations;
            updateHistoryList();
        }
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

// Update history list to show conversations
function updateHistoryList() {
    const historyList = document.getElementById('historyList');

    if (!conversationHistory || conversationHistory.length === 0) {
        historyList.innerHTML = '<p style="color: var(--text-secondary); font-size: 13px; padding: 12px;">No history yet</p>';
        return;
    }

    historyList.innerHTML = conversationHistory
        .map((conv) => {
            const preview = conv.preview || 'New Chat';
            const timestamp = conv.last_updated ? new Date(conv.last_updated).toLocaleDateString() : '';
            const messageCount = conv.message_count || 1;
            const isActive = conv.conversation_id === currentConversationId;

            return `
                <div class="history-item-wrapper">
                    <button class="history-item ${isActive ? 'active' : ''}" 
                            onclick="loadConversation('${conv.conversation_id}')" 
                            title="${escapeHtml(preview)}">
                        <span class="history-item-text">${escapeHtml(preview)}</span>
                        <span class="history-item-date">${timestamp} • ${messageCount} messages</span>
                    </button>
                    <button class="history-item-delete" onclick="deleteConversation(event, '${conv.conversation_id}')" title="Delete">
                        🗑️
                    </button>
                </div>
            `;
        })
        .join('');
}

// Load entire conversation
async function loadConversation(conversationId) {
    // Save current state before switching
    if (currentConversationId && document.getElementById('messages').innerHTML.trim() !== '') {
        saveCurrentConversationState();
    }
    
    // Check if conversation is in memory (unsaved new chat)
    if (restoreConversationState(conversationId)) {
        console.log('✓ Restored conversation from memory:', conversationId);
        return;
    }
    
    // Otherwise load from database
    try {
        const response = await fetch(`/api/history/${conversationId}`, { 
            headers: getAuthHeaders() 
        });
        const data = await response.json();

        if (data.success && data.messages) {
            // Clear current view
            document.getElementById('messages').innerHTML = '';
            document.getElementById('welcomeScreen').style.display = 'none';
            
            // Set current conversation ID
            currentConversationId = conversationId;
            
            // Clear conversation history for fresh start
            mistralConversationHistory = [];
            
            // Display all messages in order
            for (const msg of data.messages) {
                // Show user message
                addMessage('user', msg.user_message);
                
                // Add to Mistral history
                mistralConversationHistory.push({
                    role: 'user',
                    content: msg.user_message
                });
                
                // Show AI response if it's a text message
                if (msg.ai_response && msg.message_type !== 'image') {
                    addMessage('assistant', msg.ai_response);
                    mistralConversationHistory.push({
                        role: 'assistant',
                        content: msg.ai_response
                    });
                }
                
                // Show image if exists
                if (msg.image_path && msg.message_type === 'image') {
                    const imageName = msg.image_path.split('/').pop() || msg.image_path.split('\\').pop();
                    const imageUrl = `/outputs/${imageName}`;
                    const fullPrompt = msg.image_prompt || '[No refined prompt available]';
                    
                    const messages = document.getElementById('messages');
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message assistant';
                    
                    messageDiv.innerHTML = `
                        <div class="message-avatar"><img src="/photos/zypher.jpeg" alt="AI" class="avatar-logo"></div>
                        <div class="message-content">
                            <div class="message-text markdown-content">
                                <strong>Generated Image</strong><br>
                                <details style="margin-top: 8px;">
                                    <summary style="cursor: pointer; color: var(--text-secondary); font-size: 0.9em;">
                                        View full generation prompt
                                    </summary>
                                    <div style="margin-top: 8px; padding: 12px; background: var(--bg-secondary); border-radius: 6px; font-size: 0.85em; line-height: 1.6; white-space: pre-wrap;">
                                        ${escapeHtml(fullPrompt)}
                                    </div>
                                </details>
                            </div>
                            <div class="message-image">
                                <img src="${imageUrl}" alt="Generated logo" 
                                    onerror="this.parentElement.innerHTML='<p style=\\'color: var(--text-secondary); padding: 20px; text-align: center;\\'>Image not found</p>'">
                            </div>
                            <div class="message-metadata">
                                <div class="metadata-row">
                                    <span class="metadata-label">Generated:</span>
                                    <span>${msg.timestamp ? new Date(msg.timestamp).toLocaleString() : 'Unknown'}</span>
                                </div>
                                <button class="download-btn" onclick="downloadImage('${imageUrl}', '${imageName}')">
                                    Download
                                </button>
                            </div>
                        </div>
                    `;
                    messages.appendChild(messageDiv);
                }
            }
            
            // Save loaded state to memory
            saveCurrentConversationState();
            
            scrollToBottom();
        } else {
            alert('Could not load conversation');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to load conversation');
    }
}


// Delete conversation
async function deleteConversation(event, conversationId) {
    event.stopPropagation();

    if (!confirm('Delete this entire conversation?')) {
        return;
    }

    try {
        const response = await fetch(`/api/history/conversation/${conversationId}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        const data = await response.json();

        if (data.success) {
            // Remove from local array
            conversationHistory = conversationHistory.filter(
                conv => conv.conversation_id !== conversationId
            );
            updateHistoryList();
            
            // If we're currently viewing this conversation, start a new chat
            if (currentConversationId === conversationId) {
                newChat();
            }
        } else {
            alert('Could not delete conversation: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error deleting conversation:', error);
        alert('Failed to delete conversation');
    }
}

// View history item 
async function viewHistoryItem(historyId) {
    try {
        const response = await fetch(`/api/history/${historyId}`, { headers: getAuthHeaders() });
        const data = await response.json();

        if (data.success && data.history) {
            document.getElementById('messages').innerHTML = '';
            document.getElementById('welcomeScreen').style.display = 'none';

            const item = data.history;

            // 1. Show user's original message
            const userMessage = item.user_message || 'Generate image';
            addMessage('user', userMessage);

            // 2. Show AI's text response (if exists)
            if (item.ai_response && item.message_type !== 'image') {
                addMessage('assistant', item.ai_response);
            }

            // 3. Show the generated image using the SAME structure as sendMessage()
            if (item.image_path && item.message_type === 'image') {
                const imageName = item.image_path.split('/').pop() || item.image_path.split('\\').pop();
                const imageUrl = `/outputs/${imageName}`;
                const fullPrompt = item.image_prompt || '[No refined prompt available]';
                
                // Use the same format as in sendMessage() for consistency
                const messages = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message assistant';
                
                messageDiv.innerHTML = `
                    <div class="message-avatar"><img src="/photos/zypher.jpeg" alt="AI" class="avatar-logo"></div>
                    <div class="message-content">
                        <div class="message-text markdown-content">
                            <strong>Generated Image</strong><br>
                            <details style="margin-top: 8px;">
                                <summary style="cursor: pointer; color: var(--text-secondary); font-size: 0.9em;">
                                    View full generation prompt
                                </summary>
                                <div style="margin-top: 8px; padding: 12px; background: var(--bg-secondary); border-radius: 6px; font-size: 0.85em; line-height: 1.6; white-space: pre-wrap;">
                                    ${escapeHtml(fullPrompt)}
                                </div>
                            </details>
                        </div>
                        <div class="message-image">
                            <img src="${imageUrl}" alt="Generated logo" 
                                onerror="this.parentElement.innerHTML='<p style=\\'color: var(--text-secondary); padding: 20px; text-align: center;\\'>Image not found</p>'">
                        </div>
                        <div class="message-metadata">
                            <div class="metadata-row">
                                <span class="metadata-label">Generated:</span>
                                <span>${item.timestamp ? new Date(item.timestamp).toLocaleString() : 'Unknown'}</span>
                            </div>
                            <button class="download-btn" onclick="downloadImage('${imageUrl}', '${imageName}')">
                                Download
                            </button>
                        </div>
                    </div>
                `;
                messages.appendChild(messageDiv);
            }
            
            scrollToBottom();
        } else {
            alert('Could not load history item');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to load history item');
    }
}
// Delete history item
async function deleteHistoryItem(event, historyId) {
    event.stopPropagation(); // Prevent triggering the view action

    if (!confirm('Are you sure you want to delete this history item?')) {
        return;
    }

    try {
        const response = await fetch(`/api/history/${historyId}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        const data = await response.json();

        if (data.success) {
            // Remove from local array
            conversationHistory = conversationHistory.filter(item => item.id !== historyId);
            updateHistoryList();
        } else {
            alert('Could not delete history item: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error deleting history item:', error);
        alert('Failed to delete history item');
    }
}

// Clear all history
async function clearAllHistory() {
    if (!confirm('Are you sure you want to delete ALL conversations? This cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch('/api/history', {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        const data = await response.json();

        if (data.success) {
            conversationHistory = [];
            updateHistoryList();
            newChat();
        } else {
            alert('Could not clear history: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error clearing history:', error);
        alert('Failed to clear history');
    }
}

// Load available LoRA models
async function loadAvailableLoras() {
    try {
        const resp = await fetch('/api/model/loras', { headers: getAuthHeaders() });
        const data = await resp.json();
        if (data.success) {
            availableLoras = data.loras;
            updateLoraSelect();
        }
    } catch (err) {
        console.warn('Could not load LoRA models', err);
    }
}

// Update LoRA select dropdown
function updateLoraSelect() {
    const loraSelect = document.getElementById('loraSelect');
    const loraCount = document.getElementById('loraCount');

    if (!loraSelect) return;

    loraSelect.innerHTML = '';

    if (availableLoras.length === 0) {
        loraSelect.innerHTML = '<option value="">No LoRA models found</option>';
        if (loraCount) loraCount.textContent = '0 LoRA models available';
    } else {
        // Add default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = '-- Select a LoRA --';
        loraSelect.appendChild(defaultOption);

        // Add LoRA options
        availableLoras.forEach(lora => {
            const option = document.createElement('option');
            option.value = lora;
            option.textContent = lora;
            loraSelect.appendChild(option);
        });

        if (loraCount) loraCount.textContent = `${availableLoras.length} LoRA model${availableLoras.length !== 1 ? 's' : ''} available`;
    }
}

// Toggle LoRA settings visibility
function toggleLoraSettings() {
    const useLoraToggle = document.getElementById('useLoraToggle');
    const loraSelectionGroup = document.getElementById('loraSelectionGroup');

    if (useLoraToggle && loraSelectionGroup) {
        if (useLoraToggle.checked) {
            loraSelectionGroup.style.display = 'block';
        } else {
            loraSelectionGroup.style.display = 'none';
        }
    }
}

// Load user profile and update UI
async function loadUserProfile() {
    const token = localStorage.getItem('authToken');
    if (!token) return;

    try {
        const resp = await fetch('/api/user/profile', {
            headers: { 'Authorization': 'Bearer ' + token }
        });
        const data = await resp.json();
        if (!data.success) throw new Error(data.error || 'Failed');

        const profile = data.profile;

        /* ---------- 1. Header plan info (same as updateUserInfo) ---------- */
        const planInfo = document.getElementById('planInfo');
        if (planInfo) {
            if (profile.is_pro) {
                planInfo.innerHTML = '<span style="color: #10a37f; font-weight: 500;">Pro Plan</span> • Unlimited prompts';
            } else {
                const remaining = Math.max(0, 5 - (profile.prompt_count || 0));
                const color = remaining === 0 ? '#ef4444' : (remaining <= 2 ? '#f59e0b' : '#6b7280');
                planInfo.innerHTML = `<span style="color: ${color}; font-weight: 500;">Free Plan</span> • ${remaining}/5 prompts remaining`;
                if (remaining <= 5) {
                    planInfo.innerHTML += ' • <a href="/upgrade" style="color: #10a37f; text-decoration: underline; font-weight: 600;">Upgrade</a>';
                }
            }
        }

        /* ---------- 2. Sidebar name / avatar ---------- */
        const userAvatar = document.getElementById('userAvatar');
        const userFullName = document.getElementById('userFullName');

        if (profile.fname || profile.lname) {
            const initials = ((profile.fname || '')[0] || '') + ((profile.lname || '')[0] || '');
            if (userAvatar) userAvatar.textContent = initials.toUpperCase() || 'AI';
            if (userFullName) userFullName.textContent = `${profile.fname || ''} ${profile.lname || ''}`.trim();
        } else {
            const defaultName = profile.email ? profile.email.split('@')[0] : 'User';
            if (userFullName) userFullName.textContent = defaultName;
        }

        /* ---------- 3. Settings-modal plan badge (unchanged) ---------- */
        const badge = document.getElementById('planBadge');
        if (badge) {
            const badgeText = badge.querySelector('.plan-text');
            const left = 5 - (profile.prompt_count || 0);
            badgeText.textContent = profile.is_pro ? 'Pro (Unlimited)' : `Free (${left} left today)`;
            badge.className = profile.is_pro ? 'plan-badge pro' : 'plan-badge free';
        }

        /* ---------- 4. Unsubscribe button visibility ---------- */
        document.getElementById('unsubscribeBtn').style.display = profile.is_pro ? 'inline-flex' : 'none';

        // store for other parts of the UI
        userProfile = profile;
    } catch (e) {
        console.warn('Could not load profile:', e);
    }
}

// Save current user's profile (fname/lname)
async function saveUserProfile() {
    const fname = (document.getElementById('fnameInput') || {}).value || '';
    const lname = (document.getElementById('lnameInput') || {}).value || '';
    try {
        const resp = await fetch('/api/user/profile', {
            method: 'POST',
            headers: Object.assign({ 'Content-Type': 'application/json' }, getAuthHeaders()),
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

            // 🎯 ADD THIS LINE - Update prompt count display after saving profile
            await updateUserInfo();

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

// Unsubscribe from Pro 
async function unsubscribeFromPro() {
    if (!confirm('Are you sure you want to cancel your Pro subscription? You will revert to the free tier (5 images/day).')) {
        return;
    }

    try {
        const resp = await fetch('/api/unsubscribe', {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('authToken'),
                'Content-Type': 'application/json'
            }
        });
        const data = await resp.json();

        if (!data.success) throw new Error(data.error || 'Failed');

        alert('You have been downgraded to the free tier.');
        loadUserProfile();               // refresh UI
        // reload page to clear any cached state
        location.reload();
    } catch (e) {
        console.error(e);
        alert('Unsubscribe failed: ' + (e.message || e));
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // existing initFirebaseClient() already runs
    // wait a tick for the token to be stored
    setTimeout(loadUserProfile, 800);
});

// Toggle web search button
function toggleWebSearchButton() {
    useWebSearch = !useWebSearch;
    const btn = document.getElementById('webSearchToggleBtn');
    if (btn) {
        if (useWebSearch) {
            btn.classList.add('active');
            btn.title = 'Web search enabled - Click to disable';
        } else {
            btn.classList.remove('active');
            btn.title = 'Enable web search for reference logos';
        }
    }
}

// Add photo grid to display search results
function addPhotoGrid(photos) {
    const messages = document.getElementById('messages');
    const gridDiv = document.createElement('div');
    gridDiv.className = 'message assistant';
    
    let gridHTML = `
        <div class="message-avatar"><img src="/photos/zypher.jpeg" alt="AI" class="avatar-logo"></div>
        <div class="message-content">
            <div class="photo-grid">
    `;
    
    photos.forEach((photo, index) => {
        const hostname = photo.hostname || 'web';
        const title = photo.title || 'Logo';
        // Use primary image URL with fallbacks
        const imageUrl = photo.image_url || photo.thumbnail_url;
        const fallbackUrl = photo.fallback_url || photo.full_image_url || imageUrl;
        
        // Create a unique ID for this image
        const imageId = `photo-img-${index}-${Date.now()}`;
        
        gridHTML += `
            <div class="photo-grid-item" onclick="selectPhoto(${index})">
                <div class="photo-grid-image">
                    <img id="${imageId}" 
                         src="${escapeHtml(imageUrl)}" 
                         alt="${escapeHtml(title)}" 
                         loading="lazy" 
                         data-fallback="${escapeHtml(fallbackUrl)}"
                         data-index="${index}"
                         onerror="handleImageError(this)">
                    <div class="image-loader" style="display: none;">Loading...</div>
                </div>
                <div class="photo-grid-info">
                    <div class="photo-title">${escapeHtml(title)}</div>
                    <div class="photo-source">${escapeHtml(hostname)}</div>
                </div>
            </div>
        `;
    });
    
    gridHTML += `
            </div>
            <div style="margin-top: 16px; display: flex; gap: 12px;">
                <button class="btn-secondary" onclick="document.getElementById('promptInput').value='no'; sendMessage();" style="padding: 10px 20px; background: var(--bg-input); border: 1px solid var(--border-color); border-radius: 8px; color: var(--text-primary); cursor: pointer;">❌ Search Different</button>
            </div>
        </div>
    `;
    
    gridDiv.innerHTML = gridHTML;
    messages.appendChild(gridDiv);
    scrollToBottom();
}

// Handle image loading errors with fallback
function handleImageError(img) {
    // Check if we've already tried the fallback
    if (img.dataset.tried) {
        // Show error state
        const errorDiv = document.createElement('div');
        errorDiv.className = 'image-error';
        errorDiv.innerHTML = '📷<br><span style="font-size: 12px;">Image unavailable</span>';
        img.parentElement.replaceChild(errorDiv, img);
        return;
    }
    
    // Try fallback URL
    const fallbackUrl = img.dataset.fallback;
    if (fallbackUrl && fallbackUrl !== img.src && fallbackUrl !== 'null' && fallbackUrl !== '') {
        console.log(`Trying fallback URL for image ${img.dataset.index}`);
        img.dataset.tried = 'true';
        // Add a small delay to avoid rapid fire requests
        setTimeout(() => {
            img.src = fallbackUrl;
        }, 500);
    } else {
        // No valid fallback available, show error
        const errorDiv = document.createElement('div');
        errorDiv.className = 'image-error';
        errorDiv.innerHTML = '📷<br><span style="font-size: 12px;">Image unavailable</span>';
        img.parentElement.replaceChild(errorDiv, img);
    }
}

// Select a photo from the grid
function selectPhoto(index) {
    const input = document.getElementById('promptInput');
    input.value = `use image ${index}`;
    sendMessage();
}