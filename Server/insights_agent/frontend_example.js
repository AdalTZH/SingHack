/**
 * Frontend Integration Example for Insights Agent
 * 
 * This shows how to integrate the Insights Agent into your chat extension
 */

// ============================================================================
// Configuration
// ============================================================================

const INSIGHTS_AGENT_URL = 'http://localhost:8008';

// ============================================================================
// API Functions
// ============================================================================

/**
 * Fetch insights for a user query
 * @param {string} userQuery - The user's query
 * @returns {Promise<Object>} Insights result
 */
async function getInsights(userQuery) {
  try {
    const response = await fetch(`${INSIGHTS_AGENT_URL}/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: userQuery }),
      // Increased timeout as analytics can take 5-10 seconds
      signal: AbortSignal.timeout(30000)
    });

    if (!response.ok) {
      console.error('Insights API error:', response.status);
      return {
        should_analyze: false,
        performed_analytics: false,
        insights: null
      };
    }

    const data = await response.json();

    // Log for debugging
    console.log('Insights Decision:', {
      should_analyze: data.should_analyze,
      performed_analytics: data.performed_analytics,
      confidence: data.confidence,
      reasoning: data.reasoning
    });

    return data;

  } catch (error) {
    if (error.name === 'TimeoutError') {
      console.error('Insights request timed out');
    } else {
      console.error('Failed to fetch insights:', error);
    }
    
    // Return safe default on error
    return {
      should_analyze: false,
      performed_analytics: false,
      insights: null
    };
  }
}

// ============================================================================
// UI Functions
// ============================================================================

/**
 * Display insights banner at top of chat
 * @param {string} insightsText - The insights text to display
 * @param {HTMLElement} chatContainer - The chat container element
 */
function displayInsights(insightsText, chatContainer) {
  // Remove any existing insights banner
  const existingBanner = chatContainer.querySelector('.insights-banner');
  if (existingBanner) {
    existingBanner.remove();
  }

  // Create insights banner
  const insightsElement = document.createElement('div');
  insightsElement.className = 'insights-banner';
  insightsElement.innerHTML = `
    <div class="insights-header">
      <span class="insights-icon">💡</span>
      <span class="insights-title">Insights</span>
      <button class="insights-close" aria-label="Close insights">×</button>
    </div>
    <div class="insights-content">
      ${escapeHtml(insightsText)}
    </div>
  `;

  // Add close button handler
  const closeButton = insightsElement.querySelector('.insights-close');
  closeButton.addEventListener('click', () => {
    insightsElement.remove();
  });

  // Insert at top of chat
  chatContainer.insertBefore(insightsElement, chatContainer.firstChild);

  // Animate in
  setTimeout(() => {
    insightsElement.classList.add('insights-banner-visible');
  }, 10);
}

/**
 * Show loading state for insights
 * @param {HTMLElement} chatContainer - The chat container element
 */
function showInsightsLoading(chatContainer) {
  const loadingElement = document.createElement('div');
  loadingElement.className = 'insights-banner insights-loading';
  loadingElement.innerHTML = `
    <div class="insights-header">
      <span class="insights-icon">💡</span>
      <span class="insights-title">Analyzing insights...</span>
    </div>
    <div class="insights-content">
      <div class="loading-spinner"></div>
    </div>
  `;

  chatContainer.insertBefore(loadingElement, chatContainer.firstChild);
}

/**
 * Hide insights loading state
 * @param {HTMLElement} chatContainer - The chat container element
 */
function hideInsightsLoading(chatContainer) {
  const loadingElement = chatContainer.querySelector('.insights-loading');
  if (loadingElement) {
    loadingElement.remove();
  }
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

// ============================================================================
// Main Integration Function
// ============================================================================

/**
 * Handle user message with insights integration
 * @param {string} userMessage - The user's message
 * @param {HTMLElement} chatContainer - The chat container element
 */
async function handleUserMessageWithInsights(userMessage, chatContainer) {
  // Show loading state (optional)
  showInsightsLoading(chatContainer);

  // Get insights in parallel with normal chat processing
  const insightsPromise = getInsights(userMessage);

  // Continue with your normal chat flow
  // sendMessageToChat(userMessage);
  // ...

  // Wait for insights
  const insightsResult = await insightsPromise;

  // Hide loading
  hideInsightsLoading(chatContainer);

  // Display insights if available
  if (insightsResult.should_analyze && 
      insightsResult.performed_analytics && 
      insightsResult.insights) {
    displayInsights(insightsResult.insights, chatContainer);
  }
}

// ============================================================================
// Example Usage
// ============================================================================

/**
 * Example: Initialize chat with insights
 */
function initializeChat() {
  const chatContainer = document.getElementById('chat-container');
  const messageInput = document.getElementById('message-input');
  const sendButton = document.getElementById('send-button');

  sendButton.addEventListener('click', async () => {
    const userMessage = messageInput.value.trim();
    
    if (!userMessage) return;

    // Clear input
    messageInput.value = '';

    // Add user message to chat
    addMessageToChat('user', userMessage, chatContainer);

    // Process with insights
    await handleUserMessageWithInsights(userMessage, chatContainer);
  });
}

/**
 * Example: Add message to chat
 */
function addMessageToChat(role, content, chatContainer) {
  const messageElement = document.createElement('div');
  messageElement.className = `chat-message chat-message-${role}`;
  messageElement.textContent = content;
  chatContainer.appendChild(messageElement);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

// ============================================================================
// CSS (Add to your stylesheet)
// ============================================================================

const CSS_STYLES = `
/* Insights Banner */
.insights-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  opacity: 0;
  transform: translateY(-10px);
  transition: all 0.3s ease;
}

.insights-banner-visible {
  opacity: 1;
  transform: translateY(0);
}

.insights-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 8px;
}

.insights-icon {
  font-size: 18px;
}

.insights-title {
  flex: 1;
}

.insights-close {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s;
}

.insights-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.insights-content {
  font-size: 14px;
  line-height: 1.6;
  opacity: 0.95;
}

/* Loading State */
.insights-loading {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Chat Messages */
.chat-message {
  padding: 12px 16px;
  margin-bottom: 12px;
  border-radius: 8px;
  max-width: 80%;
}

.chat-message-user {
  background: #e3f2fd;
  color: #1565c0;
  align-self: flex-end;
  margin-left: auto;
}

.chat-message-assistant {
  background: #f5f5f5;
  color: #333;
  align-self: flex-start;
}
`;

// ============================================================================
// Alternative: Simpler Integration
// ============================================================================

/**
 * Simpler integration - just check and display
 */
async function simpleInsightsIntegration(userMessage, chatContainer) {
  const result = await getInsights(userMessage);
  
  if (result.insights) {
    displayInsights(result.insights, chatContainer);
  }
}

// ============================================================================
// Export for use in your extension
// ============================================================================

// If using modules:
// export { getInsights, displayInsights, handleUserMessageWithInsights };

// If using global scope:
window.InsightsIntegration = {
  getInsights,
  displayInsights,
  handleUserMessageWithInsights,
  showInsightsLoading,
  hideInsightsLoading
};

// Example initialization
// document.addEventListener('DOMContentLoaded', initializeChat);



