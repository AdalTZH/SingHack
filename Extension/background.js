// Background Service Worker

// Import configuration from external file
importScripts('config.js');

// Model configuration
const DEFAULT_MODEL = 'gpt-4o-mini';

chrome.runtime.onInstalled.addListener(() => {
    console.log('AI Chat Assistant installed');
});

// Listen for messages from sidepanel
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'chat') {
        handleChatMessage(request)
            .then(response => sendResponse(response))
            .catch(error => {
                console.error('Chat error:', error);
                sendResponse({ error: error.message || 'An error occurred' });
            });
        return true; // Indicates we'll send a response asynchronously
    }
    
    if (request.type === 'captureScreenshot') {
        handleCaptureScreenshot(request)
            .then(response => sendResponse(response))
            .catch(error => {
                console.error('Screenshot capture error:', error);
                sendResponse({ error: error.message || 'Failed to capture screenshot' });
            });
        return true; // Indicates we'll send a response asynchronously
    }
});

// Handle chat message - supports both Master Agent and direct OpenAI
async function handleChatMessage(request) {
    const { message, temperature, image } = request;
    
    // Check if we should use Master Agent or direct OpenAI
    const useMasterAgent = CONFIG.USE_MASTER_AGENT === true;
    
    if (useMasterAgent) {
        return handleMasterAgentChat(request);
    } else {
        return handleDirectOpenAIChat(request);
    }
}

// Handle chat message via Master Agent
async function handleMasterAgentChat(request) {
    const { message, temperature, image } = request;
    
    try {
        // Note: Images not yet supported in Master Agent mode
        if (image) {
            throw new Error('Image analysis not yet supported in Master Agent mode');
        }
        
        const masterAgentUrl = CONFIG.MASTER_AGENT_URL || 'http://localhost:8000';
        
        const response = await fetch(`${masterAgentUrl}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                temperature: temperature
            })
        });
        
        if (!response.ok) {
            throw new Error(`Master Agent returned ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            return {
                message: data.response,
                metadata: data
            };
        } else {
            throw new Error(data.error || 'Master Agent returned error');
        }
    } catch (error) {
        console.error('Master Agent error:', error);
        throw error;
    }
}

// Handle chat message via direct OpenAI API
async function handleDirectOpenAIChat(request) {
    const { message, temperature, image } = request;
    
    // Use the API key from config file and default model
    const apiKey = CONFIG.OPENAI_API_KEY;
    const model = DEFAULT_MODEL;
    
    if (!apiKey || apiKey === 'YOUR_API_KEY_HERE' || !apiKey.startsWith('sk-')) {
        throw new Error('Invalid API key. Please configure your API key in config.js');
    }
    
    try {
        // Build the message content - support both text and image
        let messageContent;
        
        if (image) {
            // If image is provided, use the content array format with image_url
            messageContent = [
                {
                    type: 'text',
                    text: message
                },
                {
                    type: 'image_url',
                    image_url: {
                        url: image
                    }
                }
            ];
        } else {
            // Text-only message
            messageContent = message;
        }
        
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: model,
                messages: [
                    {
                        role: 'user',
                        content: messageContent
                    }
                ],
                temperature: temperature,
                max_tokens: 1000
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error?.message || 'Failed to get response from OpenAI');
        }
        
        const data = await response.json();
        return {
            message: data.choices[0].message.content.trim()
        };
    } catch (error) {
        console.error('OpenAI API error:', error);
        throw error;
    }
}

// Handle screenshot capture request
async function handleCaptureScreenshot(request) {
    try {
        // Get the tab - use provided tabId or query for active tab
        let tab;
        if (request.tabId) {
            tab = await chrome.tabs.get(request.tabId);
        } else {
            const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
            tab = tabs[0];
        }
        
        if (!tab) {
            throw new Error('No active tab found');
        }
        
        // Check if URL is accessible (not chrome:// etc.)
        if (tab.url && (tab.url.startsWith('chrome://') || tab.url.startsWith('chrome-extension:'))) {
            throw new Error('Cannot capture screenshot of browser internal pages');
        }
        
        // Get the window that contains this tab for captureVisibleTab
        const window = await chrome.windows.get(tab.windowId);
        if (!window) {
            throw new Error('Unable to access window');
        }
        
        // Capture screenshot of the visible tab
        // Note: activeTab permission should work when extension is invoked by user action
        // However, if called from sidepanel, it may require <all_urls> in host_permissions
        // See comment below for alternative if this fails
        const dataUrl = await chrome.tabs.captureVisibleTab(window.id, { format: 'png' });
        
        return {
            dataUrl: dataUrl
        };
    } catch (error) {
        // Check if it's a permission error
        if (error.message && (error.message.includes('permission') || error.message.includes('<all_urls>') || error.message.includes('activeTab'))) {
            throw new Error('Screenshot permission denied. The extension needs permission to capture screenshots. You may need to add host permissions to the manifest.');
        }
        throw error;
    }
}

