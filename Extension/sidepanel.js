// API Configuration
const MASTER_AGENT_API = 'http://localhost:9000/chat';
const INSIGHTS_AGENT_API = 'http://localhost:8008/process';
const PDF_EXTRACTOR_API = 'http://localhost:8007/extract';

// State
let conversationHistory = [];
let uploadedDocuments = [];

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const uploadIconBtn = document.getElementById('uploadIconBtn');
const uploadSection = document.getElementById('uploadSection');
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const uploadedFiles = document.getElementById('uploadedFiles');
const insightsBanner = document.getElementById('insightsBanner');
const insightsContent = document.getElementById('insightsContent');
const insightsClose = document.getElementById('insightsClose');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  loadConversationHistory();
});

function setupEventListeners() {
  // Send message
  sendBtn.addEventListener('click', sendMessage);
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Auto-resize textarea
  chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
  });

  // Toggle upload section
  uploadIconBtn.addEventListener('click', toggleUploadSection);

  // File upload
  fileInput.addEventListener('change', handleFileSelect);
  uploadArea.addEventListener('click', () => fileInput.click());
  
  // Drag and drop
  uploadArea.addEventListener('dragover', handleDragOver);
  uploadArea.addEventListener('dragleave', handleDragLeave);
  uploadArea.addEventListener('drop', handleDrop);
  
  // Also allow drag and drop on the upload section when visible
  uploadSection.addEventListener('dragover', (e) => {
    if (uploadSection.classList.contains('show')) {
      handleDragOver(e);
    }
  });
  uploadSection.addEventListener('dragleave', (e) => {
    if (uploadSection.classList.contains('show')) {
      handleDragLeave(e);
    }
  });
  uploadSection.addEventListener('drop', (e) => {
    if (uploadSection.classList.contains('show')) {
      handleDrop(e);
    }
  });

  // Close insights banner
  insightsClose.addEventListener('click', hideInsightsBanner);
}

function toggleUploadSection() {
  const isShowing = uploadSection.classList.contains('show');
  
  if (isShowing) {
    // Hide with animation
    uploadSection.classList.remove('show');
    uploadIconBtn.classList.remove('active');
    setTimeout(() => {
      uploadSection.style.display = 'none';
    }, 300);
  } else {
    // Show with animation
    uploadSection.style.display = 'block';
    // Force reflow to ensure display is set before adding class
    uploadSection.offsetHeight;
    uploadSection.classList.add('show');
    uploadIconBtn.classList.add('active');
  }
}

function handleDragOver(e) {
  e.preventDefault();
  uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
  e.preventDefault();
  uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
  e.preventDefault();
  uploadArea.classList.remove('drag-over');
  
  const files = Array.from(e.dataTransfer.files).filter(file => file.type === 'application/pdf');
  if (files.length > 0) {
    processFiles(files);
  }
}

function handleFileSelect(e) {
  const files = Array.from(e.target.files).filter(file => file.type === 'application/pdf');
  if (files.length > 0) {
    processFiles(files);
  }
  // Reset input to allow re-uploading the same file
  e.target.value = '';
}

async function processFiles(files) {
  for (const file of files) {
    await uploadPDF(file);
  }
}

