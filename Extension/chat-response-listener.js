/**
 * Chat Response Listener for Insurance Prompts
 * Implements Option 1: Chrome Runtime Message Listener
 * This script listens for chatResponse messages and provides a global interface
 * that the React app can use to receive insurance prompts
 */

(function() {
  'use strict';

  console.log('🔧 Chat Response Listener (Option 1) initializing...');

  // Global message queue that React app can access
  if (!window.chatMessageQueue) {
    window.chatMessageQueue = [];
    window.chatMessageListeners = [];
  }

  /**
   * Add a listener function that will be called when chat responses arrive
   * React app should call this to register its message handler
   */
  window.addChatMessageListener = function(listener) {
    if (typeof listener === 'function') {
      window.chatMessageListeners.push(listener);
      console.log('✅ Registered chat message listener');
      
      // Process any queued messages
      window.chatMessageQueue.forEach(msg => {
        try {
          listener(msg);
        } catch (e) {
          console.error('Error in chat message listener:', e);
        }
      });
      
      // Clear queue after processing
      window.chatMessageQueue = [];
    }
  };

  /**
   * Process and distribute a chat message
   */
  function processChatMessage(message, metadata = {}) {
    const messageObject = {
      id: Date.now().toString(),
      text: message,
      sender: 'assistant',
      timestamp: new Date(),
      metadata: metadata
    };

    console.log('📨 Processing chat message:', {
      message_length: message.length,
      message_preview: message.substring(0, 100),
      listeners_count: window.chatMessageListeners.length
    });

    // Call all registered listeners
    if (window.chatMessageListeners.length > 0) {
      window.chatMessageListeners.forEach(listener => {
        try {
          listener(messageObject);
          console.log('✅ Message delivered to listener');
        } catch (e) {
          console.error('❌ Error calling listener:', e);
        }
      });
    } else {
      // Queue the message if no listeners registered yet
      window.chatMessageQueue.push(messageObject);
      console.log('⚠️ No listeners registered, queued message');
      
      // Also try to trigger direct injection via postMessage
      // This gives the inject-chat-message.js script a chance to inject it
      if (window.postMessage) {
        window.postMessage({
          type: 'injectChatMessage',
          message: message
        }, '*');
        console.log('📨 Sent postMessage for direct injection');
      }
    }
  }

  // Auto-injection: Try to find React app's message handler and register automatically
  function tryAutoRegister() {
    // Wait for React app to potentially expose a handler
    let attempts = 0;
    const maxAttempts = 30; // Try for 6 seconds (30 * 200ms)

    const checkInterval = setInterval(() => {
      attempts++;

      // Check if React app has exposed a message handler function
      if (window.handleChatMessage || window.addMessageToChat) {
        console.log('✅ Found React app message handler, registering automatically');
        const handler = window.handleChatMessage || window.addMessageToChat;
        window.addChatMessageListener(handler);
        clearInterval(checkInterval);
        return;
      }

      // Try to find React state setter by looking at window object
      // Some React apps expose their state setters globally for debugging
      if (window.__REACT_APP_MESSAGES__) {
        console.log('✅ Found React app messages array, creating handler');
        const handler = (msg) => {
          if (Array.isArray(window.__REACT_APP_MESSAGES__)) {
            window.__REACT_APP_MESSAGES__.push({
              id: msg.id,
              text: msg.text,
              sender: 'assistant',
              timestamp: msg.timestamp
            });
            console.log('✅ Message injected into React app messages');
          }
        };
        window.addChatMessageListener(handler);
        clearInterval(checkInterval);
        return;
      }

      if (attempts >= maxAttempts) {
        clearInterval(checkInterval);
        console.warn('⚠️ Could not auto-register with React app');
        console.log('📝 React app should call: window.addChatMessageListener((message) => { /* handle */ })');
      }
    }, 200);
  }

  // Setup Chrome Runtime message listener (Option 1 implementation)
  function setupChromeRuntimeListener() {
    if (typeof chrome === 'undefined' || !chrome.runtime) {
      console.warn('⚠️ Chrome runtime not available');
      return;
    }

    console.log('📡 Setting up chrome.runtime.onMessage listener (Option 1)...');

    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      // Only handle chatResponse, ignore other types silently
      if (request.type === 'chatResponse' && request.message) {
        console.log('✅ Processing chatResponse from chrome.runtime:', {
          message_length: request.message.length,
          message_preview: request.message.substring(0, 100),
          has_metadata: !!request.metadata
        });

        // Process the message
        processChatMessage(request.message, request.metadata || {});

        // Return true BEFORE any async operations to prevent warning
        sendResponse({ success: true });
        return true;
      }

      // Don't return anything for other message types (let message-bridge.js handle them)
      return;
    });

    console.log('✅ Chrome Runtime message listener setup complete');
    
    // Try to auto-register with React app
    tryAutoRegister();
  }

  // Also listen for custom events from index.html bridge (backup mechanism)
  window.addEventListener('chatResponse', (event) => {
    console.log('✅ Received chatResponse custom event from bridge');
    const { message, metadata } = event.detail;
    if (message) {
      processChatMessage(message, metadata || {});
    }
  });

  // Initialize
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupChromeRuntimeListener);
  } else {
    setupChromeRuntimeListener();
  }

  console.log('✅ Chat Response Listener (Option 1) loaded');
  console.log('📝 React app should call: window.addChatMessageListener((message) => { /* handle message */ })');
})();

