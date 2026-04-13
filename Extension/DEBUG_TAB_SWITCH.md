# Debug Tab Switch Issues

## Changes Made

### 1. Removed Duplicate Script Injection
**Problem**: `chrome.scripting.executeScript` was creating duplicate instances of the content script, causing conflicts.

**Solution**: Removed programmatic injection. Content script is auto-injected via manifest, so we just send messages directly.

### 2. Improved Retry Logic
- Increased retries from 3 to 5
- Progressive delays: 150ms, 300ms, 450ms, 600ms
- Better error logging

### 3. Enhanced Logging
All logs now prefixed with `[Decision Agent]` for easy filtering:
- Content script initialization
- Message reception
- Analysis triggers
- Page state checks

## How to Test

### Step 1: Reload the Extension
1. Go to `chrome://extensions/`
2. Find "SingPass Insurance Chat"
3. **Enable Developer Mode** (toggle in top-right if not already on)
4. Click the reload button (circular arrow)
5. Check for any errors displayed on the extension card

### Step 2: Open Test Page
1. Open `Extension/test.html` in your browser (drag and drop the file into Chrome)
2. OR navigate to any http:// or https:// website

### Step 3: Open Browser Console
1. Right-click on the page → Inspect
2. Go to Console tab
3. **IMPORTANT**: Clear the console (trash icon or Ctrl+L)
4. Filter by typing: `Decision Agent`

### Step 4: Reload the Page
1. Press F5 or Ctrl+R to reload the page
2. You should immediately see:
   ```
   [Decision Agent] Content script file loaded at: ...
   [Decision Agent] About to call init()
   [Decision Agent] Content script initialized
   ```

### Step 5: Test Tab Switching
1. Open another tab
2. Switch back to the test page
3. Watch the console for:
   ```
   [Decision Agent] Message received: analyzePageOnTabSwitch
   [Decision Agent] Tab switch message received, analyzing page...
   ```

### Expected Console Output

When switching to a tab, you should see:

```
[Decision Agent] Content script initialized { readyState: "complete", url: "...", timestamp: "..." }
[Decision Agent] Message received: analyzePageOnTabSwitch
[Decision Agent] Tab switch message received, analyzing page... { readyState: "complete", url: "...", ... }
[Decision Agent] analyzePageImmediately called
[Decision Agent] Page ready, analyzing immediately
Sending page content to decision agent: { url: "...", title: "...", contentLength: ... }
```

### Background Script Logs

To see background script logs:
1. Go to `chrome://extensions/`
2. Find "SingPass Insurance Chat"
3. Click "service worker" link
4. Check console for:
   - "Tab activated: ..."
   - "Successfully sent analyze message to tab (attempt 1): ..."

## Common Issues

### Issue: No logs appear at all
**Cause**: Content script not loading

**Detailed Troubleshooting**:

1. **Check Extension is Loaded**:
   - Go to `chrome://extensions/`
   - Find "SingPass Insurance Chat"
   - Verify it's enabled (toggle ON)
   - Look for any error messages on the extension card

2. **Check for JavaScript Errors**:
   - Open console on the test page
   - Look for RED error messages
   - If you see syntax errors or reference errors, the script failed to load

3. **Check Background Script**:
   - Go to `chrome://extensions/`
   - Find "SingPass Insurance Chat"
   - Click the blue "service worker" link
   - Check console for errors
   - Try switching tabs and see if "Tab activated:" logs appear

4. **Check Content Script Files Exist**:
   - Verify `Extension/content.js` exists
   - Verify `Extension/cursor-textbox.css` exists
   - Check file paths in `Extension/manifest.json`

5. **Try a Fresh Page**:
   - Open a NEW tab with a simple website (e.g., example.com)
   - The content script should inject when the page loads
   - Check console immediately

6. **Reload Everything**:
   - Reload the extension at `chrome://extensions/`
   - Close ALL tabs
   - Open a new tab with `Extension/test.html`
   - Check console immediately

### Issue: "Failed to send message after all retries"
**Cause**: Content script not responding
**Solution**:
- Check content script console for errors
- Verify the page allows content scripts
- Try a different website

### Issue: Analysis runs but no textbox appears
**Cause**: Decision agent might not be returning a persuasion message
**Solution**:
- Check if decision agent server is running on port 8004
- Check server logs for the API request
- Verify the response has `persuasion_message` field

## Testing Checklist

- [ ] Extension reloaded
- [ ] Console open and filtered
- [ ] Switch to already-loaded tab → logs appear
- [ ] Switch to new tab → logs appear after load
- [ ] API request sent to localhost:8004
- [ ] Textbox appears (if persuasion message exists)

## Key Files Modified

- `Extension/background.js` - Removed duplicate injection, improved retries
- `Extension/content.js` - Added logging, immediate analysis for tab switches

