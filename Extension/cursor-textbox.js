/**
 * Cursor TextBox Content Script
 * 
 * This script injects a cursor-following textbox into any webpage.
 * It works independently of the extension's React app and runs on all pages.
 */

(function() {
  'use strict';

  // Don't run on extension pages or chrome:// pages
  if (window.location.protocol === 'chrome-extension:' || 
      window.location.protocol === 'chrome:') {
    return;
  }

  // Wait for document body to be ready
  function waitForBody(callback) {
    if (document.body) {
      callback();
    } else {
      const observer = new MutationObserver(() => {
        if (document.body) {
          observer.disconnect();
          callback();
        }
      });
      observer.observe(document.documentElement, { childList: true, subtree: true });
    }
  }

  // Check if already injected to prevent duplicates
  function checkAndInit() {
    if (document.getElementById('cursor-textbox-extension')) {
      return;
    }

    // Check if cursor textbox is enabled
    let isEnabled = true; // Default to enabled

    // Try to load setting from storage with timeout
    let storageLoaded = false;
    const storageTimeout = setTimeout(() => {
      if (!storageLoaded) {
        // If storage doesn't respond in 500ms, default to enabled
        console.log('Cursor textbox: Storage timeout, defaulting to enabled');
        if (isEnabled) {
          initCursorTextBox();
        }
      }
    }, 500);

    // Load setting from storage
    try {
      chrome.storage.sync.get(['cursorTextBoxEnabled'], (result) => {
        storageLoaded = true;
        clearTimeout(storageTimeout);
        isEnabled = result.cursorTextBoxEnabled !== false; // Default to true if not set
        if (isEnabled) {
          initCursorTextBox();
        }
      });
    } catch (error) {
      storageLoaded = true;
      clearTimeout(storageTimeout);
      console.error('Cursor textbox: Error loading storage, defaulting to enabled', error);
      if (isEnabled) {
        initCursorTextBox();
      }
    }

    // Listen for changes to the setting
    chrome.storage.onChanged.addListener((changes, areaName) => {
      if (areaName === 'sync' && changes.cursorTextBoxEnabled) {
        isEnabled = changes.cursorTextBoxEnabled.newValue !== false;
        if (isEnabled) {
          if (!document.getElementById('cursor-textbox-extension')) {
            initCursorTextBox();
          }
        } else {
          const existing = document.getElementById('cursor-textbox-extension');
          if (existing) {
            existing.remove();
          }
        }
      }
    });

    // Listen for messages from popup/background
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      if (message.type === 'toggleCursorTextBox') {
        isEnabled = message.enabled !== false;
        if (isEnabled) {
          if (!document.getElementById('cursor-textbox-extension')) {
            initCursorTextBox();
          }
        } else {
          const existing = document.getElementById('cursor-textbox-extension');
          if (existing) {
            existing.remove();
          }
        }
      }
    });
  }

  function initCursorTextBox() {
    // Check if already exists
    if (document.getElementById('cursor-textbox-extension')) {
      console.log('Cursor textbox: Already exists, skipping');
      return;
    }

    // Make sure body exists
    if (!document.body) {
      console.warn('Cursor textbox: document.body not ready');
      return;
    }

    console.log('Cursor textbox: Initializing...');

    // Create the textbox element
    const textbox = document.createElement('div');
    textbox.id = 'cursor-textbox-extension';
    textbox.style.cssText = `
      position: fixed;
      pointer-events: none;
      z-index: 999999;
      opacity: 1;
      transform: scale(1);
      left: 100px;
      top: 100px;
      transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    `;

    // Create inner container with glassmorphism styling
    const innerContainer = document.createElement('div');
    innerContainer.style.cssText = `
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      background: rgba(255, 255, 255, 0.2);
      border: 1px solid rgba(255, 255, 255, 0.3);
      border-radius: 8px;
      padding: 8px 16px;
      box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37), inset 0 2px 4px rgba(255, 255, 255, 0.1);
    `;

    // Create text span
    const textSpan = document.createElement('span');
    textSpan.textContent = 'Leo is handsome';
    textSpan.style.cssText = `
      color: white;
      font-size: 14px;
      white-space: nowrap;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    `;

    // Assemble the structure
    innerContainer.appendChild(textSpan);
    textbox.appendChild(innerContainer);
    document.body.appendChild(textbox);

    // Mouse position tracking - initialize to center of screen
    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;
    let isVisible = true; // Start visible since opacity is 1

    // Update position function with smooth animation
    function updatePosition() {
      // Position with offset (20px right and down from cursor)
      const offsetX = 20;
      const offsetY = 20;
      
      // Use requestAnimationFrame for smooth updates
      requestAnimationFrame(() => {
        if (textbox && textbox.parentNode) {
          const left = mouseX + offsetX;
          const top = mouseY + offsetY;
          textbox.style.left = `${left}px`;
          textbox.style.top = `${top}px`;
          textbox.style.opacity = '1';
          textbox.style.transform = 'scale(1)';
        }
      });
    }

    // Mouse move handler
    function handleMouseMove(e) {
      mouseX = e.clientX;
      mouseY = e.clientY;
      updatePosition();
    }

    // Mouse leave handler (hide when mouse leaves window)
    function handleMouseLeave() {
      if (textbox) {
        textbox.style.opacity = '0';
        textbox.style.transform = 'scale(0.8)';
        isVisible = false;
      }
    }

    // Add event listeners
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseleave', handleMouseLeave);

    // Handle page visibility changes
    document.addEventListener('visibilitychange', () => {
      if (document.hidden && textbox) {
        textbox.style.opacity = '0';
        isVisible = false;
      }
    });

    // Cleanup function (for when script is removed)
    window.addEventListener('beforeunload', () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseleave', handleMouseLeave);
      if (textbox && textbox.parentNode) {
        textbox.parentNode.removeChild(textbox);
      }
    });

    // Initial positioning - set immediately and on mouse move
    updatePosition();
    console.log('Cursor textbox: Created and positioned at', mouseX, mouseY);
    
    // Also update on window resize
    window.addEventListener('resize', () => {
      if (mouseX === 0 && mouseY === 0) {
        mouseX = window.innerWidth / 2;
        mouseY = window.innerHeight / 2;
        updatePosition();
      }
    });
  }

  // Wait for body, then initialize
  waitForBody(checkAndInit);
})();
