/**
 * Content Script for Decision Agent Extension
 * Extracts page content and displays streaming response from decision agent
 */

// Immediate log to verify script loads
console.log('[Decision Agent] Content script file loaded at:', new Date().toISOString());

// Configuration
const DECISION_AGENT_URL = 'http://localhost:8004/analyze';
const STREAMING_DELAY = 15; // milliseconds per character for streaming effect

// Note: Summary Agent requests go through background.js to bypass CORS
// Background.js calls http://localhost:8020/summarize

// State management
let currentRequestId = 0;
let isProcessing = false;
let textboxElement = null;
let cursorPosition = { x: 0, y: 0 };
let isInitialized = false;

/**
 * Extract page content from the current page
 * Uses innerText for cleaner, more efficient content analysis
 */
function extractPageContent() {
  try {
    const body = document.body;
    if (!body) return '';
    
    // Extract text content (innerText handles visibility and formatting)
    // innerText is better than innerHTML because:
    // 1. Smaller payload (no HTML tags)
    // 2. Cleaner for LLM analysis
    // 3. More content fits within 10k character limit
    // 4. Sufficient for decision-making (content meaning, not structure)
    const textContent = body.innerText || body.textContent || '';
    
    // Clean up the text (remove excessive whitespace)
    const cleanedText = textContent
      .replace(/\s+/g, ' ')
      .replace(/\n\s*\n/g, '\n')
      .trim();
    
    return cleanedText;
  } catch (error) {
    console.error('Error extracting page content:', error);
    return '';
  }
}

/**
 * Track cursor position
 */
function updateCursorPosition(event) {
  cursorPosition = {
    x: event.clientX,
    y: event.clientY
  };
  
  // Update textbox position if it exists
  if (textboxElement) {
    positionTextbox();
  }
}

/**
 * Position textbox beside cursor
 */
function positionTextbox() {
  if (!textboxElement) return;
  
  const offset = 20; // Distance from cursor
  const textboxWidth = 350; // Fixed width
  const textboxHeight = textboxElement.offsetHeight || 100;
  
  // Get viewport dimensions
  const viewportWidth = window.innerWidth;
  const viewportHeight = window.innerHeight;
  
  // Use cursor position, or default to center if cursor is at (0,0) or invalid
  let baseX = cursorPosition.x;
  let baseY = cursorPosition.y;
  
  if ((baseX === 0 && baseY === 0) || baseX < 0 || baseY < 0) {
    // Default to center-right of viewport if cursor position is invalid
    baseX = viewportWidth * 0.6;
    baseY = viewportHeight * 0.3;
  }
  
  // Calculate position (prefer right side, fallback to left if not enough space)
  let left = baseX + offset;
  let top = baseY + offset;
  
  // Adjust if textbox would go off-screen
  if (left + textboxWidth > viewportWidth) {
    left = baseX - textboxWidth - offset;
  }
  
  if (top + textboxHeight > viewportHeight) {
    top = baseY - textboxHeight - offset;
  }
  
  // Ensure textbox stays within viewport
  left = Math.max(10, Math.min(left, viewportWidth - textboxWidth - 10));
  top = Math.max(10, Math.min(top, viewportHeight - textboxHeight - 10));
  
  textboxElement.style.left = `${left}px`;
  textboxElement.style.top = `${top}px`;
  
}

/**
 * Create the textbox element
 */