// Open side panel when extension icon is clicked (only if popup doesn't handle it)
chrome.action.onClicked.addListener((tab) => {
    chrome.sidePanel.open({ tabId: tab.id });
});

// ============================================================================
// PAGE SYNC FUNCTIONALITY
// ============================================================================
// This feature monitors tab switches and URL changes, then sends page HTML 
// to OpenAI API. User consent is required before any data is sent.
// PRIVACY: This feature sends page HTML, URL, title, and timestamp to OpenAI.
// ============================================================================

// Configuration
const DEBOUNCE_DELAY_MS = 5000; // Minimum 5 seconds between sends per tab
const HTML_SIZE_LIMIT = 200000; // Limit HTML to first 200k characters (change here if needed)
const MAX_RETRIES = 5; // Maximum retry attempts for network failures
const INITIAL_BACKOFF_MS = 1000; // Initial backoff delay (1 second)

// Allowlist of domains to monitor (add/remove domains here)
// Only pages from these domains will be sent to OpenAI
const ALLOWLIST = [
    // 'example.com',
    // 'anotherdomain.com',
    // Add your allowed domains here
];

// Track debounce timers per tab
const debounceTimers = {};

// Track last URL per tab to detect URL changes
const lastUrls = {};

/**
 * Check if user has opted in to page sync feature
 * @returns {Promise<boolean>} True if user has consented, false otherwise
 */
async function getUserConsent() {
    try {
        const result = await chrome.storage.sync.get(['pageSyncEnabled']);
        return result.pageSyncEnabled === true;
    } catch (error) {
        console.error('Error checking user consent:', error);
        return false;
    }
}

/**
 * Check if URL is allowed (not chrome:// and in allowlist if configured)
 * @param {string} url - The URL to check
 * @returns {boolean} True if URL is allowed
 */
function isUrlAllowed(url) {
    try {
        const urlObj = new URL(url);
        
        // Never allow chrome:// URLs
        if (urlObj.protocol === 'chrome:' || urlObj.protocol === 'chrome-extension:') {
            return false;
        }
        
        // If allowlist is empty, allow all HTTP/HTTPS URLs
        if (ALLOWLIST.length === 0) {
            return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
        }
        
        // Check if domain is in allowlist
        return ALLOWLIST.includes(urlObj.hostname);
    } catch (error) {
        // Invalid URL
        return false;
    }
}

/**
 * Extract HTML content from page using programmatic injection
 * @param {number} tabId - The tab ID to extract HTML from
 * @returns {Promise<string|null>} The HTML content (truncated if needed), or null if access denied
 */
async function extractPageHtml(tabId) {
    try {
        // Use executeScript with <all_urls> host_permissions
        // With <all_urls>, we can access content from any webpage automatically
        // This allows the extension to work when switching tabs
        const results = await chrome.scripting.executeScript({
            target: { tabId: tabId },
            func: () => document.body.innerText
        });
        
        if (!results || !results[0] || !results[0].result) {
            return null;
        }
        
        let html = results[0].result;
        
        // Sanitize: limit HTML size to protect privacy and reduce bandwidth
        if (html.length > HTML_SIZE_LIMIT) {
            html = html.substring(0, HTML_SIZE_LIMIT);
        }
        
        return html;
    } catch (error) {
        // Handle permission errors gracefully
        // With <all_urls> permission, most pages should be accessible
        // Some restricted pages (chrome://, extensions://) will still fail
        if (error.message && error.message.includes('Cannot access contents of url')) {
            // Permission denied - may occur for restricted browser pages
            const url = error.message.match(/url "([^"]+)"/)?.[1] || 'unknown';
            console.log(`Cannot access page content (restricted page): ${url}`);
            return null;
        }
        
        console.error('Error extracting page HTML:', error);
        return null;
    }
}

/**
 * Send page data to OpenAI API with exponential backoff retry logic
 * This function sends the FULL WEBPAGE HTML to OpenAI for analysis.
 * @param {Object} pageData - The page data to send (includes full HTML content)
 * @param {number} retryCount - Current retry attempt (starts at 0)
 */
