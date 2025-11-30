/**
 * Test Script for Insurance Prompts
 * Run this in the sidepanel console to test if the infrastructure works
 */

(function() {
  console.log('🧪 Insurance Prompt Test Script');
  console.log('================================');
  
  // Check if listener infrastructure is loaded
  if (!window.addChatMessageListener) {
    console.error('❌ chat-response-listener.js not loaded!');
    return;
  }
  
  console.log('✅ Infrastructure detected');
  
  // Test 1: Register a listener and see if it receives messages
  console.log('\n📝 Test 1: Registering test listener...');
  window.addChatMessageListener((message) => {
    console.log('✅ TEST: Message received!', message);
    alert('Insurance Prompt Test:\n\n' + message.text.substring(0, 200));
  });
  
  // Test 2: Check queued messages
  if (window.chatMessageQueue && window.chatMessageQueue.length > 0) {
    console.log(`\n📬 Test 2: Found ${window.chatMessageQueue.length} queued messages`);
    window.chatMessageQueue.forEach((msg, idx) => {
      console.log(`  Message ${idx + 1}:`, msg.text.substring(0, 100));
    });
  } else {
    console.log('\n📬 Test 2: No queued messages');
  }
  
  // Test 3: Try to find React app
  console.log('\n🔍 Test 3: Looking for React app...');
  const root = document.getElementById('root');
  if (root) {
    const reactKeys = Object.keys(root).filter(k => k.startsWith('__react'));
    if (reactKeys.length > 0) {
      console.log('✅ Found React instance:', reactKeys[0]);
    } else {
      console.log('⚠️ React instance not found in root element');
    }
  }
  
  // Test 4: Simulate receiving a message
  console.log('\n📨 Test 4: Simulating message reception...');
  const testMessage = {
    id: 'test-' + Date.now(),
    text: 'This is a test insurance prompt message. If you see this, the infrastructure works!',
    sender: 'assistant',
    timestamp: new Date()
  };
  
  if (window.chatMessageListeners && window.chatMessageListeners.length > 0) {
    console.log(`✅ Sending test message to ${window.chatMessageListeners.length} listener(s)`);
    window.chatMessageListeners.forEach(listener => {
      try {
        listener(testMessage);
      } catch (e) {
        console.error('❌ Error in listener:', e);
      }
    });
  } else {
    console.log('⚠️ No listeners registered - queueing test message');
    if (!window.chatMessageQueue) window.chatMessageQueue = [];
    window.chatMessageQueue.push(testMessage);
  }
  
  console.log('\n✅ Test complete!');
  console.log('📝 Next step: Add the listener to your React app source code');
  console.log('   See: Extension/REACT_SOURCE_CODE_PATCH.md');
})();








