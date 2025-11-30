# Installing React and Setting Up Chrome Extension

## ✅ React IS Compatible with Chrome Extensions!

React works perfectly in Chrome extensions. Many popular extensions use React.

## Quick Setup (5 Minutes)

### Step 1: Install Dependencies

```bash
cd Extension
npm install
```

This will install:
- React & React DOM
- Vite (build tool)
- TypeScript
- All necessary dependencies

### Step 2: Build Your App

```bash
npm run build
```

This builds your React app to `Extension/assets/` folder.

### Step 3: Reload Extension

1. Open Chrome Extensions: `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Reload" on your extension
4. Open sidepanel and test!

## File Structure

```
Extension/
├── src/
│   ├── main.tsx              # React app entry point
│   ├── App.tsx                # Main app component
│   └── InsurancePromptListener.tsx  # Insurance prompt handler
├── assets/                    # Built files (auto-generated)
├── index.html                 # Sidepanel HTML
├── manifest.json              # Extension manifest
├── vite.config.ts             # Build configuration
└── package.json               # Dependencies
```

## How It Works

1. **InsurancePromptListener** component registers a listener
2. When Decision Agent detects travel page → Master Agent responds
3. Background script sends message to sidepanel
4. **InsurancePromptListener** receives it
5. Message appears in chat automatically!

## Development

```bash
# Development mode (with hot reload)
npm run dev

# Production build
npm run build
```

## Already Have React Source Files?

If you have React source files elsewhere:

1. **Find your existing App.tsx/App.jsx**
2. **Add this import:**
   ```typescript
   import { InsurancePromptListener } from './InsurancePromptListener';
   ```

3. **Add the component to your JSX:**
   ```tsx
   <InsurancePromptListener 
     onMessageReceived={(msg) => {
       setMessages(prev => [...prev, msg]);
       setCurrentStage('chat');
     }} 
   />
   ```

4. **Rebuild and copy to Extension/assets/**

## Testing

After setup:
1. Navigate to a travel page (flight booking, hotel, etc.)
2. Insurance prompt should appear in chat automatically!
3. Check console for: `✅ Insurance prompt listener registered`

## Need Help?

- Check `SIMPLE_INTEGRATION.md` for step-by-step guide
- Check `App.example.tsx` for integration examples
- The infrastructure is ready - just connect React!










