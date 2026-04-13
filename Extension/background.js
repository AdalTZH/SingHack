// Background service worker for Chrome extension

chrome.runtime.onInstalled.addListener(() => {
  console.log('SingPass Insurance Chat extension installed');
});

// Handle side panel opening
chrome.sidePanel.setOptions({
  path: 'sidepanel.html',
  enabled: true
});

// Helper function to inject content script if needed
async function injectContentScriptIfNeeded(tabId, url) {
  try {
    // First, check if content script is already loaded by trying to send a ping
    try {
      await chrome.tabs.sendMessage(tabId, { action: 'ping' });
      console.log('Content script already loaded on tab:', url);
      return true;
    } catch (pingError) {
      // Content script not loaded, need to inject it
      console.log('Content script not loaded, injecting for tab:', url);
      
      try {
        // Inject CSS first
        await chrome.scripting.insertCSS({
          target: { tabId: tabId },
          files: ['cursor-textbox.css']
        });
        
        // Then inject JS
        await chrome.scripting.executeScript({
          target: { tabId: tabId },
          files: ['content.js']
        });
        
        console.log('Successfully injected content script for tab:', url);
        
        // Wait for script to initialize
        await new Promise(resolve => setTimeout(resolve, 500));
        return true;
      } catch (injectError) {
        console.error('Failed to inject content script:', injectError.message);
        return false;
      }
    }
  } catch (error) {
    console.error('Error in injectContentScriptIfNeeded:', error);
    return false;
  }
}

// Helper function to send message to content script with retries
async function sendAnalyzeMessage(tabId, url) {
  try {
    // First, ensure content script is loaded
    const injected = await injectContentScriptIfNeeded(tabId, url);
    
    if (!injected) {
      console.warn('Cannot send message - content script injection failed');
      return;
    }
    
    // Try to send message with retries
    let retries = 3;
    let lastError = null;
    
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const response = await chrome.tabs.sendMessage(tabId, {
          action: 'analyzePageOnTabSwitch'
        });
        console.log(`Successfully sent analyze message to tab (attempt ${attempt}):`, url);
        return response;
      } catch (err) {
        lastError = err;
        console.log(`Attempt ${attempt} failed for tab ${url}:`, err.message);
        
        if (attempt < retries) {
          // Wait before retry
          await new Promise(resolve => setTimeout(resolve, 300));
        }
      }
    }
    
    // If all retries failed, log the error
    console.warn('Failed to send message to content script after all retries:', {
      url: url,
      error: lastError?.message,
      tabId: tabId
    });
  } catch (error) {
    console.error('Error in sendAnalyzeMessage:', error);
  }
}

// Listen for tab activation (when user switches tabs)
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  try {
    // Get the active tab
    const tab = await chrome.tabs.get(activeInfo.tabId);
    
    // Only process http/https pages (skip chrome://, extension://, etc.)
    if (tab.url && (tab.url.startsWith('http://') || tab.url.startsWith('https://'))) {
      console.log('Tab activated:', tab.url, 'status:', tab.status);
      
      // For already-loaded tabs, we can send with shorter delay
      // For loading tabs, wait a bit longer for content script to initialize
      const delay = tab.status === 'complete' ? 100 : 500;
      
      setTimeout(() => {
        sendAnalyzeMessage(activeInfo.tabId, tab.url);
      }, delay);
    }
  } catch (error) {
    console.error('Error handling tab activation:', error);
  }
});

// Also listen for tab updates (when tab URL changes)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  // Only process when tab is complete and URL is http/https
  if (changeInfo.status === 'complete' && tab.url && 
      (tab.url.startsWith('http://') || tab.url.startsWith('https://'))) {
    // Check if this is the active tab
    chrome.tabs.query({ active: true, currentWindow: true }, (activeTabs) => {
      if (activeTabs.length > 0 && activeTabs[0].id === tabId) {
        console.log('Active tab updated:', tab.url);
        
        // Send analyze message with a short delay
        setTimeout(() => {
          sendAnalyzeMessage(tabId, tab.url);
        }, 300);
      }
    });
  }
});

