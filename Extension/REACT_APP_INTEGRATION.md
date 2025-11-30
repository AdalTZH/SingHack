# React App Integration for Insurance Prompts

## Current Setup

The insurance prompt now uses the same format as normal chat messages (`chatResponse` type). The React app needs to listen for incoming messages and display them.

## Required React Code Update

Add this to your React app (wherever chat messages are handled, likely in the main chat component):

```typescript
useEffect(() => {
  // Listen for incoming chat responses (including insurance prompts)
  if (typeof chrome !== 'undefined' && chrome.runtime) {
    const messageListener = (request: any, sender: any, sendResponse: any) => {
      if (request.type === 'chatResponse' && request.message) {
        console.log('Received chatResponse:', request.message);
        
        // Add message to chat as assistant message (same as normal chat)
        const assistantMessage: Message = {
          id: Date.now().toString(),
          text: request.message,
          sender: 'assistant',
          timestamp: new Date(),
        };
        
        setMessages(prev => [...prev, assistantMessage]);
        
        // Switch to chat view if needed
        setCurrentStage('chat');
        setIsChatActive(true);
        
        // Speak if in speech mode
        if (isSpeechMode && isTTSSupported) {
          speak(request.message);
        }
        
        // Return true to indicate async response
        return true;
      }
    };

    chrome.runtime.onMessage.addListener(messageListener);

    return () => {
      chrome.runtime.onMessage.removeListener(messageListener);
    };
  }
}, [setMessages, setCurrentStage, setIsChatActive, isSpeechMode, isTTSSupported, speak]);
```

## Alternative: Listen for Custom Event

If you prefer using the custom event approach (already dispatched by index.html):

```typescript
useEffect(() => {
  const handleChatResponse = (event: CustomEvent) => {
    const { message } = event.detail;
    
    const assistantMessage: Message = {
      id: Date.now().toString(),
      text: message,
      sender: 'assistant',
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, assistantMessage]);
    setCurrentStage('chat');
    setIsChatActive(true);
  };

  window.addEventListener('chatResponse', handleChatResponse as EventListener);
  return () => {
    window.removeEventListener('chatResponse', handleChatResponse as EventListener);
  };
}, []);
```

## Flow Summary

1. User browses travel page
2. Decision Agent analyzes → forwards to Master Agent
3. Master Agent generates response
4. Background.js sends `{type: 'chatResponse', message: ...}` to sidepanel
5. index.html bridge script dispatches `chatResponse` event
6. **React app listens for event/message and adds to chat** ← YOU NEED THIS
7. Message appears in chat interface

## Testing

After adding the listener, test by:
1. Navigate to a travel-related page (flight booking, hotel, etc.)
2. Check console logs to see if message is received
3. Message should appear in chat automatically








