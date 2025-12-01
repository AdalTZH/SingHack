import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import qrCodeImage from '../assets/qr-code.svg';
import singpassLogo from '../assets/singpass_logo_fullcolour.png';

interface SingPassAuthProps {
  onComplete: () => void;
}

export function SingPassAuth({ onComplete }: SingPassAuthProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Simulate authentication process - in real implementation, 
    // this would listen for authentication events from SingPass
    // For now, we'll auto-advance after 3 seconds for demo purposes
    // TODO: Replace with actual SingPass authentication flow
    const timer = setTimeout(() => {
      setIsAuthenticated(true);
      // Wait a bit before transitioning
      setTimeout(() => {
        onComplete();
      }, 500);
    }, 3000);

    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      className="absolute inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="w-full max-w-md mx-auto px-6 py-8"
      >
        {/* SingPass Section */}
        <div className="text-center mb-6">
          <motion.h3
            initial={{ y: -10, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-xl font-semibold text-gray-900 dark:text-white mb-3"
          >
            Verify Your Identity
          </motion.h3>
          <motion.p
            initial={{ y: -10, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-sm text-gray-600 dark:text-gray-400 mb-6"
          >
            Scan with Singpass to authenticate
          </motion.p>

          {/* QR Code Container */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.4, type: "spring", stiffness: 200 }}
            className="flex justify-center mb-6"
          >
            <div className="bg-white p-4 rounded-lg shadow-lg">
              <img
                src={qrCodeImage}
                alt="QR Code"
                className="w-40 h-40"
                style={{ imageRendering: 'crisp-edges' }}
              />
            </div>
          </motion.div>

          {/* SingPass Logo */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="flex justify-center mt-6"
          >
            <img
              src={singpassLogo}
              alt="Singpass"
              className="h-8 w-auto"
            />
          </motion.div>

          {/* Authentication Status */}
          {isAuthenticated && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mt-4 text-green-600 dark:text-green-400 text-sm font-medium"
            >
              ✓ Authentication successful
            </motion.div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}

