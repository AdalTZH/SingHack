/**
 * Inject Chat Message Directly
 * This script tries to inject messages directly into the React app's chat
 * by finding and manipulating the React component's state
 */

(function() {
  'use strict';

  console.log('🔧 Chat Message Injector initializing...');

  /**
   * Try to inject message directly into React app
   */
  function injectMessageDirectly(messageText) {
    console.log('📨 Attempting to inject message directly:', messageText.substring(0, 100));

    // Strategy 1: Find React Fiber and try to update state
    const rootElement = document.getElementById('root');
    if (!rootElement) {
      console.warn('⚠️ Root element not found');
      return false;
    }

    // Find React instance keys
    const reactKeys = Object.keys(rootElement).filter(key => 
      key.startsWith('__reactFiber') || key.startsWith('__reactInternalInstance')
    );

    if (reactKeys.length > 0) {
      console.log('✅ Found React instance:', reactKeys[0]);
      const reactInstance = rootElement[reactKeys[0]];

      // Try to traverse React tree to find message state
      let current = reactInstance;
      let depth = 0;
      const maxDepth = 50;

      while (current && depth < maxDepth) {
        // Check if this node has state/memoizedState with messages
        if (current.memoizedState) {
          let stateNode = current.memoizedState;
          while (stateNode) {
            if (stateNode.memoizedState && Array.isArray(stateNode.memoizedState)) {
              // Might be messages array
              console.log('🔍 Found potential messages array');
              try {
                stateNode.memoizedState.push({
                  id: Date.now().toString(),
                  text: messageText,
                  sender: 'assistant',
                  timestamp: new Date()
                });
                console.log('✅ Injected message into React state');
                return true;
              } catch (e) {
                console.warn('⚠️ Could not inject into state:', e);
              }
            }
            stateNode = stateNode.next;
          }
        }

        // Check stateNode property
        if (current.stateNode && current.stateNode.setState) {
          console.log('✅ Found component with setState');
          try {
            // Try to find messages in state
            const state = current.stateNode.state || {};
            if (state.messages && Array.isArray(state.messages)) {
              current.stateNode.setState({
                messages: [...state.messages, {
                  id: Date.now().toString(),
                  text: messageText,
                  sender: 'assistant',
                  timestamp: new Date()
                }]
              });
              console.log('✅ Injected message via setState');
              return true;
            }
          } catch (e) {
            console.warn('⚠️ Could not use setState:', e);
          }
        }

        current = current.child || current.return || current.sibling;
        depth++;
      }
    }

    // Strategy 2: Look for global message handlers
    if (window.setChatMessages || window.addChatMessage) {
      console.log('✅ Found global message handler');
      try {
        if (window.addChatMessage) {
          window.addChatMessage({
            id: Date.now().toString(),
            text: messageText,
            sender: 'assistant',
            timestamp: new Date()
          });
          return true;
        }
      } catch (e) {
        console.warn('⚠️ Error calling global handler:', e);
      }
    }

    // Strategy 3: Create synthetic chat interaction
    // Simulate that the user asked about insurance and we're responding
    console.log('🔍 Attempting synthetic chat interaction...');
    const syntheticEvent = new CustomEvent('syntheticChatResponse', {
      detail: {
        message: messageText,
        sender: 'assistant',
        timestamp: new Date()
      },
      bubbles: true
    });
    document.dispatchEvent(syntheticEvent);
    rootElement.dispatchEvent(syntheticEvent);

    return false;
  }

  /**
   * Process queued messages and try to inject them
   */
  function processQueuedMessages() {
    if (window.chatMessageQueue && window.chatMessageQueue.length > 0) {
      console.log(`📬 Processing ${window.chatMessageQueue.length} queued messages`);
      const messages = [...window.chatMessageQueue];
      window.chatMessageQueue = [];

      messages.forEach(msg => {
        if (msg.text) {
          injectMessageDirectly(msg.text);
        }
      });
    }
  }

  // Listen for messages from chat-response-listener
  window.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'injectChatMessage') {
      injectMessageDirectly(event.data.message);
    }
  });

  // Poll for queued messages
  setInterval(processQueuedMessages, 1000);

  // Try to inject when messages are queued
  if (window.chatMessageQueue) {
    const originalPush = window.chatMessageQueue.push;
    window.chatMessageQueue.push = function(...args) {
      const result = originalPush.apply(this, args);
      console.log('📬 Message queued, attempting injection...');
      setTimeout(() => {
        if (args[0] && args[0].text) {
          injectMessageDirectly(args[0].text);
        }
      }, 100);
      return result;
    };
  }

  // Strategy 4: Try to find message display elements and inject directly
  function injectIntoDOM(messageText) {
    // Look for common chat message container patterns
    const possibleContainers = [
      '[class*="message"]',
      '[class*="chat"]',
      '[data-testid*="message"]',
      '[id*="message"]',
      '[id*="chat"]'
    ];

    for (const selector of possibleContainers) {
      const containers = document.querySelectorAll(selector);
      if (containers.length > 0) {
        console.log(`🔍 Found ${containers.length} potential message containers`);
        // Don't inject directly - let React handle it properly
      }
    }

    // Instead, trigger a custom event that might be caught
    const injectionEvent = new CustomEvent('insurancePromptReceived', {
      detail: {
        message: messageText,
        id: Date.now().toString(),
        sender: 'assistant',
        timestamp: new Date()
      },
      bubbles: true
    });
    document.dispatchEvent(injectionEvent);
    window.dispatchEvent(injectionEvent);
  }

  // Enhanced queue processor with DOM injection fallback
  const enhancedProcessQueue = () => {
    if (window.chatMessageQueue && window.chatMessageQueue.length > 0) {
      console.log(`📬 Enhanced processing: ${window.chatMessageQueue.length} queued messages`);
      const messages = [...window.chatMessageQueue];
      
      messages.forEach(msg => {
        // Try all injection strategies
        if (!injectMessageDirectly(msg.text)) {
          // Fallback to DOM injection
          console.log('📨 Trying DOM injection as fallback...');
          injectIntoDOM(msg.text);
        }
      });
    }
  };

  // Poll more aggressively
  setInterval(enhancedProcessQueue, 500);

  console.log('✅ Chat Message Injector loaded');
})();

