# Adding Insurance Prompt Listener to React App

## React IS Compatible with Chrome Extensions! ✅

Yes, React works perfectly with Chrome extensions. Your extension already uses React (the bundled files in `assets/`).

## Where to Add the Code

You need to find your React source files. They're likely:
1. In a separate `src/` or `app/` directory
2. In a different project/repo that builds to `Extension/assets/`
3. Already in the Extension folder but not in the root

## Step-by-Step Integration

### 1. Find Your React Source File

Look for files like:
- `App.tsx` or `App.jsx`
- `Chat.tsx` or `Chat.jsx`
- `MessageList.tsx` or similar
- Any file that has `setMessages` or manages chat messages

### 2. Add the Listener Code

Add this `useEffect` hook to the component that handles chat messages:

```typescript
import { useEffect } from 'react';

// Inside your chat component (App.tsx, Chat.tsx, etc.)
useEffect(() => {
  // Register listener for insurance prompts from decision agent
  if (typeof window !== 'undefined' && window.addChatMessageListener) {
    const handleInsurancePrompt = (messageObject: any) => {
      console.log('📨 Insurance prompt received:', messageObject);

      // Add message to chat (same format as normal chat messages)
      setMessages((prev: Message[]) => [...prev, {
        id: messageObject.id,
        text: messageObject.text,
        sender: 'assistant' as const,
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
    window.addChatMessageListener(handleInsurancePrompt);
    console.log('✅ Insurance prompt listener registered');

    // Cleanup (optional)
    return () => {
      // The listener system handles cleanup automatically
    };
  }
}, [setMessages, setCurrentStage, setIsChatActive, isSpeechMode, isTTSSupported, speak]);
```

### 3. Add TypeScript Types (if using TypeScript)

Add to your types file or at the top of your component:

```typescript
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
```

### 4. Rebuild Your React App

After adding the code:

```bash
npm run build
# or
yarn build
# or
pnpm build
```

### 5. Copy Built Files to Extension

Copy the built files to `Extension/assets/` and update `index.html` if needed.

## Alternative: If You Can't Find Source Files

If you're using a pre-built React template and can't modify it, you can:

1. **Create a wrapper component** that wraps your React app
2. **Use React DevTools** to find the component structure
3. **Build a new React app** in the Extension folder

## Testing

1. Rebuild and reload extension
2. Open sidepanel console
3. Navigate to a travel page
4. You should see: `✅ Insurance prompt listener registered`
5. Insurance prompt should appear in chat automatically!

## Quick Test (Before Rebuilding)

You can test the infrastructure right now by running this in the sidepanel console:

```javascript
window.addChatMessageListener((msg) => {
  alert('Test: ' + msg.text.substring(0, 100));
});
```

Then navigate to a travel page. If you see the alert, the infrastructure works!