// Handle messages from content scripts to make API requests (bypasses CORS)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'summarizePage') {
    // Handle Summary Agent requests
    const requestBody = {
      inner_text: String(request.inner_text || ''),
      url: String(request.url || ''),
      title: String(request.title || ''),
      travel_context: String(request.travel_context || '')
    };
    
    // Validate required fields
    if (!requestBody.inner_text || !requestBody.url || !requestBody.title) {
      const error = 'Missing required fields: inner_text, url, or title';
      console.error('Summary Agent validation error:', error);
      sendResponse({ success: false, error: error });
      return true;
    }
    
    console.log('Background: Sending request to summary agent:', {
      url: requestBody.url,
      title: requestBody.title,
      inner_text_length: requestBody.inner_text.length,
      travel_context: requestBody.travel_context
    });
    
    // Make the API request from background script (bypasses CORS)
    fetch('http://localhost:8020/summarize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    })
    .then(async response => {
      const responseData = await response.json().catch(() => ({}));
      
      if (!response.ok) {
        let errorMessage;
        if (typeof responseData.detail === 'string') {
          errorMessage = responseData.detail;
        } else if (typeof responseData.detail === 'object') {
          errorMessage = JSON.stringify(responseData.detail);
        } else if (responseData.message) {
          errorMessage = responseData.message;
        } else {
          errorMessage = `HTTP error! status: ${response.status}`;
        }
        
        console.error('Summary Agent API Error:', {
          status: response.status,
          statusText: response.statusText,
          detail: responseData,
          errorMessage: errorMessage
        });
        throw new Error(errorMessage);
      }
      return responseData;
    })
    .then(data => {
      console.log('Background: Received successful response from summary agent');
      sendResponse({ success: true, data: data });
    })
    .catch(error => {
      console.error('Error in background fetch (summary agent):', error);
      const errorMsg = error.message || String(error);
      sendResponse({ success: false, error: errorMsg });
    });
    
    // Return true to indicate we will send a response asynchronously
    return true;
  }
  
  if (request.action === 'analyzePage') {
    // Prepare request body - ensure all fields are valid
    const requestBody = {
      url: String(request.url || ''),
      title: String(request.title || ''),
      inner_text: String(request.inner_text || ''),
      timestamp: request.timestamp || new Date().toISOString()
    };
    
    // Validate required fields
    if (!requestBody.url || !requestBody.title || !requestBody.inner_text) {
      const error = 'Missing required fields: url, title, or inner_text';
      console.error('Validation error:', error, requestBody);
      sendResponse({ success: false, error: error });
      return true;
    }
    
    // Log request for debugging
    console.log('Background: Sending request to decision agent:', {
      url: requestBody.url,
      title: requestBody.title,
      inner_text_length: requestBody.inner_text?.length || 0,
      timestamp: requestBody.timestamp
    });
    
    // Make the API request from background script (bypasses CORS)
    fetch('http://localhost:8004/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    })
    .then(async response => {
      const responseData = await response.json().catch(() => ({}));
      
      if (!response.ok) {
        // Get detailed error message from response
        let errorMessage;
        if (typeof responseData.detail === 'string') {
          errorMessage = responseData.detail;
        } else if (typeof responseData.detail === 'object') {
          errorMessage = JSON.stringify(responseData.detail);
        } else if (responseData.message) {
          errorMessage = responseData.message;
        } else {
          errorMessage = `HTTP error! status: ${response.status}`;
        }
        
        console.error('API Error:', {
          status: response.status,
          statusText: response.statusText,
          detail: responseData,
          errorMessage: errorMessage
        });
        console.error('Full response data:', JSON.stringify(responseData, null, 2));
        throw new Error(errorMessage);
      }
      return responseData;
    })
    .then(data => {
      console.log('Background: Received successful response from decision agent');
      sendResponse({ success: true, data: data });
    })
    .catch(error => {
      console.error('Error in background fetch:', error);
      // Ensure error message is a string
      const errorMsg = error.message || String(error);
      sendResponse({ success: false, error: errorMsg });
    });
    
    // Return true to indicate we will send a response asynchronously
    return true;
  }
});

