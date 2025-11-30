/**
 * Example: How to use InsurancePromptListener in your React App
 * 
 * This shows how to integrate the insurance prompt listener into your existing chat component
 */

import { useState, useEffect } from 'react';
import { InsurancePromptListener } from './InsurancePromptListener';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

export function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isChatActive, setIsChatActive] = useState(false);
  const [currentStage, setCurrentStage] = useState<'start' | 'landing' | 'decision' | 'payment' | 'chat'>('start');

  // Handler for insurance prompts
  const handleInsurancePrompt = (message: {
    id: string;
    text: string;
    sender: 'assistant';
    timestamp: Date;
  }) => {
    // Add message to chat
    setMessages(prev => [...prev, message]);
    
    // Switch to chat view
    setCurrentStage('chat');
    setIsChatActive(true);
    
    console.log('✅ Insurance prompt added to chat');
  };

  return (
    <div className="app">
      {/* Add this component anywhere in your app - it doesn't render anything */}
      <InsurancePromptListener onMessageReceived={handleInsurancePrompt} />
      
      {/* Your existing chat UI */}
      <div className="chat-container">
        {messages.map(msg => (
          <div key={msg.id} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
      </div>
    </div>
  );
}