function createTextbox() {
  // Remove existing textbox if any
  if (textboxElement) {
    textboxElement.remove();
  }
  
  // Create new textbox
  textboxElement = document.createElement('div');
  textboxElement.id = 'decision-agent-textbox';
  textboxElement.className = 'decision-agent-textbox';
  
  // Create content container
  const content = document.createElement('div');
  content.className = 'decision-agent-content';
  textboxElement.appendChild(content);
  
  // Add to page FIRST before setting styles
  document.body.appendChild(textboxElement);
  
  // Add show class for guaranteed visibility
  textboxElement.classList.add('show');
  
  // Force visibility with inline styles (using !important via setProperty)
  textboxElement.style.setProperty('display', 'block', 'important');
  textboxElement.style.setProperty('opacity', '1', 'important');
  textboxElement.style.setProperty('visibility', 'visible', 'important');
  textboxElement.style.setProperty('position', 'fixed', 'important');
  textboxElement.style.setProperty('z-index', '999999', 'important');
  
  // Position it
  positionTextbox();
  
  // Force a reflow to ensure styles are applied
  textboxElement.offsetHeight;
  
  // Verify visibility after a brief delay to ensure animation doesn't interfere
  setTimeout(() => {
    if (textboxElement) {
      // Force visibility again after animation might have started
      textboxElement.style.setProperty('opacity', '1', 'important');
      textboxElement.style.setProperty('display', 'block', 'important');
      textboxElement.style.setProperty('visibility', 'visible', 'important');
      
      const computedStyle = window.getComputedStyle(textboxElement);
      console.log('Textbox visibility after timeout:', {
        display: computedStyle.display,
        opacity: computedStyle.opacity,
        visibility: computedStyle.visibility,
        position: computedStyle.position,
        zIndex: computedStyle.zIndex,
        hasOffsetParent: textboxElement.offsetParent !== null,
        inViewport: textboxElement.getBoundingClientRect().width > 0
      });
    }
  }, 100);
  
  // Verify visibility immediately
  const computedStyle = window.getComputedStyle(textboxElement);
  const boundingRect = textboxElement.getBoundingClientRect();
  
  const debugInfo = {
    left: textboxElement.style.left,
    top: textboxElement.style.top,
    visible: textboxElement.offsetParent !== null,
    display: computedStyle.display,
    opacity: computedStyle.opacity,
    visibility: computedStyle.visibility,
    position: computedStyle.position,
    zIndex: computedStyle.zIndex,
    width: computedStyle.width,
    height: computedStyle.height,
    inDOM: document.body.contains(textboxElement),
    boundingRect: {
      x: boundingRect.x,
      y: boundingRect.y,
      width: boundingRect.width,
      height: boundingRect.height,
      top: boundingRect.top,
      left: boundingRect.left,
      bottom: boundingRect.bottom,
      right: boundingRect.right
    },
    backgroundColor: computedStyle.backgroundColor,
    color: computedStyle.color
  };
  
  console.log('Textbox created and positioned:', debugInfo);
  
  // If bounding rect has zero dimensions, force a minimum size
  if (boundingRect.width === 0 || boundingRect.height === 0) {
    console.warn('Textbox has zero dimensions! Forcing minimum size.');
    textboxElement.style.setProperty('min-width', '320px', 'important');
    textboxElement.style.setProperty('min-height', '50px', 'important');
  }
  
  // If not in viewport, log a warning
  if (boundingRect.top < 0 || boundingRect.left < 0 || 
      boundingRect.bottom > window.innerHeight || 
      boundingRect.right > window.innerWidth) {
    console.warn('Textbox appears to be outside viewport!', boundingRect);
  }
  
  return textboxElement;
}

/**
 * Display text with streaming effect
 */
function streamText(text, element) {
  return new Promise((resolve) => {
    let currentIndex = 0;
    element.textContent = '';
    
    const streamInterval = setInterval(() => {
      if (currentIndex < text.length) {
        element.textContent = text.substring(0, currentIndex + 1);
        currentIndex++;
        
        // Auto-scroll if needed
        element.scrollTop = element.scrollHeight;
      } else {
        clearInterval(streamInterval);
        resolve();
      }
    }, STREAMING_DELAY);
  });
}

/**
 * Remove text with streaming effect (reverse streaming)
 */
function streamTextOut(element) {
  return new Promise((resolve) => {
    const originalText = element.textContent;
    let currentIndex = originalText.length;
    
    if (currentIndex === 0) {
      resolve();
      return;
    }
    
    const streamInterval = setInterval(() => {
      if (currentIndex > 0) {
        element.textContent = originalText.substring(0, currentIndex - 1);
        currentIndex--;
      } else {
        clearInterval(streamInterval);
        element.textContent = '';
        resolve();
      }
    }, STREAMING_DELAY);
  });
}

/**
 * Send page content to decision agent API
 */
