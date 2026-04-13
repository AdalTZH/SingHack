# 🚨 CRITICAL FIX: Host Permissions Missing

## The Real Problem

Your error message revealed the root cause:
```
Cannot access contents of url "https://www.google.com/...". 
Extension manifest must request permission to access this host.
```

## What Was Wrong

The `manifest.json` only had host permissions for `localhost`:
```json
"host_permissions": [
  "http://localhost:9000/*",
  "http://localhost:8007/*",
  "http://localhost:8004/*",
  "http://127.0.0.1:8004/*"
]
```

This meant the extension could:
- ✅ Make API calls to localhost
- ❌ Inject content scripts on ANY website (Google, etc.)

## The Fix

Added wildcard host permissions:
```json
"host_permissions": [
  "http://localhost:9000/*",
  "http://localhost:8007/*",
  "http://localhost:8004/*",
  "http://127.0.0.1:8004/*",
  "http://*/*",      ← NEW: All HTTP sites
  "https://*/*"      ← NEW: All HTTPS sites
]
```

Now the extension can:
- ✅ Make API calls to localhost
- ✅ Inject content scripts on any website
- ✅ Work on Google search results
- ✅ Work on any http:// or https:// page

## What You Need to Do

### IMPORTANT: Reload the Extension

The manifest change requires a full extension reload:

1. **Go to** `chrome://extensions/`
2. **Find** "SingPass Insurance Chat"
3. **Click** the reload button (🔄)
4. **You may see a permission prompt** - Click "Allow" or "Accept"

### Test It Now

1. **Open a new tab** with Google search: https://www.google.com/search?q=test
2. **Open console** (F12)
3. **Filter by**: `Decision Agent`
4. **Switch to another tab and back**
5. **You should see**:
   ```
   [Decision Agent] Content script file loaded at: ...
   [Decision Agent] Content script initialized
   [Decision Agent] Message received: analyzePageOnTabSwitch
   ```

### Check Background Script

1. **Go to** `chrome://extensions/`
2. **Click** "service worker" link
3. **Switch tabs**
4. **You should see**:
   ```
   Tab activated: https://www.google.com/... status: complete
   Content script not loaded, injecting for tab: ...
   Successfully injected content script for tab: ...
   Successfully sent analyze message to tab (attempt 1): ...
   ```

## Why This Happened

### Manifest V3 Permissions Model

Chrome Manifest V3 has strict permission requirements:

1. **Content Scripts** (`content_scripts` in manifest)
   - Can match `<all_urls>` ✓
   - But only for **reading** page content
   - Cannot be injected programmatically without host permissions

2. **Programmatic Injection** (`chrome.scripting.executeScript`)
   - Requires explicit `host_permissions` for the target URL
   - Our fallback injection was failing due to missing permissions

3. **Host Permissions** (`host_permissions` in manifest)
   - Required for programmatic script injection
   - Required for making fetch requests to external hosts
   - Required for accessing tab content programmatically

## What Changed

### Before (Broken):
```
User switches to Google → 
Background tries to inject content script → 
❌ "Cannot access contents" error → 
No analysis happens
```

### After (Fixed):
```
User switches to Google → 
Background tries to inject content script → 
✅ Permission granted → 
Content script injected → 
Analysis triggered → 
API call to decision agent → 
Textbox appears
```

## Security Note

The extension now requests permission to access all websites. This is standard for extensions that:
- Inject content scripts
- Analyze page content
- Work across multiple websites

Users will see this permission request when installing/updating the extension.

## Testing Checklist

After reloading the extension:

- [ ] Extension reloaded at `chrome://extensions/`
- [ ] Permissions accepted (if prompted)
- [ ] Test on Google search results
- [ ] Test on news websites
- [ ] Test on shopping sites
- [ ] Check background script console - no "Cannot access" errors
- [ ] Check page console - see [Decision Agent] logs
- [ ] API requests reach decision agent server
- [ ] Textbox appears with persuasion message

## Common Questions

### Q: Why does the extension need access to all websites?
**A:** To inject the content script that analyzes page content and displays the decision agent's response.

### Q: Is this safe?
**A:** Yes, the extension only:
- Reads page text content (no passwords, no form data)
- Sends content to your local decision agent server (localhost:8004)
- Displays a textbox with the response
- Does not collect or transmit data to external servers

### Q: Can I limit it to specific sites?
**A:** Yes, but you'd need to list every site individually in `host_permissions`. The wildcard `http://*/*` and `https://*/*` is more practical for a general-purpose extension.

## Files Modified

- ✅ `Extension/manifest.json` - Added host permissions

## Next Steps

1. **Reload the extension** (critical!)
2. **Test on multiple sites**
3. **Verify no "Cannot access" errors**
4. **Enjoy working tab switch detection!**

---

## Summary

**Problem**: Missing host permissions prevented content script injection
**Solution**: Added `"http://*/*"` and `"https://*/*"` to `host_permissions`
**Action Required**: Reload the extension at `chrome://extensions/`
**Expected Result**: Content script now injects successfully on all websites



