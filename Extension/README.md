# SINGHACK Chrome Extension

A modern Chrome extension with AI chat assistant, page sync functionality, and SingPass authentication integration. The extension uses React with Vite for the frontend and a service worker for background tasks.

## 📋 Prerequisites

- Node.js 18+ and npm
- Chrome browser (for testing)
- OpenAI API key (for direct API mode) OR Master Agent backend running
- Decision Agent backend (optional, for page sync feature)

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure API Keys

Create or edit `config.js` in the Extension folder:

```javascript
const CONFIG = {
    // Your OpenAI API key (get from https://platform.openai.com/api-keys)
    OPENAI_API_KEY: 'sk-your-api-key-here',
    
    // Set to true to use Master Agent backend, false for direct OpenAI
    USE_MASTER_AGENT: false,
    
    // Backend URLs (adjust if your servers run on different ports)
    MASTER_AGENT_URL: 'http://localhost:9000',
    DECISION_AGENT_URL: 'http://localhost:8004'
};
```

**⚠️ Important:** The `config.js` file is excluded from git (see `.gitignore`). Do not commit your API keys!

### 3. Development Mode

Run the development server:

```bash
npm run dev
```

This will start Vite on `http://localhost:3000` for development. Note: For Chrome extension development, you'll need to build and load the extension manually.

### 4. Build for Chrome Extension

Build the extension for production:

```bash
npm run build
```

This creates a `build/` folder with all necessary files:
- Compiled React app
- `manifest.json`
- `background.js`
- `config.js`
- `popup.html` and `popup.js`
- Icons folder

### 5. Load Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `Extension/build` folder
5. The extension should now appear in your extensions list

### 6. Using the Extension

- **Extension Icon**: Click the extension icon in the toolbar to open the popup (settings)
- **Side Panel**: Click "Open Chat Assistant" in the popup, or the extension will automatically open the side panel
- **Page Sync**: Enable page sync in the popup to allow automatic page content analysis

## 📁 Project Structure

```
Extension/
├── src/                    # React source files
│   ├── components/        # React components
│   ├── App.tsx            # Main app component
│   └── main.tsx           # Entry point
├── icons/                 # Extension icons
├── background.js          # Service worker (background script)
├── config.js              # Configuration (API keys, etc.)
├── manifest.json          # Chrome extension manifest
├── popup.html             # Extension popup HTML
├── popup.js               # Extension popup JavaScript
├── index.html             # Main app HTML
├── vite.config.ts         # Vite configuration
└── package.json           # Dependencies
```

## 🔧 Configuration

### API Modes

The extension supports two modes:

1. **Direct OpenAI API** (`USE_MASTER_AGENT: false`)
   - Requires OpenAI API key in `config.js`
   - Directly calls OpenAI API
   - Supports image analysis

2. **Master Agent Mode** (`USE_MASTER_AGENT: true`)
   - Requires Master Agent backend running
   - Forwards requests to Master Agent
   - Image analysis not yet supported in this mode

### Page Sync Feature

The page sync feature monitors browser navigation and sends page content to the Decision Agent for analysis. This feature:
- Only works when explicitly enabled by the user
- Respects user privacy (requires opt-in)
- Sends HTML content, URL, title, and timestamp
- Can automatically prompt users about travel insurance needs

## 🛠️ Development Notes

- The React app runs in the side panel (loaded via `index.html`)
- The background service worker handles API calls and page monitoring
- The popup is a simple HTML/JS interface for settings
- Build outputs go to `build/` folder (git-ignored)

## 📝 TODO / Missing Components

The following components need to be created:
- `InsurancePromptListener` - Listens for insurance prompts from Decision Agent
- `MessageContent` - Component for rendering chat messages

See `src/App.tsx` for TODO comments.

## 🔒 Security Notes

- Never commit `config.js` with real API keys
- The extension requires `<all_urls>` permission for page sync feature
- Page content is only sent when user explicitly enables page sync

## 📚 Resources

- [Chrome Extension Documentation](https://developer.chrome.com/docs/extensions/)
- [Manifest V3 Guide](https://developer.chrome.com/docs/extensions/mv3/intro/)
- Original Figma design: https://www.figma.com/design/haspyeA28e870B4kpSlbeH/SINGHACK-Chrome-extention
