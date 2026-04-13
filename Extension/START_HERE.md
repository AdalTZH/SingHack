# 🚀 START HERE - No Logs Appearing?

## 🚨 CRITICAL: Host Permissions Fixed!

**If you just updated the code, you MUST reload the extension!**

The manifest was missing host permissions for websites. This is now fixed.

**ACTION REQUIRED:**
1. Go to `chrome://extensions/`
2. Find "SingPass Insurance Chat"
3. Click the **reload button** (🔄)
4. Accept any permission prompts

**Then continue with testing below...**

---

## Quick Fix (Try This First!)

### Step 1: Reload Extension
1. Open Chrome
2. Type in address bar: `chrome://extensions/`
3. Find **"SingPass Insurance Chat"**
4. Click the **reload button** (🔄 circular arrow icon)

### Step 2: Open Test Page
1. In a NEW tab, type: `http://example.com`
2. Press Enter
3. Right-click anywhere → **Inspect** → **Console** tab

### Step 3: Check for Logs
1. In the console filter box, type: `Decision Agent`
2. Press **F5** to reload the page
3. You should see:
   ```
   [Decision Agent] Content script file loaded at: 2024-...
   [Decision Agent] About to call init()
   [Decision Agent] Content script initialized { readyState: "complete", ... }
   ```

### ✅ If You See Logs
**Success!** The extension is working. Now test tab switching:
1. Open another tab
2. Switch back to example.com
3. You should see: `[Decision Agent] Message received: analyzePageOnTabSwitch`

### ❌ If You See NO Logs
**The content script is not loading automatically.**

This is now fixed! The extension will now:
1. Try to send a "ping" to check if the content script is loaded
2. If not loaded, it will inject the content script programmatically
3. Then send the analyze message

**What you need to do:**
1. Go to `chrome://extensions/`
2. Click the **reload button** on "SingPass Insurance Chat"
3. Open a new tab or switch tabs
4. Check the background script console (click "service worker" link)
5. You should see: "Content script not loaded, injecting for tab: ..."
6. Then: "Successfully injected content script for tab: ..."

Continue to troubleshooting below if still not working...

---

## Troubleshooting: No Logs

### Check 1: Is Developer Mode Enabled?
1. Go to `chrome://extensions/`
2. Look at top-right corner
3. Toggle **"Developer mode"** to ON (should be blue)

### Check 2: Is Extension Enabled?
1. On the extension card, check the toggle switch
2. Should be blue/ON
3. If OFF, click to enable

### Check 3: Are You on the Right URL?
Content scripts **DO NOT** work on:
- ❌ `chrome://` pages
- ❌ `chrome-extension://` pages  
- ❌ Chrome Web Store
- ❌ `about:` pages

Content scripts **DO** work on:
- ✅ `http://example.com`
- ✅ `https://google.com`
- ✅ Any normal website

### Check 4: Check Background Script
1. Go to `chrome://extensions/`
2. Find "SingPass Insurance Chat"
3. Click the blue **"service worker"** link
4. A console window opens
5. You should see: `SingPass Insurance Chat extension installed`
6. If you see errors (red text), there's a problem

### Check 5: Run Verification Script
1. Open any website (e.g., http://example.com)
2. Open console (F12)
3. Copy the entire contents of `Extension/verify_setup.js`
4. Paste into console and press Enter
5. Follow the diagnostic output

---

## Still Not Working?

### Nuclear Option: Reinstall Extension
1. Go to `chrome://extensions/`
2. Click **"Remove"** on "SingPass Insurance Chat"
3. Click **"Load unpacked"** button
4. Navigate to and select the **`Extension`** folder
5. Open a new tab: `http://example.com`
6. Open console (F12) and check for logs

### Check File Structure
Your Extension folder should have:
```
Extension/
├── manifest.json          ← Must exist
├── background.js          ← Must exist
├── content.js            ← Must exist
├── cursor-textbox.css    ← Must exist
├── sidepanel.html
├── sidepanel.js
├── popup.html
├── test.html             ← New test file
├── verify_setup.js       ← Verification script
└── ...
```

### Verify manifest.json
1. Open `Extension/manifest.json`
2. Check line 28-35:
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

---

## Testing Tab Switch Feature

Once you see logs appearing:

### Test 1: Switch to Existing Tab
1. Open `http://example.com` in Tab 1
2. Open `http://google.com` in Tab 2
3. Switch back to Tab 1
4. Check console - should see: `[Decision Agent] Tab switch message received`

### Test 2: Open New Tab
1. Open a new tab with any website
2. Wait for page to load
3. Check console - should see analysis triggered

### Test 3: Check API Request
1. Switch tabs
2. Check console for: `Sending page content to decision agent`
3. Check server terminal - should see API request logged

---

## Understanding the Logs

### On Page Load:
```
[Decision Agent] Content script file loaded at: ...
[Decision Agent] About to call init()
[Decision Agent] Content script initialized { ... }
```

### On Tab Switch:
```
[Decision Agent] Message received: analyzePageOnTabSwitch
[Decision Agent] Tab switch message received, analyzing page...
[Decision Agent] analyzePageImmediately called
[Decision Agent] Page ready, analyzing immediately
Sending page content to decision agent: { url: "...", ... }
```

### On API Response:
```
Decision agent response: { ... }
Response check: { ... }
Creating textbox with message: ...
```

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| No logs at all | Reload extension, reload page, check URL is http:// or https:// |
| "Receiving end does not exist" | Content script not loaded - reload extension |
| Logs appear but no tab switch trigger | Check background script console for errors |
| API request fails | Check decision agent server is running on port 8004 |
| Textbox doesn't appear | Check server response has `persuasion_message` field |

---

## Need More Help?

1. Read `TROUBLESHOOTING.md` for detailed diagnostics
2. Read `DEBUG_TAB_SWITCH.md` for technical details
3. Check background script console (service worker link)
4. Check decision agent server logs in terminal

---

## Quick Reference

| Action | Command/Location |
|--------|------------------|
| Extensions page | `chrome://extensions/` |
| Open console | F12 or Right-click → Inspect |
| Filter console | Type in filter box: `Decision Agent` |
| Reload extension | Click 🔄 on extension card |
| Reload page | F5 or Ctrl+R |
| Background console | Click "service worker" link |
| Test page | Open `Extension/test.html` in browser |

