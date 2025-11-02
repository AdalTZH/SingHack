// Sidepanel JavaScript
let apiKey = '';
let temperature = 0.7;

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const sendImageBtn = document.getElementById('sendImageBtn');
const settingsBtn = document.getElementById('settingsBtn');
const settingsModal = document.getElementById('settingsModal');
const closeSettings = document.getElementById('closeSettings');
const saveSettings = document.getElementById('saveSettings');
const temperatureInput = document.getElementById('temperature');
const tempValue = document.getElementById('tempValue');
const paymentBtn = document.getElementById('paymentBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadSettings();
    setupEventListeners();
    autoResizeTextarea();
    setupPageSummaryListener();
});

// Load settings from storage
async function loadSettings() {
    try {
        // API key is now preconfigured in background.js
        // Only load temperature from storage
        const result = await chrome.storage.sync.get(['temperature']);
        temperature = result.temperature ?? 0.7;
        
        temperatureInput.value = temperature;
        tempValue.textContent = temperature;
        
        // Always set apiKey to indicate it's configured
        apiKey = 'configured';
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    sendBtn.addEventListener('click', handleSendMessage);
    sendImageBtn.addEventListener('click', handleSendImage);
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    
    settingsBtn.addEventListener('click', () => {
        settingsModal.classList.add('show');
    });
    
    closeSettings.addEventListener('click', () => {
        settingsModal.classList.remove('show');
    });
    
    saveSettings.addEventListener('click', handleSaveSettings);
    
    temperatureInput.addEventListener('input', (e) => {
        tempValue.textContent = e.target.value;
    });
    
    paymentBtn.addEventListener('click', handlePaymentClick);
    
    // Close modal when clicking outside
    settingsModal.addEventListener('click', (e) => {
        if (e.target === settingsModal) {
            settingsModal.classList.remove('show');
        }
    });
}

// Auto-resize textarea
function autoResizeTextarea() {
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = messageInput.scrollHeight + 'px';
    });
}

// Handle save settings
async function handleSaveSettings() {
    const newTemperature = parseFloat(temperatureInput.value);
    
    temperature = newTemperature;
    
    try {
        await chrome.storage.sync.set({
            temperature: temperature
        });
        settingsModal.classList.remove('show');
        clearError();
    } catch (error) {
        console.error('Error saving settings:', error);
        showError('Failed to save settings');
    }
}

// Handle send message
async function handleSendMessage() {
    const message = messageInput.value.trim();
    if (!message || !apiKey) {
        if (!apiKey) {
            showError('Please configure your API key in settings');
            settingsModal.classList.add('show');
        }
        return;
    }
    
    // Clear welcome message if present
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    // Add user message
    addMessage(message, 'user');
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // Disable input while processing
    setInputState(false);
    
    // Add loading indicator
    const loadingId = addLoadingIndicator();
    
    try {
        // Send to background script for API call (apiKey and model are configured there)
        const response = await chrome.runtime.sendMessage({
            type: 'chat',
            message: message,
            temperature: temperature
        });
        
        removeLoadingIndicator(loadingId);
        
        if (response.error) {
            showError(response.error);
        } else {
            addMessage(response.message, 'assistant');
        }
    } catch (error) {
        removeLoadingIndicator(loadingId);
        console.error('Error sending message:', error);
        showError('Failed to send message. Please try again.');
    } finally {
        setInputState(true);
    }
}

