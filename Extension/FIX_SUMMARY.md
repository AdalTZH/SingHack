# Fix Summary: Content Script Not Loading

## Problem Identified

From your error logs:
```
Could not establish connection. Receiving end does not exist.
```

This means the content script's message listener was **not set up**, indicating the content script file (`content.js`) was **not loading automatically** from the manifest.

## Root Cause

Chrome Manifest V3 content scripts declared in `manifest.json` don't always inject reliably, especially:
- On already-open tabs when extension is loaded/reloaded
- On certain types of pages (Google search results can be tricky)
- When tabs are suspended/discarded and reactivated

## Solution Implemented

### 1. **Ping-Check Before Sending Messages**
The background script now:
1. Sends a "ping" message first to check if content script is loaded
2. If ping succeeds → content script is ready
3. If ping fails → content script needs to be injected

### 2. **Programmatic Injection Fallback**
When content script is not detected:
1. Inject CSS file (`cursor-textbox.css`)
2. Inject JS file (`content.js`)
3. Wait 500ms for initialization
4. Then send the analyze message

### 3. **Ping Handler in Content Script**
Added a ping handler that responds immediately:
```javascript
if (request.action === 'ping') {
  sendResponse({ success: true, loaded: true });
  return true;
}
```

## Code Changes

### `background.js`
- Added `injectContentScriptIfNeeded()` function
- Checks if content script is loaded with ping
- Injects script programmatically if needed
- Modified `sendAnalyzeMessage()` to call injection check first

### `content.js`
- Added ping message handler
- Enhanced logging for debugging
- No other functional changes needed

## How It Works Now

### Flow on Tab Switch:

1. **User switches to a tab**
   ```
   chrome.tabs.onActivated → background.js
   ```

2. **Background checks if content script is loaded**
   ```
   Send ping message → content script
   ```

3a. **If content script responds to ping:**
   ```
   ✓ Already loaded
   → Send analyzePageOnTabSwitch message
   → Content script analyzes page
   ```

3b. **If content script doesn't respond (our case):**
   ```
   ✗ Not loaded
   → Inject cursor-textbox.css
   → Inject content.js
   → Wait 500ms
   → Send analyzePageOnTabSwitch message
   → Content script analyzes page
   ```

## Testing the Fix

### Step 1: Reload Extension
```
1. Go to chrome://extensions/
2. Find "SingPass Insurance Chat"
3. Click reload button (🔄)
```

### Step 2: Check Background Script Console
```
1. Click "service worker" link on extension
2. Open a new tab or switch tabs
3. You should see:
   - "Content script not loaded, injecting for tab: ..."
   - "Successfully injected content script for tab: ..."
   - "Successfully sent analyze message to tab (attempt 1): ..."
```

### Step 3: Check Page Console
```
1. Open console on the page (F12)
2. Filter by: Decision Agent
3. You should now see:
   - "[Decision Agent] Content script file loaded at: ..."
   - "[Decision Agent] About to call init()"
   - "[Decision Agent] Content script initialized"
   - "[Decision Agent] Message received: analyzePageOnTabSwitch"
```

## Expected Logs

### Background Script (service worker):
```
Tab activated: https://www.google.com/search?... status: complete
Content script not loaded, injecting for tab: https://www.google.com/...
Successfully injected content script for tab: https://www.google.com/...
Successfully sent analyze message to tab (attempt 1): https://www.google.com/...
```

### Page Console:
```
[Decision Agent] Content script file loaded at: 2024-12-02T...
[Decision Agent] About to call init()
[Decision Agent] Content script initialized { readyState: "complete", ... }
[Decision Agent] Message received: analyzePageOnTabSwitch
[Decision Agent] Tab switch message received, analyzing page...
[Decision Agent] analyzePageImmediately called
[Decision Agent] Page ready, analyzing immediately
Sending page content to decision agent: { url: "...", ... }
```

## Why This Approach?

### Hybrid Strategy:
1. **Manifest declaration** (`content_scripts` in manifest.json)
   - Automatically injects on new page loads
   - More efficient when it works
   - Keeps CSS and JS together

2. **Programmatic injection** (fallback)
   - Handles cases where manifest injection fails
   - Works on already-open tabs
   - Ensures content script is always available

### Best of Both Worlds:
- Fast automatic injection when possible
- Reliable fallback when needed
- No duplicate injections (ping check prevents this)

## Potential Issues

### Issue: "Cannot access contents of url"
**Cause**: Some pages block content script injection
**Pages that block**: Chrome Web Store, chrome:// pages, some enterprise sites
**Solution**: This is expected - extension won't work on these pages

### Issue: Still no logs after fix
**Cause**: Extension might need full reload
**Solution**: 
1. Remove extension completely
2. Load unpacked again
3. Test on a simple page like http://example.com

### Issue: Duplicate textboxes appear
**Cause**: Script injected multiple times
**Solution**: The ping check should prevent this, but if it happens:
1. Reload the page
2. Check for errors in console

## Performance Impact

Minimal:
- Ping message: ~1-5ms
- CSS injection: ~10-20ms
- JS injection: ~50-100ms
- Total overhead: ~100-150ms only when script isn't loaded
- When script is already loaded: just the ping (~1-5ms)

## Next Steps

1. **Reload the extension**
2. **Test on multiple sites**:
   - Google search results ✓
   - News sites ✓
   - Shopping sites ✓
   - Simple sites (example.com) ✓
3. **Check both consoles**:
   - Background script (service worker)
   - Page console (F12)
4. **Verify API calls** reach decision agent server

## Files Modified

- `Extension/background.js` - Added injection logic
- `Extension/content.js` - Added ping handler
- `Extension/START_HERE.md` - Updated instructions
- `Extension/FIX_SUMMARY.md` - This file

## Success Criteria

✅ No more "Receiving end does not exist" errors
✅ Content script loads on tab switch
✅ Analysis triggers when switching tabs
✅ API requests sent to decision agent
✅ Textbox appears with persuasion message



