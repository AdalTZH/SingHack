# SingPass Insurance Chat Chrome Extension

A sleek, modern Chrome extension for chatting with an AI insurance agent and uploading PDF documents.

## Features

- **Popup Interface**: Clean white background with QR code and SingPass logo
- **Side Panel Chat**: Dark futuristic theme with modern chat interface
- **PDF Upload**: Drag & drop or browse files to upload PDF documents
- **AI Chat**: Integrated with Master Agent API for intelligent insurance assistance
- **Document Processing**: Automatic PDF extraction and summarization

## Setup Instructions

1. **Load the Extension in Chrome**:
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)
   - Click "Load unpacked"
   - Select the `Extension` folder

2. **Add Extension Icons** (Optional):
   - Create icon files (16x16, 48x48, 128x128 pixels) in PNG format
   - Place them in the `icons/` folder as:
     - `icon16.png`
     - `icon48.png`
     - `icon128.png`
   - If icons are not provided, Chrome will use default icons

3. **Start the Backend Servers**:
   - Ensure the Master Agent API is running on `http://localhost:9000`
   - Ensure the PDF Extractor API is running on `http://localhost:8007`

4. **Use the Extension**:
   - Click the extension icon in Chrome toolbar
   - Click "Enter Chat" button in the popup
   - The side panel will open with the chat interface
   - Start chatting or upload PDF documents

## API Endpoints

- **Master Agent API**: `http://localhost:9000/chat` (POST)
- **PDF Extractor API**: `http://localhost:8007/extract` (POST)

## File Structure

```
Extension/
├── manifest.json          # Extension manifest
├── popup.html            # Popup interface
├── popup.css             # Popup styles
├── popup.js              # Popup logic
├── sidepanel.html        # Side panel interface
├── sidepanel.css         # Side panel styles (dark futuristic theme)
├── sidepanel.js          # Side panel logic (chat & upload)
├── background.js         # Service worker
├── QR_code.svg           # QR code image
├── singpass_logo_fullcolour.png  # SingPass logo
├── icons/                # Extension icons (optional)
└── README.md             # This file
```

## Features Details

### Chat Interface
- Real-time messaging with the AI insurance agent
- Conversation history persistence
- Typing indicators
- Message formatting support (markdown-like)

### PDF Upload
- Drag & drop support
- File browser support
- Multiple file upload
- Real-time upload status
- Automatic text extraction and summarization
- Document context integration in chat

### Design
- Modern, sleek UI with futuristic dark theme
- Smooth animations and transitions
- Responsive layout
- Gradient accents
- Glassmorphism effects

## Troubleshooting

1. **Side panel doesn't open**: Make sure you're using Chrome 114+ (side panel API requirement)
2. **API errors**: Verify that both backend servers are running
3. **CORS errors**: Check that the backend servers have CORS configured for `chrome-extension://*`
4. **PDF upload fails**: Ensure the PDF file is valid and under 50MB

## Development

To modify the extension:
1. Make changes to the files
2. Go to `chrome://extensions/`
3. Click the refresh icon on the extension card
4. Test your changes

## Notes

- The extension requires Chrome 114+ for side panel support
- All API calls are made to localhost (development setup)
- Conversation history is stored locally in Chrome storage
- Uploaded documents are processed and their summaries are included in chat context



