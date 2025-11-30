/**
 * Insurance Prompt Listener Component
 * Add this component to your React app to receive insurance prompts from Decision Agent
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
    // Register listener for insurance prompts
    if (typeof window !== 'undefined' && window.addChatMessageListener) {
      const handleInsurancePrompt = (messageObject: any) => {
        console.log('📨 Insurance prompt received:', messageObject);
        
        // Call the parent component's handler
        onMessageReceived({
          id: messageObject.id,
          text: messageObject.text,
          sender: 'assistant',
          timestamp: messageObject.timestamp
        });
      };

      // Register the listener
      window.addChatMessageListener(handleInsurancePrompt);
      console.log('✅ Insurance prompt listener registered');

      // Cleanup
      return () => {
        // Listener cleanup is handled automatically
      };
    } else {
      console.warn('⚠️ window.addChatMessageListener not available');
    }
  }, [onMessageReceived]);

  // This component doesn't render anything
  return null;
}

// TypeScript declarations
declare global {
  interface Window {
    addChatMessageListener?: (
      listener: (message: {
        id: string;
        text: string;
        sender: 'assistant';
        timestamp: Date;
        metadata?: any;
      }) => void
    ) => void;
    chatMessageQueue?: Array<{
      id: string;
      text: string;
      sender: 'assistant';
      timestamp: Date;
    }>;
  }
}










