import { useState } from 'react';
import { motion } from 'motion/react';
import { Check } from 'lucide-react';

interface DecisionMakingProps {
  onSelect: (option: number) => void;
}

const options = [
  {
    title: 'Basic Plan',
    price: '$29',
    features: ['Coverage up to $50K', 'Emergency Support', 'Annual Check-up'],
  },
  {
    title: 'Premium Plan',
    price: '$59',
    features: ['Coverage up to $100K', '24/7 Support', 'Bi-annual Check-up', 'Dental Coverage'],
    recommended: true,
  },
  {
    title: 'Ultimate Plan',
    price: '$99',
    features: ['Coverage up to $250K', 'Priority Support', 'Quarterly Check-up', 'Full Dental & Vision', 'Wellness Programs'],
  },
];

export function DecisionMaking({ onSelect }: DecisionMakingProps) {
  const [selectedIndex, setSelectedIndex] = useState(1); // Default to Premium Plan (recommended)

  const handleToggle = (index: number) => {
    setSelectedIndex(index);
  };
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      className="flex items-start justify-center min-h-screen px-6 pt-4 pb-32 overflow-y-auto"
    >
      <div className="flex flex-col items-center gap-3 max-w-5xl w-full">
        {/* Header */}
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-center mb-1"
        >
          <h1 className="text-white mb-1">Choose Your Plan</h1>
          <p className="text-white/70 text-sm">Select the insurance plan that best fits your needs</p>
        </motion.div>

        {/* Comparison bubbles - 280px x 170px each, lined up vertically */}
        <div className="flex flex-col gap-3 w-full items-center">
          {options.map((option, index) => (
            <motion.div
              key={index}
              initial={{ scale: 0.8, y: 50, opacity: 0 }}
              animate={{ scale: 1, y: 0, opacity: 1 }}
              transition={{
                type: "spring",
                stiffness: 200,
                damping: 20,
                delay: 0.3 + index * 0.1,
              }}
              whileHover={{ scale: 1.02 }}
              onClick={() => onSelect(index)}
              style={{
                width: '280px',
                height: '170px',
              }}
              className="relative backdrop-blur-xl bg-white/15 border-2 border-white/30 rounded-[20px] shadow-[inset_0_4px_12px_rgba(255,255,255,0.15),0_12px_40px_rgba(0,0,0,0.3)] cursor-pointer overflow-hidden"
            >
              {/* Toggle button at top right */}
              <motion.button
                onClick={(e) => {
                  e.stopPropagation();
                  handleToggle(index);
                }}
                whileTap={{ scale: 0.9 }}
                className="absolute top-3 right-3 z-20"
              >
                <motion.div
                  animate={{
                    boxShadow: selectedIndex === index 
                      ? ['0 0 0 rgba(34, 197, 94, 0)', '0 0 20px rgba(34, 197, 94, 0.8)', '0 0 0 rgba(34, 197, 94, 0)']
                      : '0 0 0 rgba(255, 255, 255, 0)',
                  }}
                  transition={{
                    duration: 2,
                    repeat: selectedIndex === index ? Infinity : 0,
                    ease: "easeInOut",
                  }}
                  className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all ${
                    selectedIndex === index
                      ? 'bg-green-500 border-green-400'
                      : 'bg-white/10 border-white/30'
                  }`}
                >
                  {selectedIndex === index && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: "spring", stiffness: 300 }}
                    >
                      <Check size={12} className="text-white" strokeWidth={3} />
                    </motion.div>
                  )}
                </motion.div>
              </motion.button>

              {/* Animated glow */}
              <motion.div
                className="absolute inset-0 rounded-[20px] pointer-events-none"
                animate={{
                  opacity: selectedIndex === index ? [0.3, 0.5, 0.3] : [0.2, 0.4, 0.2],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: index * 0.3,
                }}
                style={{
                  background: selectedIndex === index
                    ? 'radial-gradient(circle at 50% 50%, rgba(34, 197, 94, 0.3) 0%, transparent 70%)'
                    : 'radial-gradient(circle at 50% 50%, rgba(255,255,255,0.2) 0%, transparent 70%)',
                  filter: 'blur(15px)',
                }}
              />

              {/* Content */}
              <div className="relative z-10 p-4 h-full flex flex-col">
                {/* Plan title and price */}
                <div className="mb-2">
                  <h3 className="text-white text-sm mb-0.5">{option.title}</h3>
                  <div className="text-white/90">
                    <span className="text-xl">{option.price}</span>
                    <span className="text-xs text-white/60">/month</span>
                  </div>
                </div>

                {/* Features */}
                <div className="flex-1 space-y-1">
                  {option.features.map((feature, fIndex) => (
                    <div key={fIndex} className="flex items-start gap-1.5">
                      <Check size={14} className="text-white/80 mt-0.5 flex-shrink-0" />
                      <span className="text-white/80 text-xs">{feature}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Hover effect */}
              <motion.div
                className="absolute inset-0 rounded-[20px] pointer-events-none opacity-0 hover:opacity-100 transition-opacity"
                style={{
                  background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 100%)',
                }}
              />
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