async function uploadPDF(file) {
  // Add file to UI
  const fileId = Date.now() + Math.random();
  const fileElement = createFileElement(file.name, fileId, 'processing');
  uploadedFiles.appendChild(fileElement);

  try {
    // Create FormData
    const formData = new FormData();
    formData.append('pdf_file', file);
    formData.append('summarize', 'true');
    formData.append('detail_level', 'detailed');

    // Upload to PDF extractor API
    const response = await fetch(PDF_EXTRACTOR_API, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    const result = await response.json();

    if (result.success) {
      // Store document summary
      const documentSummary = {
        file_name: file.name,
        summary: result.summary || result.text?.substring(0, 1000) + '...',
        text: result.text,
        metadata: result.metadata || {}
      };

      uploadedDocuments.push(documentSummary);

      // Update UI
      updateFileElement(fileId, 'success', 'Uploaded successfully');
      
      // Show success message
      addMessage('bot', `Document "${file.name}" uploaded successfully! I can now reference it in our conversation.`);
    } else {
      throw new Error(result.error || 'Upload failed');
    }
  } catch (error) {
    console.error('Error uploading PDF:', error);
    updateFileElement(fileId, 'error', error.message);
    addMessage('bot', `Failed to upload "${file.name}": ${error.message}`);
  }
}

function createFileElement(fileName, fileId, status) {
  const div = document.createElement('div');
  div.className = 'uploaded-file';
  div.dataset.fileId = fileId;
  div.innerHTML = `
    <span class="file-icon">📄</span>
    <span class="file-name">${fileName}</span>
    <span class="file-status ${status}">${getStatusText(status)}</span>
  `;
  return div;
}

function updateFileElement(fileId, status, text) {
  const element = document.querySelector(`[data-file-id="${fileId}"]`);
  if (element) {
    const statusElement = element.querySelector('.file-status');
    statusElement.className = `file-status ${status}`;
    statusElement.textContent = text;
  }
}

function getStatusText(status) {
  switch (status) {
    case 'processing': return 'Processing...';
    case 'success': return 'Success';
    case 'error': return 'Error';
    default: return 'Unknown';
  }
}

async function sendMessage() {
  const message = chatInput.value.trim();
  if (!message) return;

  // Add user message to UI
  addMessage('user', message);
  chatInput.value = '';
  chatInput.style.height = 'auto';

  // Show typing indicator
  const typingId = showTypingIndicator();

  try {
    // Get page summaries from chrome.storage (shared with content script)
    let pageSummaries = [];
    try {
      const result = await new Promise((resolve) => {
        chrome.storage.local.get(['page_summaries'], resolve);
      });
      
      if (result.page_summaries && Array.isArray(result.page_summaries)) {
        pageSummaries = result.page_summaries;
        console.log('[Page Summaries] Loaded from chrome.storage:', pageSummaries.length, 'summaries');
        
        // Log summary details for debugging
        pageSummaries.forEach((summary, idx) => {
          console.log(`  Summary ${idx + 1}: ${summary.title} (${summary.travel_context})`);
        });
      } else {
        console.log('[Page Summaries] No summaries found in chrome.storage');
      }
    } catch (error) {
      console.error('[Page Summaries] Error loading from chrome.storage:', error);
    }
    
    // Prepare request
    const requestBody = {
      message: message,
      conversation_history: conversationHistory,
      document_summaries: uploadedDocuments,
      page_summaries: pageSummaries
    };

    // Send to master agent API FIRST
    console.log('[Master Agent] Sending request to:', MASTER_AGENT_API);
    console.log('[Master Agent] Request body:', requestBody);
    
    const response = await fetch(MASTER_AGENT_API, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });

    console.log('[Master Agent] Response status:', response.status, response.statusText);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('[Master Agent] Error response:', errorText);
      throw new Error(`API request failed: ${response.statusText}`);
    }

    const result = await response.json();
    
    console.log('[Master Agent] Response received:', result);

    // Remove typing indicator
    removeTypingIndicator(typingId);

    if (result.success) {
      // Update conversation history
      conversationHistory = result.conversation_history || conversationHistory;
      
      console.log('[Master Agent] Adding bot response to chat:', result.response);
      
      // Add bot response
      addMessage('bot', result.response);
      
      // Save conversation history
      saveConversationHistory();
      
      // NOW send to insights agent API (after master agent completes)
      fetchAndDisplayInsights(message);
    } else {
      console.error('[Master Agent] Response indicated failure:', result);
      throw new Error(result.error || 'Unknown error');
    }
  } catch (error) {
    console.error('Error sending message:', error);
    removeTypingIndicator(typingId);
    addMessage('bot', `Error: ${error.message}. Please make sure the API server is running.`);
  }
}

function addMessage(type, content) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${type}-message`;

  const avatar = document.createElement('div');
  avatar.className = 'message-avatar';
  avatar.textContent = type === 'user' ? '👤' : '🤖';

  const contentDiv = document.createElement('div');
  contentDiv.className = 'message-content';

  // Format message content (support basic markdown-like formatting)
  const formattedContent = formatMessage(content);
  contentDiv.innerHTML = formattedContent;

  messageDiv.appendChild(avatar);
  messageDiv.appendChild(contentDiv);
  chatMessages.appendChild(messageDiv);

  // Scroll to bottom
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatMessage(text) {
  // Convert newlines to <br>
  let formatted = text.replace(/\n/g, '<br>');
  
  // Convert code blocks (```code```)
  formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre>$1</pre>');
  
  // Convert inline code (`code`)
  formatted = formatted.replace(/`([^`]+)`/g, '<code style="background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px; font-size: 0.9em;">$1</code>');
  
  // Convert **bold**
  formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  
  return formatted;
}

