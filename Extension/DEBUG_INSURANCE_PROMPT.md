# Debugging Insurance Prompt Flow

## Current Flow Architecture

```
1. User browses page
   ↓
2. Background.js extracts page HTML
   ↓
3. Background.js sends to Decision Agent (/analyze)
   ↓
4. Decision Agent analyzes with LLM
   ↓
5. If travel-related & insurance needed:
   ↓
6. Decision Agent forwards to Master Agent (/chat)
   ↓
7. Master Agent processes and returns response
   ↓
8. Decision Agent captures master_agent_response
   ↓
9. Background.js receives response
   ↓
10. Background.js sends chrome.runtime.sendMessage to sidepanel
   ↓
11. index.html bridge script receives message
   ↓
12. index.html dispatches CustomEvent('insurancePromptFromAgent')
   ↓
13. React app should listen for event and display message
   ❌ THIS IS WHERE IT'S LIKELY FAILING
```

## Debugging Steps

### Step 1: Check if Decision Agent is analyzing pages

Open Chrome DevTools → Console, navigate to a travel-related page, and look for:
```
Decision Agent analysis: {should_prompt: true, confidence: ..., is_travel_related: true}
```

### Step 2: Check if Master Agent is being called

Look for in console:
```
✅ Successfully sent insurance prompt to sidepanel
```

OR

```
⚠️ Not sending to sidepanel - missing conditions
```

### Step 3: Check if sidepanel receives the message

Open sidepanel (click extension icon), then open DevTools for sidepanel (right-click → Inspect), and look for:
```
📡 Sidepanel message listener initialized
📨 Sidepanel received message: insurancePromptFromAgent
✅ Dispatching insurancePromptFromAgent event
```

### Step 4: Check if React app listens for event

In sidepanel DevTools console, manually trigger the event:
```javascript
window.dispatchEvent(new CustomEvent('insurancePromptFromAgent', {
  detail: {
    message: 'Test message from master agent',
    url: 'https://example.com',
    title: 'Test Page',
    travel_context: 'flight booking',
    timestamp: new Date().toISOString(),
    source: 'master_agent'
  }
}));
```

If the message appears in chat, the React app IS listening.
If not, the React app needs to be updated.

## Potential Issues

### Issue 1: Decision Agent not detecting travel pages
**Symptom**: `should_prompt: false` in console logs
**Fix**: Check Decision Agent LLM prompts or adjust confidence threshold

### Issue 2: Master Agent not responding
**Symptom**: `master_agent_response` is empty or null
**Check**: Decision Agent server logs for "Master agent response is empty!"
**Fix**: Verify Master Agent is running and responding correctly

### Issue 3: Background.js not sending to sidepanel
**Symptom**: No "Successfully sent insurance prompt" message
**Check**: Conditions: `forwarded_to_master && should_prompt && master_agent_response`
**Fix**: Check that all three are true

### Issue 4: Sidepanel not receiving message
**Symptom**: No "Sidepanel received message" log
**Fix**: Ensure sidepanel is open when message is sent, or implement message queuing

### Issue 5: React app not listening for event ⚠️ MOST LIKELY
**Symptom**: Custom event dispatched but no message in chat
**Fix**: React app source code needs to add event listener (see below)

## Required React App Code Update

The React app needs to listen for the custom event. Add this to your React component (likely in App.tsx or main chat component):

```typescript
useEffect(() => {
  const handleInsurancePrompt = (event: CustomEvent) => {
    const { message } = event.detail;
    
    // Add message to chat as assistant message
    const assistantMessage = {
      id: Date.now().toString(),
      text: message, // Master agent's response
      sender: 'assistant',
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, assistantMessage]);
    
    // Switch to chat view if needed
    setCurrentStage('chat');
    setIsChatActive(true);
    
    console.log('✅ Added insurance prompt to chat:', message);
  };

  window.addEventListener('insurancePromptFromAgent', handleInsurancePrompt as EventListener);
  
  return () => {
    window.removeEventListener('insurancePromptFromAgent', handleInsurancePrompt as EventListener);
  };
}, [setMessages, setCurrentStage, setIsChatActive]);
```

## Quick Test

To test the entire flow manually:

1. Open sidepanel
2. Open sidepanel DevTools (right-click → Inspect)
3. In Console, run:
```javascript
// Simulate the entire flow
const testMessage = {
  type: 'insurancePromptFromAgent',
  message: 'Based on your flight booking to Tokyo, I recommend considering travel insurance for international trips. Would you like to learn more about suitable plans?',
  url: 'https://example.com/flight',
  title: 'Flight Booking',
  travel_context: 'international flight',
  timestamp: new Date().toISOString(),
  source: 'master_agent'
};

// This should trigger the custom event
chrome.runtime.sendMessage(testMessage);
```

If this doesn't work, the React app definitely needs the event listener code.