async function sendToOpenAI(pageData, retryCount = 0) {
    const apiKey = CONFIG.OPENAI_API_KEY;
    
    if (!apiKey || apiKey === 'YOUR_API_KEY_HERE' || !apiKey.startsWith('sk-')) {
        console.error('Invalid API key for page sync');
        return;
    }
    
    try {
        // Sends the complete webpage HTML content to OpenAI
        // The HTML is truncated to HTML_SIZE_LIMIT (200k chars) if needed to fit API limits
        // For the explanation request, we send up to 100k chars to OpenAI
        // This includes ALL page content: HTML structure, text, metadata, etc.
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: 'gpt-4o-mini',
                messages: [
                    {
                        role: 'system',
                        content: 'You are a user companion and your task is to assist the user when they are viewing a webpage and help them summarize the content of the webpage. The details should be concise and to the point.'
                    },
                    {
                        role: 'user',
                        content: `Please provide a detailed summary of the content of the following webpage:\n\nURL: ${pageData.url}\nTitle: ${pageData.title}\n\nPage HTML content:\n${pageData.html.substring(0, 100000)}${pageData.html.length > 100000 ? '\n[... content truncated for API limits ...]' : ''}`
                    }
                ],
                max_tokens: 2000,
                temperature: 0.7
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        const explanation = data.choices[0]?.message?.content?.trim() || 'Unable to generate explanation';
        
        // Success - update last sent log
        const timestamp = new Date().toLocaleString();
        await chrome.storage.sync.set({ 
            lastSentUrl: pageData.url,
            lastSentTime: timestamp 
        });
        
        // Notify popup if open
        try {
            chrome.runtime.sendMessage({ 
                type: 'updateLastSent', 
                url: pageData.url,
                timestamp: timestamp 
            }).catch(() => {
                // Popup might not be open, ignore error
            });
        } catch (e) {
            // Ignore message errors
        }
        
        // Send detailed explanation to sidepanel chatbot interface
        try {
            chrome.runtime.sendMessage({
                type: 'pageExplanation',
                url: pageData.url,
                title: pageData.title,
                explanation: explanation,
                timestamp: timestamp
            }).catch(() => {
                // Sidepanel might not be open, ignore error
            });
        } catch (e) {
            // Ignore message errors
        }
        
    } catch (error) {
        console.error(`Error sending to OpenAI (attempt ${retryCount + 1}):`, error);
        
        // Exponential backoff retry logic
        if (retryCount < MAX_RETRIES) {
            const backoffDelay = INITIAL_BACKOFF_MS * Math.pow(2, retryCount);
            console.log(`Retrying in ${backoffDelay}ms...`);
            setTimeout(() => {
                sendToOpenAI(pageData, retryCount + 1);
            }, backoffDelay);
        } else {
            console.error('Max retries reached. Failed to send page data to OpenAI.');
        }
    }
}

/**
 * Handle tab change (activation or URL update)
 * @param {number} tabId - The tab ID
 * @param {Object} changeInfo - Change information (from onUpdated)
 * @param {Object} tab - Tab object
 */
async function handleTabChange(tabId, changeInfo, tab) {
    // For onUpdated events: only process when page is fully loaded
    // For onActivated events: changeInfo is null, so we skip this check
    if (changeInfo && changeInfo.status !== 'complete') {
        return;
    }
    
    if (!tab || !tab.url) {
        return;
    }
    
    // Check if URL is allowed
    if (!isUrlAllowed(tab.url)) {
        return;
    }
    
    // For onUpdated events: only process if URL actually changed
    // For onActivated events: changeInfo is null, so we always process
    // (user switching tabs should trigger sync even if URL is the same)
    if (changeInfo !== null && lastUrls[tabId] === tab.url) {
        // This is an onUpdated event and URL hasn't changed, skip
        // (prevents duplicate sends on page reloads without URL change)
        return;
    }
    
    // Update last URL for this tab
    lastUrls[tabId] = tab.url;
    
    // Check user consent before proceeding
    const hasConsent = await getUserConsent();
    if (!hasConsent) {
        return;
    }
    
    // Clear existing debounce timer for this tab
    if (debounceTimers[tabId]) {
        clearTimeout(debounceTimers[tabId]);
        delete debounceTimers[tabId];
    }
    
    // Set new debounce timer
    debounceTimers[tabId] = setTimeout(async () => {
        delete debounceTimers[tabId];
        
        try {
            // Extract HTML from the page (this is the webpage content)
            const html = await extractPageHtml(tabId);
            
            // Skip if HTML extraction failed (permission denied or other error)
            if (html === null) {
                console.log(`Skipping page sync for tab ${tabId}: unable to access page content`);
                return;
            }
            
            // Prepare page data with minimal metadata
            // NOTE: The full webpage HTML is included here and sent to OpenAI
            const pageData = {
                url: tab.url,
                title: tab.title || 'Untitled',
                timestamp: new Date().toISOString(),
                html: html  // Full webpage HTML content (truncated to HTML_SIZE_LIMIT if needed)
            };
            
            // Send webpage HTML to OpenAI for detailed explanation
            // This includes the entire page content sent to OpenAI's API
            await sendToOpenAI(pageData);
            
        } catch (error) {
            console.error('Error processing tab change:', error);
        }
    }, DEBOUNCE_DELAY_MS);
}

// Listen for tab activation (when user switches to a different tab)
// Pass null for changeInfo to indicate this is an activation, not an update
chrome.tabs.onActivated.addListener(async (activeInfo) => {
    try {
        const tab = await chrome.tabs.get(activeInfo.tabId);
        // Pass null changeInfo to indicate tab activation (user switched tabs)
        await handleTabChange(activeInfo.tabId, null, tab);
    } catch (error) {
        console.error('Error handling tab activation:', error);
    }
});

// Listen for tab updates (URL changes, page loads)
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
    await handleTabChange(tabId, changeInfo, tab);
});

