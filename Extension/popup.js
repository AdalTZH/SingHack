// Popup JavaScript for Page Sync Settings

// DOM Elements
const enableSyncCheckbox = document.getElementById('enableSync');
const toggleSwitch = document.getElementById('toggleSwitch');
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
            'lastSentTime',
            'lastSentUrl'
        ]);
        
        // Set checkbox state
        const isEnabled = result.pageSyncEnabled === true;
        enableSyncCheckbox.checked = isEnabled;
        toggleSwitch.classList.toggle('active', isEnabled);
        toggleSwitch.setAttribute('aria-checked', isEnabled);
        
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
    // Toggle switch click
    toggleSwitch.addEventListener('click', handleToggleClick);
    toggleSwitch.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleToggleClick();
        }
    });
    
    // Checkbox change (sync with toggle)
    enableSyncCheckbox.addEventListener('change', handleToggleChange);
    
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

