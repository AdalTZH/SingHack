# Quick Fix: Register React App Listener

## The Issue

The logs show: `⚠️ No listeners registered, queued message`

This means the message is received correctly, but the React app hasn't registered a listener yet.

## Solution

Add this code to your React app (in the component that handles chat messages):

```typescript
useEffect(() => {
  // Register listener for insurance prompts
  if (typeof window !== 'undefined' && window.addChatMessageListener) {
    const handleInsurancePrompt = (messageObject: any) => {
      console.log('📨 Insurance prompt received:', messageObject);

      // Add message to chat (same as normal chat messages)
      setMessages(prev => [...prev, {
        id: messageObject.id,
        text: messageObject.text,
        sender: 'assistant',
        timestamp: messageObject.timestamp
      }]);

      // Switch to chat view
      setCurrentStage('chat');
      setIsChatActive(true);

      // Speak if in speech mode
      if (isSpeechMode && isTTSSupported) {
        speak(messageObject.text);
      }
    };

    // Register the listener
    window.addChatMessageListener(handleInsurancePrompt);
    console.log('✅ Registered insurance prompt listener');

    // Cleanup
    return () => {
      // Listener cleanup happens automatically
    };
  }
}, [setMessages, setCurrentStage, setIsChatActive, isSpeechMode, isTTSSupported, speak]);
```

## Alternative: Expose Handler for Auto-Registration

If you want the auto-injection to work, expose a handler function:

```typescript
// In your React app component
useEffect(() => {
  // Expose handler for auto-registration
  if (typeof window !== 'undefined') {
    window.handleChatMessage = (messageObject: any) => {
      setMessages(prev => [...prev, {
        id: messageObject.id,
        text: messageObject.text,
        sender: 'assistant',
        timestamp: messageObject.timestamp
      }]);
      setCurrentStage('chat');
      setIsChatActive(true);
    };
  }

  // Also register via the standard method
  if (window.addChatMessageListener) {
    window.addChatMessageListener(window.handleChatMessage);
  }
}, []);
```

## Testing

After adding the code:
1. Rebuild your React app
2. Reload the extension
3. Navigate to a travel page
4. Check console for: "✅ Registered chat message listener"
5. Message should appear in chat automatically


