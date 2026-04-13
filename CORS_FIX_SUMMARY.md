# CORS Fix for Summary Agent

## Problem

**Error:** `TypeError: Failed to fetch`

**Root Cause:**
- Extension content scripts cannot make direct fetch requests to `localhost` due to CORS restrictions
- Summary Agent was being called directly from `content.js`, which failed with CORS error

## Solution

Route Summary Agent requests through `background.js` (same pattern as Decision Agent).

### Why This Works

1. **Content scripts** run in the context of web pages → **CORS restricted**
2. **Background scripts** run in the extension context → **No CORS restrictions**
3. Background scripts can make requests to any URL, including localhost

## Files Changed

### ✅ Extension/background.js

Added new message handler for `summarizePage` action:

```javascript
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'summarizePage') {
    // Validate request
    // Call http://localhost:8020/summarize
    // Return response to content script
    return true; // Async response
  }
  // ... existing analyzePage handler
});
```

### ✅ Extension/content.js

Updated `callSummaryAgent()` to use `chrome.runtime.sendMessage` instead of direct fetch:

**Before (❌ CORS Error):**
```javascript
const response = await fetch('http://localhost:8020/summarize', {
  method: 'POST',
  body: JSON.stringify({...})
});
```

**After (✅ Works):**
```javascript
const response = await new Promise((resolve, reject) => {
  chrome.runtime.sendMessage({
    action: 'summarizePage',
    inner_text: innerText,
    url: url,
    title: title,
    travel_context: travelContext
  }, (response) => {
    if (response.success) {
      resolve(response.data);
    } else {
      reject(new Error(response.error));
    }
  });
});
```

## Architecture

```
Extension Content Script (content.js)
    ↓ chrome.runtime.sendMessage({action: 'summarizePage'})
Extension Background Script (background.js)
    ↓ fetch('http://localhost:8020/summarize')
Summary Agent Server
    ↓ Returns summary
Background Script
    ↓ sendResponse({success: true, data: summary})
Content Script
    ↓ Stores in localStorage
```

## Testing

### 1. Reload Extension

After updating the code:
1. Go to `chrome://extensions`
2. Find your extension
3. Click the reload icon 🔄

### 2. Test on Travel Site

1. Visit a travel website (e.g., Google Flights)
2. Open DevTools Console
3. Look for:

```
✅ Good:
📊 Character count sent to Decision Agent: 8523 characters
📝 Calling Summary Agent via background script...
Background: Sending request to summary agent...
Background: Received successful response from summary agent
✅ Summary generated successfully
📦 Stored page summary in localStorage

❌ Bad (CORS Error):
Error calling Summary Agent: TypeError: Failed to fetch
```

### 3. Verify Background Script

Open extension background page:
1. `chrome://extensions` → Click "service worker" or "background page"
2. Should see:

```
Background: Sending request to summary agent: {url: "...", title: "..."}
Background: Received successful response from summary agent
```

## Common Issues

### Extension not reloaded
- **Fix:** Reload extension at `chrome://extensions`

### Summary Agent not running
- **Fix:** Start server: `python Server/start_summary_agent.py`
- **Verify:** `curl http://localhost:8020/health`

### Background script error
- **Fix:** Check background page console for errors
- **Access:** `chrome://extensions` → "service worker" link

## Verification Checklist

- ✅ Extension reloaded
- ✅ Summary Agent running on port 8020
- ✅ No CORS errors in console
- ✅ Background script receives requests
- ✅ Summaries stored in localStorage
- ✅ Master Agent receives summaries

## Related Pattern

This is the **same pattern** used for Decision Agent:

| Agent | Port | Route Through Background? |
|-------|------|---------------------------|
| Decision Agent | 8004 | ✅ Yes (already implemented) |
| Summary Agent | 8020 | ✅ Yes (just fixed) |
| Master Agent | 9000 | ❌ No (called from sidepanel via fetch - no CORS issue) |

**Why Master Agent doesn't need this:**
- Sidepanel/popup context has different CORS rules
- Can make direct fetch requests to localhost
- Only content scripts are restricted

---

**Status:** ✅ CORS Issue Fixed - Summary Agent now works correctly!


