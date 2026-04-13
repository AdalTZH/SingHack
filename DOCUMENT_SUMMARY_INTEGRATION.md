# Document Summary Integration with Master Agent

## Overview

PDF summaries are now automatically integrated into the Master Agent's LangGraph state, allowing the agent to reference uploaded documents when answering user queries.

## Architecture Changes

### 1. **Extended AgentState** (`Server/master_agent/master_agent.py`)
- Added `document_summaries` field to the LangGraph state
- State now persists document context across the conversation

### 2. **Enhanced System Prompt** (`Server/master_agent/master_agent.py`)
- Added `_build_system_prompt()` method that dynamically includes document context
- When document summaries are available, the system prompt includes:
  - Document file names and page counts
  - AI-generated summaries
  - Text previews (first 500 characters)
  - Instructions on how to use document information

### 3. **Updated Chat Endpoint** (`Server/master_agent/server.py`)
- Added `document_summaries` parameter to `ChatMessage` model
- Server now accepts and forwards document summaries to the agent

### 4. **Frontend Integration** (`Extension/src/App.tsx`)
- Added `documentSummaries` state to store uploaded document summaries
- `handleUploadComplete` now receives and stores document summaries
- `handleSend` passes document summaries with each chat request

### 5. **Background Script** (`Extension/background.js`)
- Updated to pass `document_summaries` to Master Agent API
- Includes logging for document summary flow

## How It Works

### Flow Diagram

```
1. User uploads PDF
   ↓
2. DocumentUpload component extracts text and generates summary
   ↓
3. Summary stored in App.tsx state (documentSummaries)
   ↓
4. User asks question in chat
   ↓
5. App.tsx sends message + document summaries to background script
   ↓
6. Background script forwards to Master Agent API
   ↓
7. Master Agent includes summaries in LangGraph state
   ↓
8. System prompt dynamically includes document context
   ↓
9. Agent references documents when answering queries
```

## Usage

### For Users

1. **Upload PDF**: Go to upload stage and upload your insurance documents
2. **Automatic Processing**: Text extraction and summarization happen automatically
3. **Ask Questions**: Chat with the agent - it will automatically reference your documents

### Example Queries

After uploading a policy document, users can ask:
- "What does my current policy cover?"
- "What are the exclusions in my document?"
- "Compare my policy with available products"
- "What benefits does my policy offer?"

The agent will reference the uploaded document summaries to answer these questions.

## Technical Details

### Document Summary Format

Each document summary includes:
```json
{
  "file_name": "policy.pdf",
  "summary": "AI-generated detailed summary...",
  "text": "Full extracted text from PDF...",
  "metadata": {
    "pages": 10,
    "method": "pdfplumber"
  }
}
```

### System Prompt Enhancement

When documents are available, the system prompt is enhanced with:

```
=== UPLOADED DOCUMENTS ===
The user has uploaded the following documents. Use this information to answer 
questions about their insurance documents, policy details, coverage, claims, 
or any information contained in these documents:

Document 1: policy.pdf (10 pages)
Summary: [AI-generated summary]
Text Preview: [First 500 characters]

When answering questions:
- Reference specific details from these documents when relevant
- Compare information in documents with available insurance products
- Help users understand what their current documents cover
- Suggest improvements or additional coverage if needed
```

### State Persistence

Document summaries are maintained in the LangGraph state throughout the conversation:
- Summaries persist across multiple messages
- Agent can reference them in follow-up questions
- No need to re-upload documents for related questions

## Benefits

1. **Contextual Responses**: Agent can reference actual document content
2. **Better Recommendations**: Can compare user's documents with available products
3. **Accurate Information**: Uses real document data, not assumptions
4. **Seamless Experience**: Automatic integration - no manual steps required

## Example Conversation

**User**: "I uploaded my travel insurance policy. What does it cover?"

**Agent** (with document context):
"Based on your uploaded policy document (policy.pdf), I can see it covers:

- Trip cancellation up to $5,000
- Medical emergencies up to $50,000
- Baggage loss up to $2,500
- Travel delays with $100 per 6-hour delay

Your policy also includes coverage for adventure activities and has a $500 deductible. Would you like me to compare this with other available travel insurance products, or help you understand any specific coverage details?"

## Configuration

No additional configuration needed! The integration works automatically:
- PDF extractor server must be running (port 8007)
- Master agent server must be running (port 9000)
- OpenAI API key must be configured (for summarization)

## Files Modified

### Backend
- `Server/master_agent/master_agent.py` - Added document summary support to LangGraph state
- `Server/master_agent/server.py` - Updated chat endpoint to accept document summaries

### Frontend
- `Extension/src/App.tsx` - Store and pass document summaries
- `Extension/src/components/DocumentUpload.tsx` - Pass summaries to parent component
- `Extension/background.js` - Forward document summaries to master agent

## Testing

1. Upload a PDF document
2. Wait for text extraction and summarization
3. Go to chat and ask about the document
4. Verify agent references the document content in responses

## Next Steps

Future enhancements could include:
- Document-specific tool calls (e.g., "extract coverage limits from document")
- Multi-document comparison
- Document highlighting based on queries
- Persistent document storage across sessions


