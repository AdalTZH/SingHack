// Popup JavaScript for Page Sync Settings

// DOM Elements
const enableSyncCheckbox = document.getElementById('enableSync');
const toggleSwitch = document.getElementById('toggleSwitch');
const enableCursorTextBoxCheckbox = document.getElementById('enableCursorTextBox');
const cursorTextBoxToggle = document.getElementById('cursorTextBoxToggle');
const lastSentTime = document.getElementById('lastSentTime');
const lastSentUrl = document.getElementById('lastSentUrl');
const openSidepanelBtn = document.getElementById('openSidepanelBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadSettings();
    setupEventListeners();
    setupMessageListener();
});

/**
 * Load settings and last sent log from storage
 */
async function loadSettings() {
    try {
        const result = await chrome.storage.sync.get([
            'pageSyncEnabled',
            'cursorTextBoxEnabled',
            'lastSentTime',
            'lastSentUrl'
        ]);
        
        // Set page sync checkbox state
        const isEnabled = result.pageSyncEnabled === true;
        enableSyncCheckbox.checked = isEnabled;
        toggleSwitch.classList.toggle('active', isEnabled);
        toggleSwitch.setAttribute('aria-checked', isEnabled);
        
        // Set cursor textbox checkbox state (default to true if not set)
        const isCursorTextBoxEnabled = result.cursorTextBoxEnabled !== false;
        enableCursorTextBoxCheckbox.checked = isCursorTextBoxEnabled;
        cursorTextBoxToggle.classList.toggle('active', isCursorTextBoxEnabled);
        cursorTextBoxToggle.setAttribute('aria-checked', isCursorTextBoxEnabled);
        
        // Update last sent log
        updateLastSentDisplay(result.lastSentTime, result.lastSentUrl);
        
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Page sync toggle switch click
    toggleSwitch.addEventListener('click', handleToggleClick);
    toggleSwitch.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleToggleClick();
        }
    });
    
    // Page sync checkbox change (sync with toggle)
    enableSyncCheckbox.addEventListener('change', handleToggleChange);
    
    // Cursor textbox toggle switch click
    cursorTextBoxToggle.addEventListener('click', handleCursorTextBoxToggleClick);
    cursorTextBoxToggle.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleCursorTextBoxToggleClick();
        }
    });
    
    // Cursor textbox checkbox change (sync with toggle)
    enableCursorTextBoxCheckbox.addEventListener('change', handleCursorTextBoxToggleChange);
    
    // Open sidepanel button
    openSidepanelBtn.addEventListener('click', async () => {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            if (tab) {
                await chrome.sidePanel.open({ tabId: tab.id });
                window.close();
            }
        } catch (error) {
            console.error('Error opening sidepanel:', error);
        }
    });
}

/**
 * Handle toggle switch click
 */
function handleToggleClick() {
    enableSyncCheckbox.checked = !enableSyncCheckbox.checked;
    handleToggleChange();
}

/**
 * Handle toggle state change
 */
async function handleToggleChange() {
    const isEnabled = enableSyncCheckbox.checked;
    
    // Update visual state
    toggleSwitch.classList.toggle('active', isEnabled);
    toggleSwitch.setAttribute('aria-checked', isEnabled);
    
    // Save to storage
    try {
        await chrome.storage.sync.set({ pageSyncEnabled: isEnabled });
    } catch (error) {
        console.error('Error saving page sync setting:', error);
    }
}

/**
 * Handle cursor textbox toggle switch click
 */
function handleCursorTextBoxToggleClick() {
    enableCursorTextBoxCheckbox.checked = !enableCursorTextBoxCheckbox.checked;
    handleCursorTextBoxToggleChange();
}

/**
 * Handle cursor textbox toggle state change
 */
async function handleCursorTextBoxToggleChange() {
    const isEnabled = enableCursorTextBoxCheckbox.checked;
    
    // Update visual state
    cursorTextBoxToggle.classList.toggle('active', isEnabled);
    cursorTextBoxToggle.setAttribute('aria-checked', isEnabled);
    
    // Save to storage
    try {
        await chrome.storage.sync.set({ cursorTextBoxEnabled: isEnabled });
        
        // Notify all tabs to update cursor textbox visibility
        const tabs = await chrome.tabs.query({});
        tabs.forEach(tab => {
            chrome.tabs.sendMessage(tab.id, {
                type: 'toggleCursorTextBox',
                enabled: isEnabled
            }).catch(() => {
                // Tab might not have content script loaded, ignore error
            });
        });
    } catch (error) {
        console.error('Error saving cursor textbox setting:', error);
    }
}

/**
 * Update last sent display
 * @param {string} time - Timestamp string
 * @param {string} url - URL string
 */
function updateLastSentDisplay(time, url) {
    if (time) {
        lastSentTime.textContent = time;
    } else {
        lastSentTime.textContent = 'Never';
    }
    
    if (url) {
        lastSentUrl.textContent = url;
    } else {
        lastSentUrl.textContent = '';
    }
}

/**
 * Setup message listener for updates from background script
 */
function setupMessageListener() {
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.type === 'updateLastSent') {
            updateLastSentDisplay(message.timestamp, message.url);
            
            // Also save to storage
            chrome.storage.sync.set({
                lastSentTime: message.timestamp,
                lastSentUrl: message.url
            }).catch(error => {
                console.error('Error saving last sent log:', error);
            });
        }
    });
}

