import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import logoImage from 'figma:asset/af381eb3a8f7834d199ad1e91c14bd520807f3d6.png';

interface StartPageProps {
  onComplete: () => void;
}

export function StartPage({ onComplete }: StartPageProps) {
  const [stage, setStage] = useState<'morph' | 'fadeOut'>('morph');

  useEffect(() => {
    // After 3 seconds, start fade out
    const morphTimer = setTimeout(() => {
      setStage('fadeOut');
    }, 3000);

    // After fade out completes, call onComplete
    const completeTimer = setTimeout(() => {
      onComplete();
    }, 3600);

    return () => {
      clearTimeout(morphTimer);
      clearTimeout(completeTimer);
    };
  }, [onComplete]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: stage === 'fadeOut' ? 0 : 1 }}
      transition={{ duration: 0.6 }}
      className="absolute inset-0 z-50 flex items-center justify-center"
    >
      {/* Dark overlay that fades out */}
      <motion.div
        initial={{ opacity: 1 }}
        animate={{ opacity: stage === 'fadeOut' ? 0 : 1 }}
        transition={{ duration: 0.5 }}
        className="absolute inset-0 bg-black/70"
      />

      {/* Glassmorphism bubble that morphs to FAB */}
      <motion.div
        layoutId="morph-container"
        initial={{ scale: 0.5, opacity: 0 }}
        animate={{ 
          scale: [0.5, 1.1, 1],
          opacity: 1,
        }}
        exit={{
          opacity: 1,
          transition: { duration: 0 }
        }}
        transition={{
          scale: {
            duration: 2.2,
            ease: [0.34, 1.56, 0.64, 1],
          },
          opacity: {
            duration: 0.4,
          },
          layout: {
            type: "spring", 
            stiffness: 260, 
            damping: 30,
            mass: 1
          }
        }}
        style={{
          width: '110px',
          height: '110px',
          borderRadius: '9999px',
          backgroundColor: 'rgba(255,255,255,0.15)',
          borderWidth: '2px',
          borderStyle: 'solid',
          borderColor: 'rgba(255,255,255,0.3)',
          boxShadow: 'inset 0 4px 8px rgba(255,255,255,0.15), 0 8px 24px rgba(0,0,0,0.3)',
        }}
        className="relative backdrop-blur-xl flex items-center justify-center"
      >
        {/* Pulsing glow effect */}
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

        {/* Logo - 72px x 72px */}
        <motion.img
          src={logoImage}
          alt="Logo"
          initial={{ rotate: -180, opacity: 0 }}
          animate={{ 
            rotate: [-180, 10, 0],
            opacity: stage === 'fadeOut' ? 0 : 1,
          }}
          transition={{
            rotate: {
              duration: 2.2,
              ease: [0.34, 1.56, 0.64, 1],
            },
            opacity: {
              duration: stage === 'fadeOut' ? 0.3 : 0.4,
            }
          }}
          style={{
            width: '72px',
            height: '72px',
          }}
          className="relative z-10 object-contain"
        />
      </motion.div>
    </motion.div>
  );
}