async function analyzePage() {
  // Prevent multiple simultaneous requests
  if (isProcessing) {
    return;
  }
  
  isProcessing = true;
  const requestId = ++currentRequestId;
  
  try {
    // Extract page content (using innerText for cleaner analysis)
    const pageContent = extractPageContent();
    const pageTitle = document.title || '';
    const pageUrl = window.location.href;
    
    if (!pageContent || pageContent.length < 50) {
      console.log('Page content too short, skipping analysis');
      isProcessing = false;
      return;
    }
    
    console.log('Sending page content to decision agent:', {
      url: pageUrl,
      title: pageTitle,
      contentLength: pageContent.length,
      contentCharactersSent: Math.min(pageContent.length, 10000)
    });
    
    console.log(`📊 Character count sent to Decision Agent: ${Math.min(pageContent.length, 10000)} characters (original: ${pageContent.length})`);
    
    // Send request via background script to bypass CORS
    const messageResponse = await new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(
        {
          action: 'analyzePage',
          url: pageUrl,
          title: pageTitle,
          inner_text: pageContent,
          timestamp: new Date().toISOString()
        },
        (response) => {
          if (chrome.runtime.lastError) {
            reject(new Error(chrome.runtime.lastError.message));
          } else if (response && response.success) {
            resolve(response.data);
          } else {
            // Handle error properly - response.error might be an object
            const errorMsg = typeof response?.error === 'string' 
              ? response.error 
              : JSON.stringify(response?.error || 'Unknown error');
            console.error('Background script error:', response);
            reject(new Error(errorMsg));
          }
        }
      );
    });
    
    // Check if this request is still current
    if (requestId !== currentRequestId) {
      console.log('Request superseded, ignoring response');
      isProcessing = false;
      return;
    }
    
    const data = messageResponse;
    
    // Check if this request is still current
    if (requestId !== currentRequestId) {
      console.log('Request superseded, ignoring response');
      isProcessing = false;
      return;
    }
    
    console.log('Decision agent response:', JSON.stringify(data, null, 2));
    
    // If should_prompt is true, call Summary Agent
    if (data && data.should_prompt && data.inner_text) {
      console.log('📝 Calling Summary Agent for page summary...');
      try {
        // Call Summary Agent to generate summary
        const summaryResponse = await callSummaryAgent(
          data.inner_text,
          pageUrl,
          pageTitle,
          data.travel_context || ''
        );
        
        if (summaryResponse && summaryResponse.success) {
          console.log('✅ Summary generated successfully');
          
          // Store summary in localStorage for Master Agent
          storePageSummary(summaryResponse);
        } else {
          console.error('❌ Failed to generate summary:', summaryResponse);
        }
      } catch (error) {
        console.error('❌ Error calling Summary Agent:', error);
      }
    }
    
    // Display response with streaming effect
    // Show textbox if we have a persuasion message
    if (data) {
      const messageToShow = data.persuasion_message;
      const hasValidMessage = messageToShow && typeof messageToShow === 'string' && messageToShow.trim().length > 0;
      
      console.log('Response check:', {
        success: data.success,
        should_prompt: data.should_prompt,
        has_message: !!messageToShow,
        message_type: typeof messageToShow,
        message_length: messageToShow ? messageToShow.length : 0,
        message_preview: messageToShow ? messageToShow.substring(0, 50) : 'none',
        hasValidMessage: hasValidMessage
      });
      
      if (hasValidMessage) {
        // Create textbox only when we have a response to show
        console.log('Creating textbox with message:', messageToShow);
        const textbox = createTextbox();
        const contentElement = textbox.querySelector('.decision-agent-content');
        
        if (!contentElement) {
          console.error('Content element not found in textbox!');
          return;
        }
        
        // Ensure textbox is visible (force it)
        if (textboxElement) {
          textboxElement.style.setProperty('display', 'block', 'important');
          textboxElement.style.setProperty('opacity', '1', 'important');
          textboxElement.style.setProperty('visibility', 'visible', 'important');
          
          // Add a temporary placeholder to ensure it has content and is visible
          if (!contentElement.textContent.trim()) {
            contentElement.textContent = messageToShow.trim().substring(0, 1);
          }
          
          // Force reflow
          textboxElement.offsetHeight;
          
          // Ensure textbox is properly visible
          textboxElement.offsetHeight; // Force reflow
        }
        
        // Stream the persuasion message
        await streamText(messageToShow.trim(), contentElement);
        console.log('Message streamed successfully');
        
        // Auto-hide after 10 seconds with streaming exit effect
        setTimeout(async () => {
          if (textboxElement && requestId === currentRequestId) {
            // Stream out the text first
            await streamTextOut(contentElement);
            
            // Then fade out and remove
            textboxElement.style.opacity = '0';
            textboxElement.style.transform = 'translateY(-10px) scale(0.95)';
            setTimeout(() => {
              if (textboxElement) {
                textboxElement.remove();
                textboxElement = null;
              }
            }, 300);
          }
        }, 10000);
      } else {
        console.log('Not showing textbox - no valid message found. Response data:', data);
      }
    } else {
      console.log('No response data received');
    }
    
  } catch (error) {
    console.error('Error analyzing page:', error);
    
    // Check if this request is still current - don't show error textbox
    if (requestId === currentRequestId) {
      console.error('Error analyzing page, not displaying textbox:', error.message);
    }
  } finally {
    isProcessing = false;
  }
}

