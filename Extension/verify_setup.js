/**
 * Verification Script
 * Paste this into the browser console to check if the extension is working
 */

console.log('=== Extension Verification Script ===');
console.log('');

// Check 1: Chrome Runtime
console.log('1. Checking chrome.runtime...');
if (typeof chrome !== 'undefined' && chrome.runtime) {
    console.log('   ✓ chrome.runtime exists');
    console.log('   Extension ID:', chrome.runtime.id);
} else {
    console.log('   ✗ chrome.runtime NOT available');
    console.log('   This page cannot access extension APIs');
}

// Check 2: Current URL
console.log('');
console.log('2. Checking current URL...');
console.log('   URL:', window.location.href);
if (window.location.protocol === 'chrome:' || 
    window.location.protocol === 'chrome-extension:' ||
    window.location.protocol === 'edge:') {
    console.log('   ✗ Content scripts cannot run on this type of URL');
    console.log('   Try opening http://example.com instead');
} else {
    console.log('   ✓ URL is compatible with content scripts');
}

// Check 3: Document State
console.log('');
console.log('3. Checking document state...');
console.log('   readyState:', document.readyState);
console.log('   body exists:', !!document.body);

// Check 4: Look for Decision Agent logs
console.log('');
console.log('4. Checking for Decision Agent logs...');
console.log('   Filter the console by: Decision Agent');
console.log('   You should see logs starting with [Decision Agent]');

// Check 5: Try to send a message
console.log('');
console.log('5. Testing message to background script...');
if (typeof chrome !== 'undefined' && chrome.runtime) {
    try {
        chrome.runtime.sendMessage({ action: 'test' }, (response) => {
            if (chrome.runtime.lastError) {
                console.log('   ✗ Error:', chrome.runtime.lastError.message);
            } else {
                console.log('   ✓ Background script responded');
            }
        });
    } catch (error) {
        console.log('   ✗ Exception:', error.message);
    }
} else {
    console.log('   ✗ Cannot test - chrome.runtime not available');
}

console.log('');
console.log('=== Verification Complete ===');
console.log('');
console.log('Next steps:');
console.log('1. If you see ✗ errors above, follow the troubleshooting guide');
console.log('2. Reload the extension at chrome://extensions/');
console.log('3. Reload this page');
console.log('4. Run this script again');



