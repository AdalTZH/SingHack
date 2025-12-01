import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { WaveGradientBackground } from './components/WaveGradientBackground';
import { GlassFAB } from './components/GlassFAB';
import { StartPage } from './components/StartPage';
import { LandingPage } from './components/LandingPage';
import { DecisionMaking } from './components/DecisionMaking';
import { Payment } from './components/Payment';
import { DocumentUpload } from './components/DocumentUpload';
import { TravelBooking } from './components/TravelBooking';
import { InsightBubble } from './components/InsightBubble';

// ============================================================================
// TYPES
// ============================================================================
type Stage = 'start' | 'landing' | 'decision' | 'payment' | 'chat' | 'upload' | 'travel';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

// ============================================================================
// MAIN APP COMPONENT
// Chrome Extension Sidebar - Fully Scalable & Resizable
// ============================================================================
export default function App() {
  // ========================================
  // STATE
  // ========================================
  const [currentStage, setCurrentStage] = useState<Stage>('travel');
  const [selectedPlan, setSelectedPlan] = useState<number>(0);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isChatActive, setIsChatActive] = useState(false);
  const [showInsuranceComparison, setShowInsuranceComparison] = useState(false);
  const [isInsightVisible, setInsightVisible] = useState(true);
  const INSIGHT_TEXT = "Flying to China isn't risk-free: there have already been 13,929 claims there, with insurers paying out over €3.2 million in total and an average of about 6231 per incident. On some days, payouts spike into the tens of thousands (for example, over €92,000 on a single day in April 2024 and nearly €128,000 on a day in July 2825), usually driven by serious delay s, cancellations, or medical emergencies. Those are the kinds of unexpected hits that can turn a great trip into a financial mess if you're paying out of pocket. A simple travel in surance policy shifts those risks-and those bills-off your shoulders before you ever board the plane.";
  
  // ========================================
  // REFS
  // ========================================
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const shouldAutoScrollRef = useRef(true);

  // ========================================
  // SCROLL HANDLERS
  // ========================================
  const scrollToBottom = useCallback((force = false) => {
    if ((shouldAutoScrollRef.current || force) && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ 
        behavior: 'smooth',
        block: 'end'
      });
    }
  }, []);

  const handleScroll = useCallback(() => {
    if (!scrollContainerRef.current) return;
    
    const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 50;
    shouldAutoScrollRef.current = isNearBottom;
  }, []);

  // ========================================
  // EFFECTS
  // ========================================
  // Track scroll position for auto-scroll behavior
  useEffect(() => {
    const scrollContainer = scrollContainerRef.current;
    if (scrollContainer) {
      scrollContainer.addEventListener('scroll', handleScroll);
      return () => scrollContainer.removeEventListener('scroll', handleScroll);
    }
  }, [handleScroll]);

  // Auto-scroll when new messages arrive
  useEffect(() => {
    if (messages.length > 0 && currentStage === 'chat') {
      const timeoutId = setTimeout(() => scrollToBottom(), 100);
      return () => clearTimeout(timeoutId);
    }
  }, [messages, scrollToBottom, currentStage]);

  // Reset insurance comparison flag when stage changes
  useEffect(() => {
    if (currentStage !== 'travel') {
      setShowInsuranceComparison(false);
    }
  }, [currentStage]);
  
  // ========================================
  // MESSAGE HANDLERS
  // ========================================
  const handleSend = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: text,
      sender: 'user',
      timestamp: new Date(),
    };

    shouldAutoScrollRef.current = true;
    setMessages(prev => [...prev, userMessage]);
    setTimeout(() => scrollToBottom(true), 50);
    
    // Check if message contains "insurance" keyword
    if (text.toLowerCase().includes('insurance')) {
      setIsLoading(true);
      // Show AI response first
      setTimeout(() => {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: "I'll help you with insurance options! Opening the insurance comparison tool...",
          sender: 'assistant',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, assistantMessage]);
        setIsLoading(false);
        setTimeout(() => scrollToBottom(), 50);
        
        // Trigger travel/insurance modal
        setTimeout(() => {
          setCurrentStage('travel');
          setShowInsuranceComparison(true);
        }, 500);
      }, 1000);
      return;
    }
    
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: getAIResponse(text),
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsLoading(false);
      setTimeout(() => scrollToBottom(), 50);
    }, 1000 + Math.random() * 1000);
  };

  const getAIResponse = (input: string): string => {
    const responses = [
      "That's an interesting question! Let me help you with that.",
      "I understand what you're asking. Here's what I think...",
      "Great question! Based on what you've shared, I'd suggest...",
      "I'm here to help! Let me provide you with some insights.",
      "Thanks for reaching out! Here's my take on this...",
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  };

  // ========================================
  // STAGE NAVIGATION HANDLERS
  // ========================================
  const handleStartComplete = () => setCurrentStage('landing');
  const handleLandingDoubleTap = () => setCurrentStage('decision');
  const handleDecisionSelect = (planIndex: number) => {
    setSelectedPlan(planIndex);
    setCurrentStage('payment');
  };
  const handlePaymentComplete = () => setCurrentStage('landing');
  const handlePaymentBack = () => setCurrentStage('decision');
  const handleUploadComplete = () => setCurrentStage('decision');
  const handleUploadBack = () => setCurrentStage('landing');
  const handleTravelComplete = () => setCurrentStage('decision');
  const handleTravelBack = () => setCurrentStage('landing');

  // ========================================
  // FAB ACTION HANDLERS
  // ========================================
  const handleVoiceCommand = () => {
    console.log('Voice command activated');
  };

  const handleDragDrop = () => {
    console.log('Drag and drop activated');
    setCurrentStage('upload');
  };

  // ========================================
  // RENDER
  // ========================================
  return (
    <div className="w-full h-full flex bg-gray-100">
      {/* Main Scrollable Container - Scales with sidebar resize */}
      <div 
        ref={scrollContainerRef} 
        className="w-full h-full flex flex-col shadow-[0_8px_32px_0_rgba(31,38,135,0.37)] overflow-y-auto relative"
      >
        <div className="min-h-full flex flex-col relative">
          <AnimatePresence>
            {currentStage === 'chat' && isInsightVisible && (
              <InsightBubble
                text={INSIGHT_TEXT}
                onSelect={() => setCurrentStage('decision')}
                onExploreMore={() => {
                  setCurrentStage('travel');
                  setShowInsuranceComparison(true);
                }}
                onClose={() => setInsightVisible(false)}
              />
            )}
          </AnimatePresence>
          {/* Wave Background - Automatically extends to fill container */}
          <WaveGradientBackground />

          {/* Stage-based Content */}
          <AnimatePresence mode="sync">
            {currentStage === 'start' && (
              <StartPage key="start" onComplete={handleStartComplete} />
            )}

            {(currentStage === 'landing' || currentStage === 'payment') && (
              <LandingPage key="landing" onDoubleTap={handleLandingDoubleTap} />
            )}

            {currentStage === 'decision' && (
              <DecisionMaking key="decision" onSelect={handleDecisionSelect} />
            )}

            {currentStage === 'chat' && (
              <motion.div
                key="chat"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="min-h-screen flex flex-col relative z-10 pb-40"
              >
                <div className="flex-1 px-6 pt-6 relative z-10">
                  {messages.length > 0 ? (
                    <div className="space-y-4">
                      {messages.map((message, index) => (
                        <motion.div
                          key={message.id}
                          initial={{ opacity: 0, y: 10, scale: 0.95 }}
                          animate={{ opacity: 1, y: 0, scale: 1 }}
                          transition={{ 
                            delay: index * 0.05,
                            type: "spring",
                            stiffness: 400,
                            damping: 30
                          }}
                          className={`flex ${
                            message.sender === 'user' ? 'justify-end' : 'justify-start'
                          }`}
                        >
                          <div
                            className={`max-w-[85%] px-4 py-3 rounded-[18px] break-words backdrop-blur-lg border shadow-[0_4px_16px_0_rgba(31,38,135,0.2)] ${
                              message.sender === 'user'
                                ? 'bg-white/25 text-white border-white/30 rounded-br-[4px]'
                                : 'bg-white/15 text-white border-white/20 rounded-bl-[4px]'
                            }`}
                          >
                            {message.text}
                          </div>
                        </motion.div>
                      ))}
                      {isLoading && (
                        <motion.div
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="flex"
                        >
                          <div className="max-w-[85%] px-4 py-3 rounded-[18px] backdrop-blur-lg bg-white/15 text-white border border-white/20 rounded-bl-[4px] shadow-[0_4px_16px_0_rgba(31,38,135,0.2)]">
                            <div className="inline-flex gap-1 items-center">
                              <div className="w-2 h-2 rounded-full bg-white/80 animate-[bounce_1.4s_infinite_ease-in-out_both] [animation-delay:-0.32s]" />
                              <div className="w-2 h-2 rounded-full bg-white/80 animate-[bounce_1.4s_infinite_ease-in-out_both] [animation-delay:-0.16s]" />
                              <div className="w-2 h-2 rounded-full bg-white/80 animate-[bounce_1.4s_infinite_ease-in-out_both]" />
                            </div>
                          </div>
                        </motion.div>
                      )}
                      <div ref={messagesEndRef} />
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-64">
                      <motion.div
                        className="text-white/40 text-sm text-center"
                        animate={{ opacity: [0.3, 0.6, 0.3] }}
                        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                      >
                        Start a conversation...
                      </motion.div>
                    </div>
                  )}
                </div>
              </motion.div>
            )}

            {currentStage === 'upload' && (
              <DocumentUpload key="upload" onComplete={handleUploadComplete} onBack={handleUploadBack} />
            )}

            {currentStage === 'travel' && (
              <TravelBooking key="travel" openInsuranceComparison={showInsuranceComparison} />
            )}
          </AnimatePresence>
        </div>

        {/* FAB Button - Always centered horizontally in container */}
        {(currentStage === 'landing' || currentStage === 'decision' || currentStage === 'payment' || currentStage === 'chat' || currentStage === 'travel') && (
          <div className="fixed bottom-8 left-0 right-0 flex justify-center z-40 pointer-events-none">
            <div className="pointer-events-auto w-full max-w-sm px-6">
              <GlassFAB
                onVoiceCommand={handleVoiceCommand}
                onTextMessage={() => {
                  setCurrentStage('chat');
                  setIsChatActive(true);
                  setInsightVisible(true);
                }}
                onDragDrop={handleDragDrop}
                onSend={handleSend}
                isChatActive={isChatActive}
                onExpandedChange={(expanded) => {
                  if (!expanded) {
                    setIsChatActive(false);
                    if (currentStage === 'chat') {
                      setCurrentStage('landing');
                    }
                  }
                }}
              />
            </div>
          </div>
        )}

        {/* Payment Overlay */}
        <AnimatePresence>
          {currentStage === 'payment' && (
            <Payment 
              key="payment" 
              selectedPlan={selectedPlan}
              onComplete={handlePaymentComplete}
              onBack={handlePaymentBack}
            />
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
