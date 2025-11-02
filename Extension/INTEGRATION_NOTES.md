# Master Agent Response Integration Notes

## Overview
The Decision Agent forwards insurance prompts to the Master Agent, and the Master Agent's response needs to be displayed in the chat interface.

## Current Implementation

1. **Decision Agent** (`Server/decision_agent/server.py`):
   - Captures master agent response when forwarding insurance prompts
   - Returns `master_agent_response` field in API response

2. **Background Script** (`Extension/background.js`):
   - Receives master agent response from Decision Agent
   - Sends message to sidepanel: `type: 'insurancePromptFromAgent'`
   - Includes `message: data.master_agent_response` (the master agent's response text)

3. **Sidepanel HTML** (`Extension/index.html`):
   - Added bridge script that listens for `insurancePromptFromAgent` messages
   - Dispatches custom event `insurancePromptFromAgent` with message details
   - The React app should listen for this event to add the message to chat

## To Complete Integration

### Option 1: Update Source Code and Rebuild (Recommended)

If the sidepanel is built from `New Design` folder:

1. Update `New Design/src/App.tsx` to listen for the custom event:
   ```typescript
   useEffect(() => {
     const handleInsurancePrompt = (event: CustomEvent) => {
       const { message } = event.detail;
       // Add message to chat as assistant message
       const assistantMessage: Message = {
         id: Date.now().toString(),
         text: message,
         sender: 'assistant',
         timestamp: new Date(),
       };
       setMessages(prev => [...prev, assistantMessage]);
       setCurrentStage('chat');
       setIsChatActive(true);
     };

     window.addEventListener('insurancePromptFromAgent', handleInsurancePrompt as EventListener);
     return () => {
       window.removeEventListener('insurancePromptFromAgent', handleInsurancePrompt as EventListener);
     };
   }, []);
   ```

2. Rebuild the sidepanel:
   ```bash
   cd New Design
   npm run build
   ```

3. Copy built files to Extension folder

### Option 2: Direct Chrome Runtime Message Listener (If React App Supports It)

If the React app in `sidepanel.js` has access to `chrome.runtime.onMessage`, you can modify it directly to listen for `insurancePromptFromAgent` messages.

## Testing

1. Ensure both servers are running:
   - Master Agent: `http://localhost:9000`
   - Decision Agent: `http://localhost:8004`

2. Navigate to a travel-related page (flight booking, hotel, etc.)

3. The Decision Agent should:
   - Analyze the page
   - Forward to Master Agent
   - Master Agent responds
   - Response should appear in chat interface

## Message Flow

```
User browses page
  ↓
Decision Agent analyzes
  ↓
Decision Agent forwards to Master Agent
  ↓
Master Agent generates response
  ↓
Decision Agent captures response
  ↓
Background.js sends to sidepanel
  ↓
Sidepanel displays in chat (via custom event or direct listener)
```