// Add message to chat
function addMessage(text, role, isImage = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (isImage && role === 'user') {
        // For image messages, display an indicator
        const imageIndicator = document.createElement('div');
        imageIndicator.style.cssText = 'display: flex; align-items: center; gap: 8px;';
        imageIndicator.innerHTML = `
            <span>📸</span>
            <span>${text}</span>
        `;
        contentDiv.appendChild(imageIndicator);
    } else {
        contentDiv.textContent = text;
    }
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Add loading indicator
function addLoadingIndicator() {
    const loadingId = Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.id = `loading-${loadingId}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content loading-indicator';
    contentDiv.innerHTML = `
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
    `;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return loadingId;
}

// Remove loading indicator
function removeLoadingIndicator(id) {
    const loadingElement = document.getElementById(`loading-${id}`);
    if (loadingElement) {
        loadingElement.remove();
    }
}

// Set input state
function setInputState(enabled) {
    messageInput.disabled = !enabled;
    sendBtn.disabled = !enabled;
    sendImageBtn.disabled = !enabled;
}

// Handle send image (screenshot)
async function handleSendImage() {
    if (!apiKey) {
        showError('Please configure your API key in settings');
        settingsModal.classList.add('show');
        return;
    }
    
    // Clear welcome message if present
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    // Add user message indicating screenshot is being sent
    const optionalText = messageInput.value.trim();
    addMessage(optionalText || '📸 Screenshot', 'user', true);
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // Disable input while processing
    setInputState(false);
    
    // Add loading indicator
    const loadingId = addLoadingIndicator();
    
    try {
        // Get current tab info to pass to background script
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        if (!tab) {
            throw new Error('No active tab found');
        }
        
        // Request screenshot capture from background script
        // Background script can use activeTab permission when extension is invoked
        const captureResponse = await chrome.runtime.sendMessage({
            type: 'captureScreenshot',
            tabId: tab.id
        });
        
        if (captureResponse.error) {
            throw new Error(captureResponse.error);
        }
        
        if (!captureResponse.dataUrl) {
            throw new Error('Failed to capture screenshot');
        }
        
        // Send to background script for API call
        const response = await chrome.runtime.sendMessage({
            type: 'chat',
            message: optionalText || 'Please analyze this screenshot.',
            image: captureResponse.dataUrl,
            temperature: temperature
        });
        
        removeLoadingIndicator(loadingId);
        
        if (response.error) {
            showError(response.error);
        } else {
            addMessage(response.message, 'assistant');
        }
    } catch (error) {
        removeLoadingIndicator(loadingId);
        console.error('Error sending image:', error);
        showError('Failed to capture or send screenshot. Please try again.');
    } finally {
        setInputState(true);
    }
}

// Show error
function showError(message) {
    clearError();
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    chatMessages.appendChild(errorDiv);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Clear error
function clearError() {
    const errorMsg = document.querySelector('.error-message');
    if (errorMsg) {
        errorMsg.remove();
    }
}

/**
 * Setup listener for page explanations from background script
 */
function setupPageSummaryListener() {
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.type === 'pageExplanation') {
            displayPageExplanation(message);
        }
    });
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Handle payment button click - creates Stripe checkout session and redirects to payment page
 */
async function handlePaymentClick() {
    try {
        // Disable button during processing
        paymentBtn.disabled = true;
        paymentBtn.style.opacity = '0.6';
        
        // Call payment API to create checkout session
        const response = await fetch('http://localhost:8085/create-checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                amount: 5000, // $50 in cents
                product_name: 'Travel Insurance - Standard Plan',
                currency: 'SGD'
            })
        });
        
        if (!response.ok) {
            throw new Error(`Payment API returned ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Open Stripe checkout page in a new tab
        chrome.tabs.create({ url: data.checkout_url });
        
        // Re-enable button
        paymentBtn.disabled = false;
        paymentBtn.style.opacity = '1';
        
    } catch (error) {
        console.error('Error creating payment checkout:', error);
        showError('Failed to create payment checkout. Please check if the payment service is running on localhost:8085.');
        
        // Re-enable button
        paymentBtn.disabled = false;
        paymentBtn.style.opacity = '1';
    }
}

/**
 * Display page explanation in the chatbot interface
 * @param {Object} data - Explanation data containing url, title, explanation, timestamp
 */
function displayPageExplanation(data) {
    // Clear welcome message if present
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    // Create a special message div for page explanation with better formatting
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Escape user-provided content to prevent XSS
    const safeTitle = escapeHtml(data.title || 'Untitled');
    const safeUrl = escapeHtml(data.url || '');
    const safeExplanation = escapeHtml(data.explanation || 'No explanation available');
    
    // Create formatted explanation with HTML to preserve line breaks
    const explanationHTML = `
        <div style="margin-bottom: 8px;">
            <strong style="display: flex; align-items: center; gap: 6px;">
                <span>📄</span>
                <span>Page Explanation</span>
            </strong>
        </div>
        <div style="margin-bottom: 8px; font-size: 0.9em; color: #666;">
            <div style="font-weight: 500; margin-bottom: 4px;">${safeTitle}</div>
            <div style="word-break: break-all; font-size: 0.85em; color: #888;">${safeUrl}</div>
        </div>
        <div style="white-space: pre-wrap; line-height: 1.6;">${safeExplanation}</div>
    `;
    
    contentDiv.innerHTML = explanationHTML;
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

