/**
 * InsurancePromptListener Component
 * 
 * Listens for insurance prompts from the Decision Agent via chrome.runtime messages.
 * When the Decision Agent determines that insurance should be prompted (based on page analysis),
 * it sends a message through the background script, which this component receives and forwards
 * to the parent App component.
 */

import { useEffect } from 'react';

interface InsurancePromptListenerProps {
  onMessageReceived: (message: {
    id: string;
    text: string;
    sender: 'assistant';
    timestamp: Date;
  }) => void;
}

export function InsurancePromptListener({ onMessageReceived }: InsurancePromptListenerProps) {
  useEffect(() => {
    // Listen for messages from background script
    // The background script sends 'chatResponse' type messages when Decision Agent
    // determines insurance should be prompted
    const messageListener = (
      message: any,
      sender: chrome.runtime.MessageSender,
      sendResponse: (response?: any) => void
    ) => {
      // Only handle 'chatResponse' type messages (from Decision Agent)
      if (message && message.type === 'chatResponse') {
        console.log('📨 Insurance prompt received in React app:', message);
        
        // Format the message to match the expected interface
        const formattedMessage = {
          id: Date.now().toString(),
          text: message.message || 'Insurance prompt received',
          sender: 'assistant' as const,
          timestamp: new Date(message.metadata?.timestamp || Date.now()),
        };
        
        // Call the callback to notify parent component
        onMessageReceived(formattedMessage);
      }
      
      // Return true to indicate we may send a response asynchronously
      return true;
    };

    // Register the message listener
    if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.onMessage) {
      chrome.runtime.onMessage.addListener(messageListener);
      
      // Cleanup: remove listener when component unmounts
      return () => {
        if (chrome.runtime && chrome.runtime.onMessage) {
          chrome.runtime.onMessage.removeListener(messageListener);
        }
      };
    }
  }, [onMessageReceived]);

  // This component doesn't render anything - it's just a listener
  return null;
}
