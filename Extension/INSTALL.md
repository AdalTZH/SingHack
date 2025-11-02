# Installation Guide

## Quick Start

Follow these simple steps to get your AI Chat Assistant running:

### Step 1: Get Your OpenAI API Key

1. Visit [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy your API key (starts with `sk-`)

⚠️ **Important**: You'll need this key in Step 2!

### Step 2: Configure Your API Key **BEFORE Loading Extension**

This must be done before loading the extension in Chrome!

1. Open `config.js` in any text editor
2. Find this line: `OPENAI_API_KEY: 'YOUR_API_KEY_HERE'`
3. Replace `YOUR_API_KEY_HERE` with your actual API key from Step 1
4. Save the file

```javascript
const CONFIG = {
    OPENAI_API_KEY: 'sk-your-actual-api-key-here'
};
```

**Note**: The `config.js` file is gitignored, so your API key won't be committed to version control.

### Step 3: Load Extension in Chrome

1. Open Google Chrome
2. Type `chrome://extensions/` in the address bar and press Enter
3. Toggle **Developer mode** ON (switch in the top-right corner)
4. Click **Load unpacked** button
5. Navigate to and select your `SingHack` folder
6. The extension should now appear in your list

### Step 4: Pin the Extension (Optional but Recommended)

1. Click the puzzle piece icon (🧩) in Chrome's toolbar
2. Find "AI Chat Assistant" in the list
3. Click the pin icon to keep it visible

### Step 5: Start Chatting!

🎉 You're all set! Click the extension icon anytime to open the chatbot sidebar and start chatting.

## Troubleshooting

**Problem**: "Load unpacked" button is grayed out  
**Solution**: Make sure Developer mode is enabled

**Problem**: Side panel doesn't open  
**Solution**: 
- Check you're using Chrome 114 or later
- Reload the extension at `chrome://extensions/`

**Problem**: "Invalid API key" error  
**Solution**:
- Make sure you replaced `YOUR_API_KEY_HERE` in `config.js` with your actual key
- Ensure your API key starts with `sk-`
- Verify `config.js` file exists in the extension folder
- Reload the extension after updating `config.js`
- Try generating a new key from OpenAI dashboard

**Problem**: Messages won't send  
**Solution**:
- Verify you have credits in your OpenAI account
- Check your API key permissions
- Look for error messages in the chat

## Requirements

- **Browser**: Google Chrome version 114 or later
- **Account**: Active OpenAI account with API access
- **Internet**: Active connection for API calls

## Security Notes

✅ **Secure Configuration**: Your API key is stored separately in `config.js`.

✅ API key is in `config.js` which is gitignored  
✅ No data is sent to third-party servers  
✅ Conversations stay private in your browser  
✅ You can safely commit code without exposing your API key

