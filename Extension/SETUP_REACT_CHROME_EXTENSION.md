# Setting Up React in Chrome Extension

## React + Chrome Extensions: Complete Guide

Yes, **React is fully compatible with Chrome extensions!** Many popular extensions use React.

## Quick Setup

### Option 1: Using Vite (Recommended for Chrome Extensions)

1. **Install dependencies:**
```bash
cd Extension
npm init -y
npm install react react-dom
npm install -D vite @vitejs/plugin-react @types/react @types/react-dom typescript
```

2. **Create `vite.config.ts`:**
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'assets',
    rollupOptions: {
      input: 'src/main.tsx',
      output: {
        format: 'es',
        entryFileNames: 'index-[hash].js',
        assetFileNames: 'index-[hash].[ext]'
      }
    }
  },
  server: {
    port: 5173
  }
});
```

3. **Create `src/main.tsx`:**
```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

4. **Add insurance prompt listener to `src/App.tsx`:**
```typescript
import { useEffect, useState } from 'react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isChatActive, setIsChatActive] = useState(false);

  // Add insurance prompt listener
  useEffect(() => {
    if (typeof window !== 'undefined' && window.addChatMessageListener) {
      const handleInsurancePrompt = (messageObject: any) => {
        setMessages(prev => [...prev, {
          id: messageObject.id,
          text: messageObject.text,
          sender: 'assistant',
          timestamp: messageObject.timestamp
        }]);
        setIsChatActive(true);
      };

      window.addChatMessageListener(handleInsurancePrompt);
      console.log('✅ Insurance prompt listener registered');
    }
  }, []);

  // ... rest of your component
}
```

5. **Build:**
```bash
npm run build
```

### Option 2: Using Create React App

```bash
npx create-react-app extension-app
cd extension-app
npm run build
# Copy build files to Extension/assets/
```

### Option 3: Using Webpack

Similar setup, just configure webpack to output to `Extension/assets/`.

## Chrome Extension Specific Considerations

### Content Security Policy (CSP)

React works fine, but you need to:
- ✅ Use external script files (not inline scripts)
- ✅ Bundle React with your app (not from CDN)
- ✅ All scripts from `'self'` are allowed (your assets folder)

### Manifest.json

Your current manifest is good:
```json
{
  "manifest_version": 3,
  "side_panel": {
    "default_path": "index.html"
  }
}
```

### Script Loading Order

In `index.html`, load scripts in this order:
1. Bridge scripts (message-bridge.js)
2. Helper scripts (chat-response-listener.js)
3. React app bundle

## Testing Your Setup

1. Build your React app
2. Copy to Extension/assets/
3. Update index.html to reference new bundle
4. Load extension in Chrome
5. Test insurance prompts!

## Need Help Finding Your Source?

If you can't find your React source files, they might be:
- In a separate repository
- In a parent directory
- Built by CI/CD and not in the repo

Let me know and I can help locate them or set up a new React project!









