import { useState, useEffect } from 'react';
import { motion } from 'motion/react';

export function CursorTextBox() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return (
    <motion.div
      className="fixed pointer-events-none z-[9999]"
      style={{
        left: mousePosition.x + 20,
        top: mousePosition.y + 20,
      }}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{
        type: "spring",
        stiffness: 500,
        damping: 28,
      }}
    >
      <div className="backdrop-blur-xl bg-white/20 border border-white/30 rounded-[8px] px-4 py-2 shadow-[0_8px_32px_0_rgba(31,38,135,0.37),inset_0_2px_4px_rgba(255,255,255,0.1)]">
        <span className="text-white text-sm whitespace-nowrap">
          Leo is handsome
        </span>
      </div>
    </motion.div>
  );
}