/**
 * Analyze page immediately (for tab switches to already-loaded pages)
 */
function analyzePageImmediately() {
  console.log('[Decision Agent] analyzePageImmediately called');
  
  // Clear any pending debounced analysis
  if (window.decisionAgentTimeout) {
    clearTimeout(window.decisionAgentTimeout);
    window.decisionAgentTimeout = null;
  }
  
  // Check if page is ready
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log('[Decision Agent] Page ready, analyzing immediately');
    // Page is already loaded, analyze immediately
    setTimeout(() => {
      analyzePage();
    }, 50); // Small delay just to ensure DOM is stable
  } else {
    console.log('[Decision Agent] Page still loading, waiting for load event');
    // Page is still loading, wait for it
    const loadHandler = () => {
      console.log('[Decision Agent] Load event fired, analyzing');
      setTimeout(() => {
        analyzePage();
      }, 50);
    };
    window.addEventListener('load', loadHandler, { once: true });
    
    // Fallback: if load event doesn't fire within 2 seconds, analyze anyway
    setTimeout(() => {
      window.removeEventListener('load', loadHandler);
      if (!isProcessing) {
        console.log('[Decision Agent] Fallback timeout, analyzing anyway');
        analyzePage();
      }
    }, 2000);
  }
}

/**
 * Handle page navigation (with debounce for normal navigation)
 */
function handlePageNavigation() {
  // Debounce to avoid multiple calls
  if (window.decisionAgentTimeout) {
    clearTimeout(window.decisionAgentTimeout);
  }
  
  window.decisionAgentTimeout = setTimeout(() => {
    // Wait for page to be fully loaded, but don't wait too long
    const checkAndAnalyze = () => {
      if (document.readyState === 'complete' || document.readyState === 'interactive') {
        // Small additional delay to ensure DOM is ready
        setTimeout(() => {
          analyzePage();
        }, 100);
      } else {
        // If page is still loading, wait for load event with timeout
        const loadHandler = () => {
          setTimeout(() => {
            analyzePage();
          }, 100);
        };
        window.addEventListener('load', loadHandler, { once: true });
        
        // Fallback: if load event doesn't fire within 3 seconds, analyze anyway
        setTimeout(() => {
          window.removeEventListener('load', loadHandler);
          if (!isProcessing) {
            analyzePage();
          }
        }, 3000);
      }
    };
    
    checkAndAnalyze();
  }, 200); // Reduced debounce time from 500ms to 200ms
}

/**
 * Listen for messages from background script (e.g., tab switch)
 * Set up early to ensure it's ready when messages arrive
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('[Decision Agent] Message received:', request.action);
  
  // Handle ping to check if script is loaded
  if (request.action === 'ping') {
    sendResponse({ success: true, loaded: true });
    return true;
  }
  
  if (request.action === 'analyzePageOnTabSwitch') {
    console.log('[Decision Agent] Tab switch message received, analyzing page...', {
      readyState: document.readyState,
      url: window.location.href,
      bodyExists: !!document.body,
      isInitialized: isInitialized,
      isProcessing: isProcessing,
      timestamp: new Date().toISOString()
    });
    
    // Immediately acknowledge the message
    sendResponse({ success: true });
    
    // For tab switches, analyze immediately (no debounce)
    // This handles already-loaded pages that user switches to
    analyzePageImmediately();
    
    return true; // Indicate we will send a response asynchronously
  }
  return false; // Not handling this message
});

/**
 * Call Summary Agent to generate page summary (via background script to bypass CORS)
 */
