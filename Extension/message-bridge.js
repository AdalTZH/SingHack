/**
 * Message Bridge Script
 * Handles chrome.runtime.onMessage and dispatches custom events
 * This is a separate file to avoid CSP (Content Security Policy) violations
 */

(function() {
  'use strict';

  if (typeof chrome !== 'undefined' && chrome.runtime) {
    console.log('📡 Sidepanel message listener initialized');

    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      console.log('📨 Sidepanel received message:', request.type);

      // Handle insurance prompt as a chatResponse (same format as normal chat)
      if (request.type === 'chatResponse' && request.message) {
        console.log('✅ Received chatResponse (insurance prompt):', {
          message_length: request.message.length,
          message_preview: request.message.substring(0, 100)
        });

        // Dispatch event that React app can listen for
        // Format it the same way as normal chat responses
        const event = new CustomEvent('chatResponse', {
          detail: {
            message: request.message, // Master agent's response text
            metadata: request.metadata || {}
          }
        });
        window.dispatchEvent(event);
        console.log('✅ Dispatched chatResponse event');

        // Return true to indicate async response, but don't call sendResponse
        // The chat-response-listener.js will handle the actual processing
        return true;
      }

      // Handle other message types - return false to indicate no async response needed
      if (request.type === 'updateLastSent') {
        return false;
      }

      // For unknown types, return false to avoid async warnings
      return false;
    });
  } else {
    console.warn('⚠️ Chrome runtime not available in sidepanel');
  }
})();

