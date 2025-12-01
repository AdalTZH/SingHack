import { motion } from 'motion/react';

export function ChefHat() {
  return (
    <motion.div
      className="absolute pointer-events-none"
      style={{
        top: '-42px',
        left: '-1px',
        zIndex: 100,
        transformOrigin: 'bottom left',
      }}
      initial={{ scale: 0, rotate: -20 }}
      animate={{ 
        scale: 1, 
        rotate: -26,
      }}
      transition={{
        scale: { type: "spring", stiffness: 200, damping: 15, delay: 0.2 },
        rotate: { type: "spring", stiffness: 200, damping: 15, delay: 0.2 },
      }}
    >
      <svg 
        width="93.98" 
        height="86.75" 
        viewBox="0 0 100 100" 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
        style={{
          filter: 'drop-shadow(0 1px 4px rgba(0,0,0,0.18))',
        }}
      >
        <path
          d="M 20 65 C 8 50 22 30 38 42 C 38 18 68 18 72 42 C 85 38 96 52 82 65"
          stroke="rgba(255,255,255,0.95)"
          strokeWidth="4"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M 18 68 Q 50 52 82 68 L 82 82 Q 50 66 18 82 Z"
          fill="none"
          stroke="rgba(255,255,255,0.95)"
          strokeWidth="4"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </motion.div>
  );
}
