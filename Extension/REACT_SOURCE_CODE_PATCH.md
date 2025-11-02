# React Source Code Patch for Option 1

## Quick Implementation

Add this code to your React app's main chat component (usually `App.tsx` or wherever you handle chat messages):

```typescript
import { useEffect } from 'react';

// Inside your component:
useEffect(() => {
  // Register listener with the chat-response-listener.js script
  if (typeof window !== 'undefined' && window.addChatMessageListener) {
    const handleChatMessage = (messageObject: any) => {
      // messageObject has: { id, text, sender, timestamp, metadata }
      console.log('📨 Received insurance prompt:', messageObject);

      // Add to messages state (same as normal chat)
      setMessages(prev => [...prev, {
        id: messageObject.id,
        text: messageObject.text,
        sender: 'assistant',
        timestamp: messageObject.timestamp
      }]);

      // Switch to chat view if needed
      setCurrentStage('chat');
      setIsChatActive(true);

      // Speak if in speech mode
      if (isSpeechMode && isTTSSupported) {
        speak(messageObject.text);
      }
    };

    // Register the listener
    window.addChatMessageListener(handleChatMessage);
    console.log('✅ Registered insurance prompt listener');

    // Cleanup
    return () => {
      if (window.removeChatMessageListener) {
        window.removeChatMessageListener(handleChatMessage);
      }
    };
  }
}, [setMessages, setCurrentStage, setIsChatActive, isSpeechMode, isTTSSupported, speak]);
```

## Alternative: Direct Chrome Runtime Listener

If you prefer to implement it directly without the helper script:

```typescript
useEffect(() => {
  if (typeof chrome !== 'undefined' && chrome.runtime) {
    const messageListener = (request: any, sender: any, sendResponse: any) => {
      if (request.type === 'chatResponse' && request.message) {
        console.log('📨 Received chatResponse:', request.message);

        // Add message to chat
        const assistantMessage: Message = {
          id: Date.now().toString(),
          text: request.message,
          sender: 'assistant',
          timestamp: new Date(),
        };

        setMessages(prev => [...prev, assistantMessage]);
        setCurrentStage('chat');
        setIsChatActive(true);

        if (isSpeechMode && isTTSSupported) {
          speak(request.message);
        }

        return true; // Indicate async response
      }
    };

    chrome.runtime.onMessage.addListener(messageListener);

    return () => {
      chrome.runtime.onMessage.removeListener(messageListener);
    };
  }
}, [setMessages, setCurrentStage, setIsChatActive, isSpeechMode, isTTSSupported, speak]);
```

## TypeScript Types

Add to your types file:

```typescript
interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

declare global {
  interface Window {
    addChatMessageListener?: (listener: (message: ChatMessage & { metadata?: any }) => void) => void;
    chatMessageQueue?: Array<ChatMessage & { metadata?: any }>;
    chatMessageListeners?: Array<(message: ChatMessage & { metadata?: any }) => void>;
  }
}
```

## Testing

1. Add the code to your React source
2. Rebuild the app
3. Navigate to a travel-related page
4. Check console logs for "📨 Received insurance prompt"
5. Message should appear in chat automatically


