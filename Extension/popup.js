document.addEventListener('DOMContentLoaded', () => {
  const enterChatBtn = document.getElementById('enterChatBtn');
  
  enterChatBtn.addEventListener('click', async () => {
    try {
      // Open side panel
      await chrome.sidePanel.open({ windowId: (await chrome.windows.getCurrent()).id });
      
      // Close popup
      window.close();
    } catch (error) {
      console.error('Error opening side panel:', error);
    }
  });
});



