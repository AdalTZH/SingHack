import { useState } from 'react';
import { motion } from 'motion/react';
import { CreditCard, Lock, X, Minus, Maximize2 } from 'lucide-react';

interface PaymentProps {
  selectedPlan: number;
  onComplete: () => void;
  onBack: () => void;
}

const planDetails = [
  { name: 'Basic Plan', price: '$29' },
  { name: 'Premium Plan', price: '$59' },
  { name: 'Ultimate Plan', price: '$99' },
];

export function Payment({ selectedPlan, onComplete, onBack }: PaymentProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const plan = planDetails[selectedPlan];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsProcessing(true);
    
    // Simulate payment processing
    setTimeout(() => {
      setIsProcessing(false);
      onComplete();
    }, 2000);
  };

  return (
    <div className="absolute inset-0 z-20 flex items-center justify-center px-4 pb-44 pointer-events-none">
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
        onClick={onBack}
        className="absolute inset-0 bg-black/30 backdrop-blur-sm pointer-events-auto"
      />

      {/* Payment Window Bubble */}
      <motion.div
        initial={{ opacity: 0, scale: 0.85, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.85, y: 20 }}
        transition={{
          type: "spring",
          stiffness: 300,
          damping: 25,
        }}
        className="relative w-full max-w-sm pointer-events-auto"
      >
        {/* Payment card bubble */}
        <div className="backdrop-blur-xl bg-white/15 border-2 border-white/30 rounded-[28px] shadow-[inset_0_4px_12px_rgba(255,255,255,0.15),0_12px_40px_rgba(0,0,0,0.4)] overflow-hidden">
          {/* Animated glow */}
          <motion.div
            className="absolute inset-0 rounded-[32px] pointer-events-none"
            animate={{
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            style={{
              background: 'radial-gradient(circle at 50% 0%, rgba(100, 200, 255, 0.3) 0%, transparent 70%)',
              filter: 'blur(30px)',
            }}
          />

          <div className="relative z-10 p-6">
            {/* Window Control Buttons - macOS style */}
            <div className="absolute top-5 left-5 flex items-center gap-2">
              <motion.button
                onClick={onBack}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="w-3 h-3 rounded-full bg-red-400/80 hover:bg-red-500 border border-red-600/30 shadow-sm transition-colors group relative"
                title="Close"
              >
                <X size={8} className="absolute inset-0 m-auto text-red-900/70 opacity-0 group-hover:opacity-100 transition-opacity" />
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="w-3 h-3 rounded-full bg-yellow-400/80 hover:bg-yellow-500 border border-yellow-600/30 shadow-sm transition-colors group relative"
                title="Minimize"
              >
                <Minus size={8} className="absolute inset-0 m-auto text-yellow-900/70 opacity-0 group-hover:opacity-100 transition-opacity" />
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="w-3 h-3 rounded-full bg-green-400/80 hover:bg-green-500 border border-green-600/30 shadow-sm transition-colors group relative"
                title="Expand"
              >
                <Maximize2 size={7} className="absolute inset-0 m-auto text-green-900/70 opacity-0 group-hover:opacity-100 transition-opacity" />
              </motion.button>
            </div>

            {/* Header */}
            <div className="text-center mb-5 mt-4">
              <div className="inline-flex items-center justify-center w-14 h-14 backdrop-blur-lg bg-white/20 border border-white/30 rounded-full mb-2">
                <CreditCard size={24} className="text-white" />
              </div>
              <h2 className="text-white mb-0.5">Complete Payment</h2>
              <p className="text-white/70 text-sm">Secure checkout for {plan.name}</p>
            </div>

            {/* Plan summary */}
            <div className="backdrop-blur-md bg-white/10 border border-white/20 rounded-2xl p-3.5 mb-5">
              <div className="flex justify-between items-center">
                <span className="text-white/80">{plan.name}</span>
                <span className="text-white">{plan.price}/month</span>
              </div>
            </div>

            {/* Payment form */}
            <form onSubmit={handleSubmit} className="space-y-3.5">
              {/* Card number */}
              <div>
                <label className="text-white/70 text-sm mb-1 block">Card Number</label>
                <input
                  type="text"
                  placeholder="1234 5678 9012 3456"
                  required
                  className="w-full backdrop-blur-md bg-white/10 border border-white/20 rounded-xl px-3.5 py-2.5 text-white placeholder:text-white/40 outline-none focus:border-white/40 transition-colors text-sm"
                />
              </div>

              {/* Card details row */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-white/70 text-sm mb-1 block">Expiry Date</label>
                  <input
                    type="text"
                    placeholder="MM/YY"
                    required
                    className="w-full backdrop-blur-md bg-white/10 border border-white/20 rounded-xl px-3.5 py-2.5 text-white placeholder:text-white/40 outline-none focus:border-white/40 transition-colors text-sm"
                  />
                </div>
                <div>
                  <label className="text-white/70 text-sm mb-1 block">CVV</label>
                  <input
                    type="text"
                    placeholder="123"
                    required
                    maxLength={3}
                    className="w-full backdrop-blur-md bg-white/10 border border-white/20 rounded-xl px-3.5 py-2.5 text-white placeholder:text-white/40 outline-none focus:border-white/40 transition-colors text-sm"
                  />
                </div>
              </div>

              {/* Name on card */}
              <div>
                <label className="text-white/70 text-sm mb-1 block">Name on Card</label>
                <input
                  type="text"
                  placeholder="John Doe"
                  required
                  className="w-full backdrop-blur-md bg-white/10 border border-white/20 rounded-xl px-3.5 py-2.5 text-white placeholder:text-white/40 outline-none focus:border-white/40 transition-colors text-sm"
                />
              </div>

              {/* Submit button */}
              <motion.button
                type="submit"
                disabled={isProcessing}
                whileHover={{ scale: isProcessing ? 1 : 1.02 }}
                whileTap={{ scale: isProcessing ? 1 : 0.98 }}
                className="w-full backdrop-blur-lg bg-white/25 border border-white/40 rounded-xl py-3 px-6 text-white shadow-[inset_0_2px_4px_rgba(255,255,255,0.2),0_4px_16px_rgba(0,0,0,0.2)] transition-all disabled:opacity-50 disabled:cursor-not-allowed mt-5"
              >
                {isProcessing ? (
                  <div className="flex items-center justify-center gap-2">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                    />
                    <span>Processing...</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center gap-2">
                    <Lock size={18} />
                    <span>Pay {plan.price}</span>
                  </div>
                )}
              </motion.button>

              {/* Security note */}
              <div className="flex items-center justify-center gap-1.5 text-white/50 text-xs mt-3">
                <Lock size={11} />
                <span>Secured by 256-bit encryption</span>
              </div>
            </form>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
