import { useState, useRef, useEffect } from 'react';
import { MessageSquare, Upload, Mic, Send } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { ChefHat } from './ChefHat';

interface GlassFABProps {
  onVoiceCommand: () => void;
  onTextMessage: () => void;
  onDragDrop: () => void;
  onSend: (message: string) => void;
  isChatActive: boolean;
  onExpandedChange?: (isExpanded: boolean) => void;
}

export function GlassFAB({ onVoiceCommand, onTextMessage, onDragDrop, onSend, isChatActive, onExpandedChange }: GlassFABProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isMicActive, setIsMicActive] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [isBlinking, setIsBlinking] = useState(false);
  const [isTalking, setIsTalking] = useState(false);
  const [mouthOpenness, setMouthOpenness] = useState(0);
  const [lastMouseActivity, setLastMouseActivity] = useState(Date.now());
  const [isWandering, setIsWandering] = useState(false);
  const [wanderTarget, setWanderTarget] = useState({ x: 0, y: 0 });
  const [wanderExpression, setWanderExpression] = useState<'o' | 'neutral' | 'curious' | 'shake'>('neutral');
  const [headShakeOffset, setHeadShakeOffset] = useState({ x: 0, y: 0, rotation: 0 });
  const inputRef = useRef<HTMLInputElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Call onExpandedChange when isExpanded or isChatActive changes
  useEffect(() => {
    onExpandedChange?.(isExpanded || isChatActive);
  }, [isExpanded, isChatActive, onExpandedChange]);

  // Focus input when chat becomes active
  useEffect(() => {
    if (isChatActive && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isChatActive]);

  // Track mouse position for eye following
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY });
      setLastMouseActivity(Date.now());
      setIsWandering(false); // Exit wandering mode when mouse moves
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Check for mouse inactivity (1 minute = 60000ms)
  useEffect(() => {
    const inactivityCheck = setInterval(() => {
      const inactiveTime = Date.now() - lastMouseActivity;
      if (inactiveTime >= 60000 && !isWandering) {
        setIsWandering(true);
      }
    }, 1000); // Check every second

    return () => clearInterval(inactivityCheck);
  }, [lastMouseActivity, isWandering]);

  // Generate random wander target and expression every 10 seconds when wandering
  useEffect(() => {
    if (!isWandering) {
      setWanderExpression('neutral');
      setHeadShakeOffset(0);
      return;
    }

    // Generate initial random target when entering wander mode
    const generateRandomTarget = () => {
      const maxMovement = 15;
      return {
        x: (Math.random() - 0.5) * maxMovement * 2,
        y: (Math.random() - 0.5) * maxMovement * 2,
      };
    };

    const generateRandomExpression = (): 'o' | 'neutral' | 'curious' | 'shake' => {
      const expressions: ('o' | 'neutral' | 'curious' | 'shake')[] = ['o', 'neutral', 'curious', 'shake'];
      return expressions[Math.floor(Math.random() * expressions.length)];
    };

    setWanderTarget(generateRandomTarget());
    setWanderExpression(generateRandomExpression());

    const wanderInterval = setInterval(() => {
      setWanderTarget(generateRandomTarget());
      setWanderExpression(generateRandomExpression());
    }, 10000); // Update every 10 seconds

    return () => clearInterval(wanderInterval);
  }, [isWandering]);

  // Pendulum head shake animation when expression is 'shake'
  useEffect(() => {
    if (wanderExpression !== 'shake' || !isWandering) {
      setHeadShakeOffset({ x: 0, y: 0, rotation: 0 });
      return;
    }

    let frame = 0;
    const shakeAnimation = setInterval(() => {
      frame += 1;
      const angle = frame * 0.08; // Slower for more pendulum-like motion
      
      // Pendulum motion: swing angle (rotation) and arc path
      const swingAngle = Math.sin(angle) * 15; // Rotation in degrees
      const arcX = Math.sin(angle) * 10; // Horizontal movement
      const arcY = Math.abs(Math.cos(angle)) * 3 - 3; // Slight upward arc at extremes
      
      setHeadShakeOffset({ 
        x: arcX, 
        y: arcY, 
        rotation: swingAngle 
      });
    }, 40); // Update every 40ms for smooth pendulum motion

    return () => clearInterval(shakeAnimation);
  }, [wanderExpression, isWandering]);

  // Random blinking effect
  useEffect(() => {
    let blinkTimeout: NodeJS.Timeout;
    let unblinkTimeout: NodeJS.Timeout;
    let isCleanedUp = false;

    const scheduleNextBlink = () => {
      if (isCleanedUp) return;
      const randomDelay = 5000 + Math.random() * 5000; // 5-10 seconds
      blinkTimeout = setTimeout(() => {
        if (isCleanedUp) return;
        setIsBlinking(true);
        unblinkTimeout = setTimeout(() => {
          if (isCleanedUp) return;
          setIsBlinking(false);
          scheduleNextBlink();
        }, 150); // Blink duration
      }, randomDelay);
    };

    scheduleNextBlink();

    return () => {
      isCleanedUp = true;
      clearTimeout(blinkTimeout);
      clearTimeout(unblinkTimeout);
    };
  }, []);

  // Talking animation - mouth opens and closes
  useEffect(() => {
    if (!isTalking) {
      setMouthOpenness(0);
      return;
    }

    // Animate mouth opening and closing in a talking pattern
    const talkingInterval = setInterval(() => {
      setMouthOpenness((prev) => {
        // Random variation in mouth movement for natural talking
        const target = Math.random() * 0.7 + 0.3; // 0.3 to 1.0
        return target;
      });
    }, 150); // Change mouth shape every 150ms

    return () => clearInterval(talkingInterval);
  }, [isTalking]);

  // Auto-start talking when chat is active (simulating bot response)
  useEffect(() => {
    if (isChatActive) {
      // Start talking after a short delay
      const talkTimeout = setTimeout(() => {
        setIsTalking(true);
        // Stop talking after 2-4 seconds
        const stopTimeout = setTimeout(() => {
          setIsTalking(false);
        }, 2000 + Math.random() * 2000);
        return () => clearTimeout(stopTimeout);
      }, 500);
      return () => clearTimeout(talkTimeout);
    } else {
      setIsTalking(false);
    }
  }, [isChatActive]);

  // Calculate eye/mouth position offset based on cursor tracking or wandering
  const getCursorTrackingOffset = () => {
    // If wandering, return the random wander target
    if (isWandering) {
      return wanderTarget;
    }

    // Otherwise, follow the cursor
    if (!buttonRef.current) return { x: 0, y: 0 };
    
    const rect = buttonRef.current.getBoundingClientRect();
    const buttonCenterX = rect.left + rect.width / 2;
    const buttonCenterY = rect.top + rect.height / 2;
    
    // Calculate direction from button center to cursor
    const deltaX = mousePos.x - buttonCenterX;
    const deltaY = mousePos.y - buttonCenterY;
    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
    
    // Normalize and limit the movement (max 20px for more dramatic tracking)
    const maxMovement = 20;
    const normalizedX = distance > 0 ? (deltaX / distance) * Math.min(distance / 10, maxMovement) : 0;
    const normalizedY = distance > 0 ? (deltaY / distance) * Math.min(distance / 10, maxMovement) : 0;
    
    return { x: normalizedX, y: normalizedY };
  };

  const handleMainButtonClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!isExpanded && !isChatActive) {
      setIsExpanded(true);
    }
  };

  const handleBackdropClick = () => {
    setIsExpanded(false);
    setIsMicActive(false);
    setInputValue('');
    // Signal to parent to close everything including chat
    onExpandedChange?.(false);
  };

  const handleSend = () => {
    if (!inputValue.trim()) return;
    onSend(inputValue);
    setInputValue('');
    
    // Trigger talking animation when sending a message
    setIsTalking(true);
    setTimeout(() => {
      setIsTalking(false);
    }, 2000 + Math.random() * 1500);
    
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Backdrop - appears when expanded or chat active */}
      <AnimatePresence>
        {(isExpanded || isChatActive) && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={handleBackdropClick}
            className="fixed inset-0 z-30"
            style={{ cursor: 'default' }}
          />
        )}
      </AnimatePresence>

      <div className="relative flex items-center justify-center w-full z-40">
        {/* Chat Mode - Text Input Bar */}
        {isChatActive ? (
          <motion.div
            key="text-input"
            layoutId="morph-container"
            className="backdrop-blur-xl bg-white/15 border-2 border-white/30 shadow-[inset_0_4px_8px_rgba(255,255,255,0.15),0_8px_24px_rgba(0,0,0,0.3)] flex items-center pl-6 pr-3 gap-2"
            style={{
              width: '100%',
              height: '60px',
              borderRadius: '30px',
            }}
            transition={{ 
              type: "spring", 
              stiffness: 280, 
              damping: 28,
              mass: 0.8
            }}
          >
            <motion.input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              onClick={(e) => e.stopPropagation()}
              placeholder="Type your message..."
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ delay: 0.1, duration: 0.2 }}
              className="flex-1 bg-transparent border-none outline-none text-white placeholder:text-white/50"
            />
            <motion.button
              onClick={(e) => {
                e.stopPropagation();
                handleSend();
              }}
              disabled={!inputValue.trim()}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0 }}
              transition={{ delay: 0.15, type: "spring", stiffness: 400, damping: 25 }}
              whileTap={{ scale: 0.9 }}
              className="w-10 h-10 backdrop-blur-xl bg-white/20 border border-white/30 rounded-full flex items-center justify-center transition-all duration-300 hover:bg-white/25 disabled:opacity-40 disabled:cursor-not-allowed shadow-[inset_0_2px_4px_rgba(255,255,255,0.1)] flex-shrink-0"
            >
              <Send size={18} className="text-white" />
            </motion.button>
          </motion.div>
        ) : (
          <>
            {/* Normal Mode - FAB with Sub-buttons */}
            <div className="relative flex items-center justify-center h-[125px] w-full">
                {/* Left Sub-button - Text Message */}
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ scale: 0, x: 0, opacity: 0 }}
                      animate={{ 
                        scale: 1, 
                        x: -100, 
                        opacity: 1,
                      }}
                      exit={{ 
                        scale: 0, 
                        x: 0, 
                        opacity: 0,
                      }}
                      transition={{ 
                        type: "spring", 
                        stiffness: 200, 
                        damping: 15,
                        mass: 0.8
                      }}
                      className="absolute"
                    >
                      <motion.button
                        onClick={(e) => {
                          e.stopPropagation();
                          onTextMessage();
                          setIsExpanded(false);
                        }}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        className="relative w-16 h-16 backdrop-blur-xl bg-white/10 border border-white/20 rounded-full cursor-pointer flex items-center justify-center shadow-[inset_0_2px_4px_rgba(255,255,255,0.1),0_4px_12px_rgba(0,0,0,0.2)]"
                        aria-label="Text message"
                      >
                        <motion.div
                          className="absolute inset-0 rounded-full bg-white/5"
                          animate={{
                            scale: [1, 1.2, 1],
                            opacity: [0.5, 0, 0.5],
                          }}
                          transition={{
                            duration: 2,
                            repeat: Infinity,
                            ease: "easeInOut"
                          }}
                        />
                        <MessageSquare size={24} className="text-white relative z-10" />
                      </motion.button>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Main Button */}
                <div className="relative z-10">
                  <motion.div
                    className="absolute inset-0 rounded-full backdrop-blur-xl border pointer-events-none"
                    animate={{
                      scale: isExpanded ? [1, 1.15, 1] : [1, 1.05, 1],
                      opacity: [0.3, 0.6, 0.3],
                    }}
                    transition={{
                      duration: 3,
                      repeat: Infinity,
                      ease: "easeInOut"
                    }}
                    style={{
                      width: '125px',
                      height: '125px',
                      backgroundColor: 'rgba(255,255,255,0.05)',
                      borderColor: 'rgba(255,255,255,0.1)',
                    }}
                  />
                  
                  <motion.button
                    ref={buttonRef}
                    layoutId="morph-container"
                    onClick={handleMainButtonClick}
                    whileTap={{ scale: 0.92 }}
                    animate={{
                      scale: isExpanded ? [1, 1.05, 1] : 1,
                    }}
                    transition={{
                      layout: {
                        type: "spring", 
                        stiffness: 280, 
                        damping: 28,
                        mass: 0.8
                      },
                      scale: {
                        duration: 0.6,
                        repeat: isExpanded ? Infinity : 0,
                        ease: "easeInOut"
                      }
                    }}
                    style={{
                      width: '125px',
                      height: '125px',
                      borderRadius: '9999px',
                      backgroundColor: 'rgba(255,255,255,0.1)',
                      borderWidth: '2.5px',
                      borderStyle: 'solid',
                      borderColor: 'rgba(255,255,255,0.9)',
                      boxShadow: 'inset 0 4px 8px rgba(255,255,255,0.15), 0 8px 24px rgba(0,0,0,0.3)',
                    }}
                    className="relative backdrop-blur-xl cursor-pointer flex items-center justify-center"
                    aria-label="Main menu"
                  >
                    {/* Chef Hat - positioned on top left edge */}
                    {!isExpanded && <ChefHat />}
                    <motion.div
                      className="absolute inset-0 rounded-full pointer-events-none"
                      animate={{
                        scale: [1, 1.1, 1],
                        opacity: [0.2, 0.4, 0.2],
                      }}
                      transition={{
                        duration: 2.5,
                        repeat: Infinity,
                        ease: "easeInOut",
                        repeatType: "reverse"
                      }}
                      style={{
                        background: 'radial-gradient(circle, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0) 70%)',
                        filter: 'blur(8px)',
                      }}
                    />
                    
                    <AnimatePresence mode="wait">
                      {isExpanded ? (
                        <motion.div
                          key="mic"
                          initial={{ scale: 0, rotate: -180, opacity: 0 }}
                          animate={{ scale: 1, rotate: 0, opacity: 1 }}
                          exit={{ scale: 0, rotate: 180, opacity: 0 }}
                          transition={{ 
                            type: "spring", 
                            stiffness: 300, 
                            damping: 20 
                          }}
                          className="relative cursor-pointer"
                          onClick={(e) => {
                            e.stopPropagation();
                            setIsMicActive(!isMicActive);
                            if (!isMicActive) {
                              onVoiceCommand();
                            }
                          }}
                        >
                          {/* Strong green glowing ring when recording */}
                          {isMicActive && (
                            <>
                              {/* Inner intense glow */}
                              <motion.div
                                className="absolute inset-0 rounded-full pointer-events-none"
                                style={{
                                  left: '-20px',
                                  top: '-20px',
                                  width: '88px',
                                  height: '88px',
                                }}
                                animate={{
                                  scale: [1, 1.12, 1],
                                  opacity: [0.8, 1, 0.8],
                                }}
                                transition={{
                                  duration: 2,
                                  repeat: Infinity,
                                  ease: "easeInOut"
                                }}
                              >
                                <div 
                                  className="w-full h-full rounded-full"
                                  style={{
                                    background: 'radial-gradient(circle, rgba(34,197,94,0.6) 0%, rgba(34,197,94,0.2) 70%)',
                                    boxShadow: '0 0 40px rgba(34,197,94,0.9), 0 0 60px rgba(34,197,94,0.6), inset 0 0 25px rgba(34,197,94,0.4)',
                                    border: '3px solid rgba(34,197,94,0.8)',
                                  }}
                                />
                              </motion.div>
                              {/* Outer pulsing ring */}
                              <motion.div
                                className="absolute inset-0 rounded-full pointer-events-none"
                                style={{
                                  left: '-20px',
                                  top: '-20px',
                                  width: '88px',
                                  height: '88px',
                                }}
                                animate={{
                                  scale: [1, 1.35, 1],
                                  opacity: [0.6, 0, 0.6],
                                }}
                                transition={{
                                  duration: 2.5,
                                  repeat: Infinity,
                                  ease: "easeOut"
                                }}
                              >
                                <div 
                                  className="w-full h-full rounded-full"
                                  style={{
                                    border: '3px solid rgba(34,197,94,0.9)',
                                    boxShadow: '0 0 30px rgba(34,197,94,0.8), 0 0 50px rgba(34,197,94,0.5)',
                                  }}
                                />
                              </motion.div>
                              {/* Extra outer glow layer */}
                              <motion.div
                                className="absolute inset-0 rounded-full pointer-events-none"
                                style={{
                                  left: '-30px',
                                  top: '-30px',
                                  width: '108px',
                                  height: '108px',
                                }}
                                animate={{
                                  scale: [1, 1.2, 1],
                                  opacity: [0.3, 0.5, 0.3],
                                }}
                                transition={{
                                  duration: 1.8,
                                  repeat: Infinity,
                                  ease: "easeInOut"
                                }}
                              >
                                <div 
                                  className="w-full h-full rounded-full"
                                  style={{
                                    background: 'radial-gradient(circle, transparent 40%, rgba(34,197,94,0.3) 70%, transparent 100%)',
                                    boxShadow: '0 0 50px rgba(34,197,94,0.7)',
                                  }}
                                />
                              </motion.div>
                            </>
                          )}
                          <Mic 
                            size={48} 
                            className="relative z-10 transition-all duration-300" 
                            style={{
                              color: 'white',
                              filter: isMicActive ? 'drop-shadow(0 0 12px rgba(34,197,94,1)) drop-shadow(0 0 8px rgba(34,197,94,0.9)) drop-shadow(0 0 4px rgba(34,197,94,0.8))' : 'none'
                            }}
                          />
                        </motion.div>
                      ) : (
                        <motion.div
                          key="face"
                          initial={{ scale: 0, opacity: 0 }}
                          animate={{ 
                            scale: 1, 
                            opacity: 1,
                            x: headShakeOffset.x, // Horizontal arc
                            y: headShakeOffset.y, // Vertical arc (pendulum dips at center)
                            rotate: headShakeOffset.rotation // Tilt rotation
                          }}
                          exit={{ scale: 0, opacity: 0 }}
                          transition={{ 
                            type: "spring", 
                            stiffness: 300, 
                            damping: 20,
                            x: { type: "spring", stiffness: 150, damping: 12, mass: 0.5 }, // Bouncy spring motion
                            y: { type: "spring", stiffness: 180, damping: 10, mass: 0.4 }, // Slightly more bounce on vertical
                            rotate: { type: "spring", stiffness: 140, damping: 11, mass: 0.5 }
                          }}
                          className="absolute inset-0 flex items-center justify-center pointer-events-none"
                        >
                          {/* Face Container - Just eyes and mouth, no circles */}
                          <div className="relative w-20 h-20">
                            {/* Left Eye - Oval (vertical) */}
                            <motion.div
                              className="absolute rounded-full"
                              style={{
                                left: '26px',
                                top: '29px',
                                width: '8px',
                                height: '10px',
                                backgroundColor: 'rgba(255,255,255,1)',
                              }}
                              animate={{
                                x: getCursorTrackingOffset().x * 0.4,
                                y: getCursorTrackingOffset().y * 0.4,
                                scaleY: isBlinking ? 0.1 : 1,
                              }}
                              transition={{ 
                                x: { type: "spring", stiffness: 100, damping: 20 },
                                y: { type: "spring", stiffness: 100, damping: 20 },
                                scaleY: { duration: 0.1 }
                              }}
                            />
                            
                            {/* Right Eye - Oval (vertical) */}
                            <motion.div
                              className="absolute rounded-full"
                              style={{
                                left: '48px',
                                top: '29px',
                                width: '8px',
                                height: '10px',
                                backgroundColor: 'rgba(255,255,255,1)',
                              }}
                              animate={{
                                x: getCursorTrackingOffset().x * 0.4,
                                y: getCursorTrackingOffset().y * 0.4,
                                scaleY: isBlinking ? 0.1 : 1,
                              }}
                              transition={{ 
                                x: { type: "spring", stiffness: 100, damping: 20 },
                                y: { type: "spring", stiffness: 100, damping: 20 },
                                scaleY: { duration: 0.1 }
                              }}
                            />
                            
                            {/* Mouth - Simple Curved Smile */}
                            <motion.svg
                              className="absolute"
                              style={{
                                left: '24px',
                                top: '50px',
                                width: '32px',
                                height: '12px',
                              }}
                              animate={{
                                x: getCursorTrackingOffset().x * 0.3,
                                y: getCursorTrackingOffset().y * 0.3,
                              }}
                              transition={{ 
                                x: { type: "spring", stiffness: 100, damping: 20 },
                                y: { type: "spring", stiffness: 100, damping: 20 },
                              }}
                              viewBox="0 0 32 12"
                            >
                              {/* Simple smile curve */}
                              <path
                                d="M 4 2 Q 16 10 28 2"
                                fill="none"
                                stroke="rgba(255,255,255,1)"
                                strokeWidth="3"
                                strokeLinecap="round"
                              />
                            </motion.svg>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.button>
                </div>

                {/* Right Sub-button - Screenshot */}
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ scale: 0, x: 0, opacity: 0 }}
                      animate={{ 
                        scale: 1, 
                        x: 100, 
                        opacity: 1,
                      }}
                      exit={{ 
                        scale: 0, 
                        x: 0, 
                        opacity: 0,
                      }}
                      transition={{ 
                        type: "spring", 
                        stiffness: 200, 
                        damping: 15,
                        mass: 0.8
                      }}
                      className="absolute"
                    >
                      <motion.button
                        onClick={(e) => {
                          e.stopPropagation();
                          onDragDrop();
                        }}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        className="relative w-16 h-16 backdrop-blur-xl bg-white/10 border border-white/20 rounded-full cursor-pointer flex items-center justify-center shadow-[inset_0_2px_4px_rgba(255,255,255,0.1),0_4px_12px_rgba(0,0,0,0.2)]"
                        aria-label="Screenshot"
                      >
                        <motion.div
                          className="absolute inset-0 rounded-full bg-white/5"
                          animate={{
                            scale: [1, 1.2, 1],
                            opacity: [0.5, 0, 0.5],
                          }}
                          transition={{
                            duration: 2,
                            repeat: Infinity,
                            ease: "easeInOut",
                            delay: 0.3
                          }}
                        />
                        <Upload size={24} className="text-white relative z-10" />
                      </motion.button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </>
          )}
      </div>
    </>
  );
}