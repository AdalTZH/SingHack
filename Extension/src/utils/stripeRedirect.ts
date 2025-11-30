/**
 * Utility function to redirect to Stripe checkout
 * Reuses logic from insurance-popup.js
 */

export async function redirectToStripe(metadata: Record<string, any> = {}): Promise<void> {
  console.log('💳 Redirecting to Stripe checkout...');
  
  // Get payment service URL from config or use default
  let PAYMENT_SERVICE_URL = 'http://localhost:8085';
  
  // Try to get from config if available
  if (typeof window !== 'undefined' && (window as any).CONFIG?.PAYMENT_SERVICE_URL) {
    PAYMENT_SERVICE_URL = (window as any).CONFIG.PAYMENT_SERVICE_URL;
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








