import { useRef } from 'react';
import { motion } from 'motion/react';

interface LandingPageProps {
  onDoubleTap: () => void;
}

export function LandingPage({ onDoubleTap }: LandingPageProps) {
  const lastTapRef = useRef(0);

  const handleClick = (e: React.MouseEvent) => {
    // Check if click is not on the FAB button area (bottom portion)
    const clickY = e.clientY;
    const windowHeight = window.innerHeight;
    
    // If click is in the bottom 150px (where FAB is), ignore it
    if (windowHeight - clickY < 150) {
      return;
    }

    const now = Date.now();
    const timeSinceLastTap = now - lastTapRef.current;
    
    if (timeSinceLastTap < 400 && timeSinceLastTap > 0) {
      // Double tap detected
      onDoubleTap();
      lastTapRef.current = 0; // Reset to prevent triple-tap
    } else {
      lastTapRef.current = now;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      className="flex items-center justify-center min-h-screen cursor-pointer pb-32"
      onClick={handleClick}
    >
      {/* Blank page - FAB button is shown in App.tsx */}
      <motion.div
        className="text-white/40 text-sm"
        animate={{
          opacity: [0.3, 0.6, 0.3],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      >
        Double-click to continue
      </motion.div>
    </motion.div>
  );
}
