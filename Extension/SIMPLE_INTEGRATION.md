# Simple Integration Guide

## React IS Compatible with Chrome Extensions! ✅

Yes, React works perfectly. Your extension already uses React (you have bundled files in `assets/`).

## Quick Integration (3 Steps)

### Step 1: Create the Listener Component

I've created `Extension/src/InsurancePromptListener.tsx` for you. This component handles all the insurance prompt logic.

### Step 2: Add to Your React App

In your main App component (wherever you handle chat messages), add:

```typescript
import { InsurancePromptListener } from './InsurancePromptListener';

// In your component:
function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  
  const handleInsurancePrompt = (message) => {
    setMessages(prev => [...prev, message]);
    setCurrentStage('chat');
    setIsChatActive(true);
  };

  return (
    <>
      <InsurancePromptListener onMessageReceived={handleInsurancePrompt} />
      {/* Your existing UI */}
    </>
  );
}
```

### Step 3: Rebuild

```bash
npm run build
# or
yarn build
```

Copy the built files to `Extension/assets/`.

## If You Don't Have React Source Files

If your React app is built elsewhere or you don't have source files:

### Option A: Find Your Source
- Look for a `src/` folder
- Check if you have a separate React project
- Check your build configuration (webpack, vite, etc.)

### Option B: Create New React App
1. Create `Extension/src/` folder
2. Set up a simple React + Vite project
3. Add the InsurancePromptListener component
4. Build to `Extension/assets/`

### Option C: Test Without Rebuilding

For now, test the infrastructure by running this in sidepanel console:

```javascript
window.addChatMessageListener((msg) => {
  alert('Insurance Prompt: ' + msg.text.substring(0, 100));
  console.log('Full message:', msg);
});
```

Then navigate to a travel page - if you see the alert, everything works!

## What You Need

1. **Find your React source files** (or create new ones)
2. **Add the InsurancePromptListener component**
3. **Rebuild your React app**
4. **Copy to Extension/assets/**

The infrastructure is ready - you just need to connect it to your React app!









