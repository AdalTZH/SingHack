/**
 * Insurance Prompt Popup
 * Simple popup notification that appears when insurance prompt is received
 * No React integration needed - pure JavaScript
 */

(function() {
  'use strict';

  console.log('🔔 Insurance Popup initializing...');

  // Create popup element
  function createPopup(message, metadata = {}) {
    // Remove existing popup if any
    const existing = document.getElementById('insurance-prompt-popup');
    if (existing) {
      existing.remove();
    }

    const popup = document.createElement('div');
    popup.id = 'insurance-prompt-popup';
    popup.className = 'insurance-prompt-popup';

    // Extract concise message - take first meaningful sentence or truncate to 100 chars
    let shortMessage = message;
    
    // Try to get first sentence (more natural)
    const firstSentence = message.match(/^[^.!?]+[.!?]/);
    if (firstSentence && firstSentence[0].length <= 120) {
      shortMessage = firstSentence[0];
    } else {
      // Fallback: truncate to 100 chars
      shortMessage = message.length > 100 
        ? message.substring(0, 97) + '...'
        : message;
    }

    // Escape HTML to prevent XSS
    const escapeHtml = (text) => {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    };

    popup.innerHTML = `
      <div class="insurance-prompt-popup-header">
        <h3 class="insurance-prompt-popup-title">Travel Insurance</h3>
        <button class="insurance-prompt-popup-close" aria-label="Close">×</button>
      </div>
      <p class="insurance-prompt-popup-message">${escapeHtml(shortMessage)}</p>
      <div class="insurance-prompt-popup-actions">
        <button class="insurance-prompt-popup-button primary" data-action="purchase-plan">Purchase Plan</button>
        <button class="insurance-prompt-popup-button secondary" data-action="dismiss">Later</button>
      </div>
    `;

    // Add to page
    document.body.appendChild(popup);

    // Close button handler
    const closeBtn = popup.querySelector('.insurance-prompt-popup-close');
    closeBtn.addEventListener('click', () => dismissPopup(popup));

    // Action button handlers
    popup.querySelectorAll('.insurance-prompt-popup-button').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const action = e.currentTarget.dataset.action;
        if (action === 'purchase-plan') {
          e.currentTarget.disabled = true;
          e.currentTarget.textContent = 'Loading...';
          await redirectToStripe(metadata);
          dismissPopup(popup);
        } else if (action === 'dismiss') {
          dismissPopup(popup);
        }
      });
    });

    // Auto-dismiss after 10 seconds
    setTimeout(() => {
      if (document.body.contains(popup)) {
        dismissPopup(popup);
      }
    }, 10000);

    console.log('✅ Insurance popup displayed');
  }

  function dismissPopup(popup) {
    popup.classList.add('hide');
    setTimeout(() => {
      if (document.body.contains(popup)) {
        popup.remove();
      }
    }, 300);
  }

  async function redirectToStripe(metadata = {}) {
    console.log('💳 Redirecting to Stripe checkout...');
    
    // Get payment service URL from config or use default
    let PAYMENT_SERVICE_URL = 'http://localhost:8085';
    
    // Try to get from config if available
    if (typeof CONFIG !== 'undefined' && CONFIG.PAYMENT_SERVICE_URL) {
      PAYMENT_SERVICE_URL = CONFIG.PAYMENT_SERVICE_URL;
    }
    
    try {
      // Create checkout session
      const response = await fetch(`${PAYMENT_SERVICE_URL}/create-checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          amount: 5000, // $50 in cents (SGD)
          product_name: `Travel Insurance - ${metadata.travel_context || 'Standard Plan'}`,
          currency: 'SGD'
        })
      });

      if (!response.ok) {
        throw new Error(`Payment service returned ${response.status}`);
      }

      const data = await response.json();
      const checkoutUrl = data.checkout_url;

      if (checkoutUrl) {
        console.log('✅ Checkout URL received, redirecting...');
        // Open Stripe checkout in new tab
        window.open(checkoutUrl, '_blank');
      } else {
        throw new Error('No checkout URL in response');
      }
    } catch (error) {
      console.error('❌ Error creating checkout:', error);
      
      // Fallback: show error message
      alert('Unable to open payment page. Please try again later or contact support.');
      
      // Optional: fallback to chat
      if (typeof chrome !== 'undefined' && chrome.runtime) {
        chrome.runtime.sendMessage({
          type: 'chat',
          message: 'I want to purchase travel insurance for my trip'
        }).catch(err => {
          console.log('Could not send chat message:', err);
        });
      }
    }
  }

  // Listen for insurance prompts
  function setupListener() {
    if (typeof chrome !== 'undefined' && chrome.runtime) {
      console.log('📡 Setting up chrome.runtime listener for popup...');

      chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request.type === 'chatResponse' && request.message) {
          console.log('🔔 Showing insurance popup:', request.message.substring(0, 100));
          
          // Show popup with concise message
          createPopup(request.message, request.metadata || {});
          
          // Return true for async response
          return true;
        }
        return false;
      });
    }

    // Also listen for custom events from message-bridge
    window.addEventListener('chatResponse', (event) => {
      const { message } = event.detail;
      if (message) {
        console.log('🔔 Showing insurance popup from event:', message.substring(0, 100));
        createPopup(message, event.detail.metadata || {});
      }
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupListener);
  } else {
    setupListener();
  }

  console.log('✅ Insurance Popup loaded');
})();

