
  import { createRoot } from "react-dom/client";
  import App from "./App.tsx";
  import "./index.css";

  // Error handling
  window.addEventListener('error', (event) => {
    console.error('Global error in React app:', event.error);
    const root = document.getElementById("root");
    if (root) {
      root.innerHTML = `
        <div style="padding: 20px; color: red; font-family: monospace; white-space: pre-wrap;">
          <h2>Error loading React app</h2>
          <p><strong>Error:</strong> ${event.error?.message || 'Unknown error'}</p>
          <p><strong>Stack:</strong> ${event.error?.stack || 'No stack trace'}</p>
          <p>Check console for more details.</p>
        </div>
      `;
    }
  });

  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
  });

  // Check if root element exists
  const rootElement = document.getElementById("root");
  if (!rootElement) {
    console.error('Root element not found!');
    document.body.innerHTML = '<div style="padding: 20px; color: red;">Error: Root element not found</div>';
  } else {
    try {
      console.log('Initializing React app...');
      const root = createRoot(rootElement);
      root.render(<App />);
      console.log('React app initialized successfully');
    } catch (error) {
      console.error('Error initializing React app:', error);
      rootElement.innerHTML = `
        <div style="padding: 20px; color: red; font-family: monospace; white-space: pre-wrap;">
          <h2>Error initializing React app</h2>
          <p><strong>Error:</strong> ${error instanceof Error ? error.message : String(error)}</p>
          <p><strong>Stack:</strong> ${error instanceof Error ? error.stack : 'No stack trace'}</p>
        </div>
      `;
    }
  }
  