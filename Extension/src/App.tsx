/**
 * Main App Component
 * 
 * IMPORTANT: If you already have an App.tsx, just add the InsurancePromptListener
 * component to your existing file instead of replacing it.
 */

import { useState, useEffect } from 'react';
import { InsurancePromptListener } from './InsurancePromptListener';
import { MessageContent } from './components/MessageContent';

// Message interface
interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

// Stage type
type Stage = 'start' | 'landing' | 'decision' | 'payment' | 'chat';

export default function App() {
  const [currentStage, setCurrentStage] = useState<Stage>('start');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isChatActive, setIsChatActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Handler for insurance prompts from Decision Agent
  const handleInsurancePrompt = (message: {
    id: string;
    text: string;
    sender: 'assistant';
    timestamp: Date;
  }) => {
    console.log('📨 Insurance prompt received:', message);

    // Add message to chat
    setMessages(prev => [...prev, message]);

    // Switch to chat view
    setCurrentStage('chat');
    setIsChatActive(true);
  };

  // Handle normal chat messages (from user)
  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: text,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send to background script
      if (typeof chrome !== 'undefined' && chrome.runtime) {
        const response = await chrome.runtime.sendMessage({
          type: 'chat',
          message: text,
          temperature: 0.7
        });

        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: response.message || 'No response received',
          sender: 'assistant',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      {/* Fixed background layer */}
      <div className="fixed-background"></div>
      
      {/* Add Insurance Prompt Listener - handles automatic insurance prompts */}
      <InsurancePromptListener onMessageReceived={handleInsurancePrompt} />

      {/* Your existing UI code goes here */}
      {currentStage === 'chat' && (
        <div className="chat-container">
          <div className="messages">
            {messages.map(msg => (
              <div key={msg.id} className={`message ${msg.sender}`}>
                <MessageContent text={msg.text} sender={msg.sender} />
              </div>
            ))}
            {isLoading && (
              <div className="message assistant loading">
                <div className="typing-indicator">...</div>
              </div>
            )}
          </div>
          <div className="chat-input">
            <input
              type="text"
              placeholder="Type your message..."
              onKeyPress={(e) => {
                if (e.key === 'Enter' && e.currentTarget.value) {
                  handleSendMessage(e.currentTarget.value);
                  e.currentTarget.value = '';
                }
              }}
            />
          </div>
        </div>
      )}

      {/* Add your other stages/components here */}
    </div>
  );
}

