import { useState, useRef, useEffect } from 'react';
import { Send, X } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

interface TextMessageDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSend: (message: string) => void;
  messages: Message[];
  isLoading?: boolean;
}

export function TextMessageDialog({ isOpen, onClose, onSend, messages, isLoading = false }: TextMessageDialogProps) {
  const [inputValue, setInputValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    console.log('TextMessageDialog isOpen:', isOpen);
    if (isOpen && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    if (isOpen && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const handleSend = () => {
    if (!inputValue.trim()) return;
    onSend(inputValue);
    setInputValue('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
          />

          {/* Half-Screen Chat Panel */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="fixed right-0 top-0 bottom-0 w-1/2 z-50 flex flex-col"
          >
            <div className="backdrop-blur-xl bg-white/10 border-l border-white/20 shadow-[-8px_0_32px_0_rgba(31,38,135,0.37)] flex flex-col h-full">
              {/* Header */}
              <div className="flex justify-between items-center px-6 py-5 border-b border-white/10 flex-shrink-0">
                <h3 className="text-white">Chat</h3>
                <button
                  onClick={onClose}
                  className="w-9 h-9 backdrop-blur-xl bg-white/10 border border-white/20 rounded-full cursor-pointer transition-all duration-300 flex items-center justify-center hover:bg-white/20 active:scale-95"
                  aria-label="Close"
                >
                  <X size={18} className="text-white" />
                </button>
              </div>

              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto px-6 py-4 min-h-0">
                {messages.length === 0 ? (
                  <div className="text-center py-20 text-white/70">
                    <p>Start a conversation...</p>
                  </div>
                ) : (
                  <>
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex mb-4 animate-[fadeIn_0.3s_ease-in] ${
                          message.sender === 'user' ? 'justify-end' : 'justify-start'
                        }`}
                      >
                        <div
                          className={`max-w-[75%] px-4 py-3 rounded-[18px] break-words backdrop-blur-lg border shadow-[0_4px_16px_0_rgba(31,38,135,0.2)] ${
                            message.sender === 'user'
                              ? 'bg-white/25 text-white border-white/30 rounded-br-[4px]'
                              : 'bg-white/15 text-white border-white/20 rounded-bl-[4px]'
                          }`}
                        >
                          {message.text}
                        </div>
                      </div>
                    ))}
                    {isLoading && (
                      <div className="flex mb-4 animate-[fadeIn_0.3s_ease-in]">
                        <div className="max-w-[75%] px-4 py-3 rounded-[18px] backdrop-blur-lg bg-white/15 text-white border border-white/20 rounded-bl-[4px] shadow-[0_4px_16px_0_rgba(31,38,135,0.2)]">
                          <div className="inline-flex gap-1 items-center">
                            <div className="w-2 h-2 rounded-full bg-white/80 animate-[bounce_1.4s_infinite_ease-in-out_both] [animation-delay:-0.32s]" />
                            <div className="w-2 h-2 rounded-full bg-white/80 animate-[bounce_1.4s_infinite_ease-in-out_both] [animation-delay:-0.16s]" />
                            <div className="w-2 h-2 rounded-full bg-white/80 animate-[bounce_1.4s_infinite_ease-in-out_both]" />
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </>
                )}
              </div>

              {/* Input Area */}
              <div className="flex gap-3 px-6 py-5 border-t border-white/10 flex-shrink-0">
                <textarea
                  ref={textareaRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  className="flex-1 backdrop-blur-xl bg-white/10 border border-white/20 rounded-[24px] px-4 py-3 resize-none max-h-[120px] outline-none transition-all duration-300 focus:bg-white/15 active:scale-[0.99] text-white placeholder:text-white/50 shadow-[inset_0_2px_4px_rgba(255,255,255,0.1),0_2px_8px_rgba(0,0,0,0.1)]"
                  rows={3}
                />
                <button
                  onClick={handleSend}
                  disabled={!inputValue.trim()}
                  className="w-12 h-12 border border-white/20 rounded-full backdrop-blur-xl bg-white/10 text-white cursor-pointer flex items-center justify-center transition-all duration-300 flex-shrink-0 hover:bg-white/15 active:scale-95 shadow-[inset_0_2px_4px_rgba(255,255,255,0.1),0_2px_8px_rgba(0,0,0,0.1)] disabled:opacity-40 disabled:cursor-not-allowed disabled:active:scale-100 self-end"
                  aria-label="Send message"
                >
                  <Send size={20} />
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
