# Troubleshooting: Content Script Not Loading

## Quick Checklist

If you see **NO LOGS AT ALL** in the console:

### 1. ✓ Extension Loaded and Enabled
```
1. Go to chrome://extensions/
2. Enable "Developer mode" (top-right toggle)
3. Find "SingPass Insurance Chat"
4. Verify toggle is ON (blue)
5. Click reload button (circular arrow)
6. Look for any RED error messages on the card
```

### 2. ✓ Test on a Fresh Page
```
1. Open a NEW tab
2. Navigate to: http://example.com
3. Open console (F12)
4. Type in filter: Decision Agent
5. Reload the page (F5)
6. You should see logs immediately
```

### 3. ✓ Check Background Script
```
1. Go to chrome://extensions/
2. Find "SingPass Insurance Chat"
3. Click blue "service worker" link (opens console)
4. You should see: "SingPass Insurance Chat extension installed"
5. Open a new tab - you should see: "Tab activated: ..."
```

### 4. ✓ Verify Files Exist
Check these files exist in your Extension folder:
- `content.js` ✓
- `cursor-textbox.css` ✓
- `background.js` ✓
- `manifest.json` ✓

### 5. ✓ Check for Syntax Errors
```
1. Open any page
2. Open console (F12)
3. Look for RED errors
4. If you see errors mentioning content.js, there's a syntax error
```

## Common Error Messages

### "Uncaught SyntaxError"
**Cause**: JavaScript syntax error in content.js
**Solution**: Check the line number in the error, fix the syntax

### "Cannot access chrome runtime"
**Cause**: Extension not properly loaded
**Solution**: Reload extension, reload page

### "Receiving end does not exist"
**Cause**: Content script not responding to background script
**Solution**: This is the issue we're debugging - content script isn't loading

## Step-by-Step Debug Process

### Step 1: Verify Extension Loads
1. Go to `chrome://extensions/`
2. Look at "SingPass Insurance Chat" card
3. **If you see errors here**, the extension failed to load
4. Common issues:
   - manifest.json syntax error
   - Missing required files
   - Invalid permissions

### Step 2: Check Background Script Works
1. Click "service worker" link on extension card
2. Console should open
3. You should see: "SingPass Insurance Chat extension installed"
4. If not, there's an error in background.js

### Step 3: Test Content Script Injection
1. Open http://example.com in a new tab
2. Open console (F12)
3. Type: `Decision Agent` in filter
4. Reload page (F5)
5. **Expected**: See "[Decision Agent] Content script file loaded at: ..."
6. **If nothing**: Content script is NOT injecting

### Step 4: Manual Injection Test
If content script doesn't auto-inject, test manually:

1. Open any page
2. Open console (F12)
3. Paste this code and press Enter:
```javascript
console.log('[Manual Test] Testing if extension context exists');
console.log('[Manual Test] chrome.runtime:', typeof chrome.runtime);
```

If you see "undefined", the extension isn't accessible on this page.

### Step 5: Check Manifest Content Scripts
The manifest should have:
```json
"content_scripts": [
  {
    "matches": ["<all_urls>"],
    "js": ["content.js"],
    "css": ["cursor-textbox.css"],
    "run_at": "document_idle"
  }
]
```

Verify:
- `matches` includes `<all_urls>` ✓
- `js` array includes `content.js` ✓
- Files exist in Extension folder ✓

## What URL Are You Testing On?

Content scripts **WILL NOT** work on:
- ❌ `chrome://` pages (extensions, settings, etc.)
- ❌ `chrome-extension://` pages
- ❌ `edge://` pages
- ❌ `about:` pages
- ❌ Chrome Web Store pages

Content scripts **WILL** work on:
- ✅ `http://` pages
- ✅ `https://` pages
- ✅ Local files (if you enable "Allow access to file URLs" in extension settings)

## Still Not Working?

### Try This Nuclear Option:
1. Go to `chrome://extensions/`
2. Click "Remove" on "SingPass Insurance Chat"
3. Click "Load unpacked"
4. Select the `Extension` folder
5. Open a NEW tab with http://example.com
6. Check console

### Check Extension Folder Structure:
```
Extension/
├── manifest.json
├── background.js
├── content.js
├── cursor-textbox.css
├── sidepanel.html
├── sidepanel.js
├── popup.html
└── (other files...)
```

### Verify manifest.json is Valid JSON:
1. Open manifest.json
2. Copy entire contents
3. Go to https://jsonlint.com/
4. Paste and validate
5. Fix any errors shown

## Getting More Debug Info

Add this to the very top of `content.js` (line 1):
```javascript
console.log('[CONTENT SCRIPT] File executed!', window.location.href);
```

This will log IMMEDIATELY when the file runs, before any other code.

If you don't see this log, the file is NOT being loaded by Chrome.

## Next Steps

If you've tried everything above and still see no logs:

1. **Check Chrome version**: Go to `chrome://version/` - should be recent
2. **Try a different browser**: Test in Edge or Brave (Chromium-based)
3. **Check file permissions**: Ensure content.js is readable
4. **Look for antivirus interference**: Some security software blocks extensions

## Report the Issue

If nothing works, provide:
1. Chrome version (`chrome://version/`)
2. Operating system
3. Screenshot of `chrome://extensions/` showing the extension
4. Screenshot of console with filter "Decision Agent"
5. Screenshot of background script console (service worker)
6. Any error messages (red text) from any console



