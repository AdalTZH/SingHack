# AI Chat Assistant - Chrome Extension

A modern, clean chatbot interface that lives in your browser's sidebar, now powered by a **Master Agent** orchestration system!

## Features

- 🤖 **Modern UI**: Clean, gradient-based design with smooth animations
- 💬 **Sidebar Chat**: Stays accessible while you browse
- ⚙️ **Dual Mode**: Choose between Master Agent or direct OpenAI
- 🧠 **Multi-Agent System**: Routes queries to specialized agents
- 🔒 **Secure**: API key stored locally in Chrome's secure storage
- 📱 **Responsive**: Works beautifully on all screen sizes
- ⚡ **Fast**: Efficient message handling and real-time responses

## Installation

### 1. Download or Clone
```bash
git clone <your-repo-url>
cd SingHack
```

### 2. Load Extension in Chrome

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right corner)
3. Click **Load unpacked**
4. Select the `SingHack` folder

### 3. Configure Your API

Open `config.js` in a text editor and configure:

**Option A: Use Master Agent (Recommended)**
```javascript
const CONFIG = {
    USE_MASTER_AGENT: true,
    MASTER_AGENT_URL: 'http://localhost:8000',
    OPENAI_API_KEY: 'your-key'  // Still needed for fallback
};
```

**Option B: Direct OpenAI**
```javascript
const CONFIG = {
    USE_MASTER_AGENT: false,
    OPENAI_API_KEY: 'sk-your-actual-api-key-here'
};
```

**Note**: If using Master Agent, ensure the server is running at `http://localhost:8000`.

### 4. Start the Master Agent Server (if using Master Agent mode)

```bash
cd Server
python -m master_agent.server
```

### 5. Start Chatting

The side panel will open when you click the extension icon. Start typing your message and press Enter or click Send!

## Usage

- **Open Sidebar**: Click the extension icon
- **Send Message**: Type and press Enter or click the send button
- **Settings**: Click the ⚙️ icon in the header
- **Temperature**: Adjust creativity (0 = focused, 2 = creative)

### Master Agent Mode vs Direct OpenAI

**Master Agent Mode** (Recommended):
- Queries routed through intelligent orchestration
- Responses synthesized from specialized agents
- Better context understanding
- Multi-agent collaboration

**Direct OpenAI Mode**:
- Direct API calls to OpenAI
- Faster for simple queries
- Uses OpenAI credits directly

## Project Structure

```
SingHack/
├── manifest.json       # Extension configuration
├── background.js       # Service worker for API calls
├── config.js           # API key configuration (gitignored)
├── sidepanel.html      # Chat interface HTML
├── sidepanel.js        # Chat logic and UI handling
├── styles.css          # Modern UI styles
├── icons/              # Extension icons
└── README.md           # This file
```

## Configuration

Settings include:

- **API Key**: Preconfigured in `config.js` (see Step 3 of Installation)
- **Model**: GPT model to use (saved in Chrome's sync storage)
- **Temperature**: Response randomness (0-2, saved in Chrome's sync storage)

## API Key Security

✅ **Secure Configuration**: Your API key is stored separately in `config.js` which is gitignored.

- The `config.js` file is excluded from version control (.gitignore)
- You can safely share the extension code without exposing your API key
- Keep your `config.js` file private and never commit it

## Troubleshooting

**Side panel doesn't open:**
- Make sure you're using Chrome version 114 or later
- Try reloading the extension at `chrome://extensions/`

**Messages aren't sending:**
- Verify your API key is correctly set in `config.js`
- Check that you have API credits in your OpenAI account
- Look for error messages in the chat
- Make sure `config.js` exists and contains a valid API key

**API errors:**
- Ensure your API key has the right permissions
- Check your OpenAI account billing status
- Verify you're not exceeding rate limits

## Development

To modify the extension:

1. Make your changes to the source files
2. Go to `chrome://extensions/`
3. Click the **Reload** button on the extension card
4. Test your changes

## Privacy

- No data is collected or tracked
- Conversations stay in your browser
- API calls go directly to OpenAI
- No third-party analytics

## License

MIT License - feel free to use and modify!

## Support

For issues or questions, please open an issue on GitHub.

---

**Note**: This extension requires an active OpenAI API account and usage will be billed according to OpenAI's pricing.

