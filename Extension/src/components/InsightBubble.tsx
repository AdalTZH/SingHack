import { useEffect, useMemo, useRef, useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Button } from "./ui/button";

interface InsightBubbleProps {
  text: string;
  onSelect?: () => void;
  onExploreMore?: () => void;
  onClose?: () => void;
}

export function InsightBubble({ text, onSelect, onExploreMore, onClose }: InsightBubbleProps) {
  const [visibleChars, setVisibleChars] = useState(0);
  const characters = useMemo(() => text.split(""), [text]);
  const done = visibleChars >= characters.length;
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setVisibleChars(0);
  }, [text]);

  useEffect(() => {
    if (done) return;
    const interval = setInterval(() => {
      setVisibleChars((v) => Math.min(v + 2, characters.length));
    }, 35);
    return () => clearInterval(interval);
  }, [done, characters.length]);

  const shown = useMemo(() => characters.slice(0, visibleChars).join(""), [characters, visibleChars]);

  useEffect(() => {
    const c = containerRef.current;
    if (!c) return;
    c.scrollTop = c.scrollHeight;
  }, [shown]);

  

  return (
    <div className="fixed top-6 left-0 right-0 z-50 flex justify-center pointer-events-none">
      <AnimatePresence>
        <motion.div
          key="insight-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.25 }}
          className="fixed inset-0 z-40 bg-black/20 pointer-events-auto"
          onClick={onClose}
        />
        <motion.div
          key="insight-panel"
          initial={{ opacity: 0, y: -6, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -6, scale: 0.98 }}
          transition={{ duration: 0.25 }}
          className="relative z-50 max-w-[28rem] w-[46%] md:w-[40%] min-w-0 overflow-hidden pointer-events-auto px-6 py-4 rounded-[18px] bg-white/15 text-white border border-white/25 shadow-[0_8px_32px_0_rgba(31,38,135,0.37)]"
        >
          <div
            ref={containerRef}
            className="text-base md:text-lg leading-relaxed select-none overflow-y-auto overflow-x-hidden h-[58px] relative whitespace-normal break-words"
          >
            <div>
              {shown}
              {!done && <span className="inline-block w-3 h-5 align-baseline bg-white/70 animate-pulse ml-1" />}
            </div>
          </div>
          {done && (
            <div className="mt-4 flex gap-3">
              <Button size="lg" onClick={onSelect} className="bg-white/30 hover:bg-white/40 text-white border border-white/40">
                select
              </Button>
              <Button size="lg" variant="outline" onClick={onExploreMore} className="bg-transparent text-white border-white/40 hover:bg-white/10">
                explore more
              </Button>
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
