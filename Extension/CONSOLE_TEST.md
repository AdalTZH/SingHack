# Console Test Instructions

## Quick Test

1. **Open the sidepanel** (click extension icon)
2. **Open DevTools** (right-click in sidepanel → Inspect)
3. **Go to Console tab**
4. **Run this command:**

```javascript
// Copy and paste this entire block:

(function() {
  if (!window.addChatMessageListener) {
    console.error('❌ Infrastructure not loaded!');
    return;
  }
  
  window.addChatMessageListener((msg) => {
    console.log('✅ TEST SUCCESS! Message received:', msg.text.substring(0, 100));
    alert('Insurance Prompt Received!\n\n' + msg.text.substring(0, 200));
  });
  
  console.log('✅ Listener registered! Now navigate to a travel page...');
  console.log('📝 When insurance prompt arrives, you should see the alert');
})();
```

5. **Navigate to a travel-related page** (flight booking, hotel, etc.)
6. **Watch for the alert** when the insurance prompt arrives

## What This Proves

- ✅ If you see the alert: Infrastructure works! You just need to add this code to React source.
- ❌ If no alert: Check console logs to see where it fails.

## Next Steps After Test

If the test works, add this to your React source code:

```typescript
useEffect(() => {
  if (window.addChatMessageListener) {
    window.addChatMessageListener((msg) => {
      setMessages(prev => [...prev, {
        id: msg.id,
        text: msg.text,
        sender: 'assistant',
        timestamp: msg.timestamp
      }]);
      setCurrentStage('chat');
      setIsChatActive(true);
    });
  }
}, []);
```