function showTypingIndicator() {
  const typingId = 'typing-' + Date.now();
  const messageDiv = document.createElement('div');
  messageDiv.className = 'message bot-message';
  messageDiv.id = typingId;

  const avatar = document.createElement('div');
  avatar.className = 'message-avatar';
  avatar.textContent = '🤖';

  const contentDiv = document.createElement('div');
  contentDiv.className = 'message-content typing-indicator';
  contentDiv.innerHTML = '<span></span><span></span><span></span>';

  messageDiv.appendChild(avatar);
  messageDiv.appendChild(contentDiv);
  chatMessages.appendChild(messageDiv);

  chatMessages.scrollTop = chatMessages.scrollHeight;
  return typingId;
}

function removeTypingIndicator(typingId) {
  const element = document.getElementById(typingId);
  if (element) {
    element.remove();
  }
}

function saveConversationHistory() {
  chrome.storage.local.set({ conversationHistory, uploadedDocuments });
}

function loadConversationHistory() {
  chrome.storage.local.get(['conversationHistory', 'uploadedDocuments'], (result) => {
    if (result.conversationHistory) {
      conversationHistory = result.conversationHistory;
    }
    if (result.uploadedDocuments) {
      uploadedDocuments = result.uploadedDocuments;
      // Restore uploaded files UI
      uploadedDocuments.forEach((doc, index) => {
        const fileId = 'restored-' + index;
        const fileElement = createFileElement(doc.file_name, fileId, 'success');
        uploadedFiles.appendChild(fileElement);
        updateFileElement(fileId, 'success', 'Restored');
      });
    }
  });
}

// ============================================================================
// Insights Banner Functions
// ============================================================================

/**
 * Fetch insights from the Insights Agent API and display them
 * @param {string} userMessage - The user's message
 */
async function fetchAndDisplayInsights(userMessage) {
  try {
    console.log('[Insights] Checking if insights needed for message:', userMessage);
    
    const response = await fetch(INSIGHTS_AGENT_API, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query: userMessage }),
      signal: AbortSignal.timeout(30000) // 30 second timeout
    });

    if (!response.ok) {
      console.warn('[Insights] API request failed:', response.statusText);
      return;
    }

    const result = await response.json();
    
    console.log('[Insights] Decision result:', {
      should_analyze: result.should_analyze,
      performed_analytics: result.performed_analytics,
      confidence: result.confidence,
      reasoning: result.reasoning
    });

    // Display insights if they were generated
    if (result.should_analyze && result.performed_analytics && result.insights) {
      showInsightsBanner(result.insights);
      console.log('[Insights] Displayed insights banner');
    } else {
      console.log('[Insights] No insights to display:', result.reasoning);
    }
    
  } catch (error) {
    // Insights are optional, so just log the error
    if (error.name === 'TimeoutError') {
      console.warn('[Insights] Request timed out (non-critical)');
    } else if (error.name === 'AbortError') {
      console.warn('[Insights] Request aborted (non-critical)');
    } else {
      console.warn('[Insights] Error fetching insights (non-critical):', error);
    }
  }
}

/**
 * Show the insights banner with content
 * @param {string} insights - The insights text to display
 */
function showInsightsBanner(insights) {
  if (!insights) return;
  
  // Set the content
  insightsContent.textContent = insights;
  
  // Show the banner with animation
  insightsBanner.style.display = 'block';
  
  // Force reflow to ensure display is set before adding class
  insightsBanner.offsetHeight;
  
  // Add visible class for animation
  setTimeout(() => {
    insightsBanner.classList.add('visible');
  }, 10);
}

/**
 * Hide the insights banner
 */
function hideInsightsBanner() {
  insightsBanner.classList.remove('visible');
  
  // Wait for animation to complete before hiding
  setTimeout(() => {
    insightsBanner.style.display = 'none';
  }, 300);
}