async function callSummaryAgent(innerText, url, title, travelContext) {
  try {
    console.log('Calling Summary Agent via background script:', {
      url: url,
      title: title,
      travelContext: travelContext,
      innerTextLength: innerText.length
    });
    
    // Send request via background script to bypass CORS
    const response = await new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(
        {
          action: 'summarizePage',
          inner_text: innerText,
          url: url,
          title: title,
          travel_context: travelContext
        },
        (response) => {
          if (chrome.runtime.lastError) {
            reject(new Error(chrome.runtime.lastError.message));
          } else if (response && response.success) {
            resolve(response.data);
          } else {
            const errorMsg = typeof response?.error === 'string' 
              ? response.error 
              : JSON.stringify(response?.error || 'Unknown error');
            console.error('Background script error (summary):', response);
            reject(new Error(errorMsg));
          }
        }
      );
    });
    
    console.log('Summary Agent response:', response);
    return response;
  } catch (error) {
    console.error('Error calling Summary Agent:', error);
    return null;
  }
}

/**
 * Store page summary in chrome.storage for Master Agent
 * Note: Must use chrome.storage.local (not localStorage) to share between content script and sidepanel
 */
function storePageSummary(summaryResponse) {
  try {
    // Get existing summaries from chrome.storage
    chrome.storage.local.get(['page_summaries'], (result) => {
      let summaries = result.page_summaries || [];
      
      // Ensure summaries is an array
      if (!Array.isArray(summaries)) {
        summaries = [];
      }
      
      // Add new summary
      summaries.push({
        summary: summaryResponse.summary,
        url: summaryResponse.url,
        title: summaryResponse.title,
        travel_context: summaryResponse.travel_context,
        metadata: summaryResponse.metadata,
        timestamp: new Date().toISOString()
      });
      
      // Keep only the last 10 summaries (to avoid storage limits)
      if (summaries.length > 10) {
        summaries = summaries.slice(-10);
      }
      
      // Store back to chrome.storage
      chrome.storage.local.set({ page_summaries: summaries }, () => {
        console.log('📦 Stored page summary in chrome.storage:', {
          totalSummaries: summaries.length,
          latestTitle: summaryResponse.title
        });
      });
    });
  } catch (error) {
    console.error('Error storing page summary:', error);
  }
}

/**
 * Initialize the content script
 */
function init() {
  console.log('[Decision Agent] Content script initialized', {
    readyState: document.readyState,
    url: window.location.href,
    timestamp: new Date().toISOString()
  });
  
  isInitialized = true;
  
  // Track cursor position
  document.addEventListener('mousemove', updateCursorPosition);
  
  // Handle initial page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', handlePageNavigation);
  } else {
    // Page is already loaded, but use normal navigation handler (with debounce)
    // This prevents duplicate analysis on initial load
    handlePageNavigation();
  }
  
  // Handle navigation in SPAs (Single Page Applications)
  let lastUrl = location.href;
  new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
      lastUrl = url;
      handlePageNavigation();
    }
  }).observe(document, { subtree: true, childList: true });
  
  // Handle browser navigation (back/forward)
  window.addEventListener('popstate', handlePageNavigation);
  
  // Handle pushState/replaceState (SPA navigation)
  const originalPushState = history.pushState;
  const originalReplaceState = history.replaceState;
  
  history.pushState = function(...args) {
    originalPushState.apply(history, args);
    handlePageNavigation();
  };
  
  history.replaceState = function(...args) {
    originalReplaceState.apply(history, args);
    handlePageNavigation();
  };
}

// Initialize when script loads
try {
  console.log('[Decision Agent] About to call init()');
  init();
  console.log('[Decision Agent] init() completed successfully');
} catch (error) {
  console.error('[Decision Agent] ERROR during initialization:', error);
  console.error('[Decision Agent] Stack trace:', error.stack);
}

