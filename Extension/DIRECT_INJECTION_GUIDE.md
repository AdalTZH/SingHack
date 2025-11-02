# Direct Message Injection Guide

## Problem
The message is received and queued, but the React app doesn't display it because it hasn't registered a listener.

## Solutions Implemented

### Solution 1: Queue + Listener Registration (Current)
Messages are queued and will be delivered when React app calls `window.addChatMessageListener()`.

### Solution 2: Direct DOM Injection (Fallback)
The `inject-chat-message.js` script tries to inject messages directly by:
- Finding React state via React Fiber
- Using setState if available
- Looking for global handlers
- Creating synthetic events

## Recommended Solution

**The best approach is to add the listener to your React source code:**

```typescript
// In your React chat component
useEffect(() => {
  if (typeof window !== 'undefined' && window.addChatMessageListener) {
    const handler = (msg: any) => {
      setMessages(prev => [...prev, {
        id: msg.id,
        text: msg.text,
        sender: 'assistant',
        timestamp: msg.timestamp
      }]);
      setCurrentStage('chat');
      setIsChatActive(true);
    };
    
    window.addChatMessageListener(handler);
    console.log('✅ Insurance prompt listener registered');
    
    return () => {
      // Optional cleanup
    };
  }
}, [setMessages, setCurrentStage, setIsChatActive]);
```

## Testing Current Setup

1. Open sidepanel DevTools console
2. Navigate to a travel page
3. You should see:
   - `✅ Processing chatResponse from chrome.runtime`
   - `⚠️ No listeners registered, queued message`
4. Manually test by calling:
   ```javascript
   window.addChatMessageListener((msg) => {
     console.log('Test message received:', msg);
     // Your React code would call setMessages here
   });
   ```
5. If message appears after registering, the infrastructure works - you just need to add it to React source.

## Quick Test Script

Run this in sidepanel console to simulate what React app should do:

```javascript
// Simulate React app registration
window.addChatMessageListener((messageObject) => {
  console.log('📨 Insurance prompt received:', messageObject);
  alert('Insurance prompt: ' + messageObject.text.substring(0, 100));
  
  // This is what your React app should do:
  // setMessages(prev => [...prev, messageObject]);
  // setCurrentStage('chat');
  // setIsChatActive(true);
});

// Process any queued messages
if (window.chatMessageQueue && window.chatMessageQueue.length > 0) {
  console.log('📬 Processing queued messages:', window.chatMessageQueue.length);
  window.chatMessageQueue.forEach(msg => {
    console.log('Queued message:', msg);
  });
}
```

