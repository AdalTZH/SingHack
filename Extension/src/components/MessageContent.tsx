/**
 * MessageContent Component
 * Renders message text with clickable plan mentions that redirect to Stripe on double-click
 */

import { useCallback } from 'react';
import { redirectToStripe } from '../utils/stripeRedirect';

interface MessageContentProps {
  text: string;
  sender: 'user' | 'assistant';
}

export function MessageContent({ text, sender }: MessageContentProps) {
  const handlePlanDoubleClick = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    console.log('💳 Double-clicked on plan, redirecting to Stripe...');
    redirectToStripe({
      travel_context: 'Plan Selection'
    });
  }, []);

  // Only process assistant messages for plan detection
  if (sender !== 'assistant') {
    return <div className="message-content">{text}</div>;
  }

  // Patterns to match plan-related text
  const planPatterns = [
    /plans available/gi,
    /available plans/gi,
    /insurance plans/gi,
    /travel insurance plans/gi,
    /plan recommendations/gi,
    /recommended plans/gi,
    /plan options/gi,
    /insurance options/gi,
  ];

  // Check if message contains plan-related text
  const hasPlanText = planPatterns.some(pattern => pattern.test(text));

  if (!hasPlanText) {
    return <div className="message-content">{text}</div>;
  }

  // Split text and highlight plan mentions
  const renderTextWithPlans = () => {
    const parts: Array<{ text: string; isPlan: boolean }> = [];
    let lastIndex = 0;
    let textToProcess = text;

    // Find all matches
    const matches: Array<{ index: number; length: number; text: string }> = [];
    planPatterns.forEach(pattern => {
      const regex = new RegExp(pattern.source, 'gi');
      let match;
      while ((match = regex.exec(textToProcess)) !== null) {
        matches.push({
          index: match.index,
          length: match[0].length,
          text: match[0]
        });
      }
    });

    // Sort matches by index
    matches.sort((a, b) => a.index - b.index);

    // Remove overlapping matches (keep the first one)
    const uniqueMatches: typeof matches = [];
    for (const match of matches) {
      if (uniqueMatches.length === 0 || match.index >= uniqueMatches[uniqueMatches.length - 1].index + uniqueMatches[uniqueMatches.length - 1].length) {
        uniqueMatches.push(match);
      }
    }

    // Build parts array
    for (const match of uniqueMatches) {
      // Add text before match
      if (match.index > lastIndex) {
        parts.push({
          text: textToProcess.substring(lastIndex, match.index),
          isPlan: false
        });
      }
      // Add match as plan
      parts.push({
        text: match.text,
        isPlan: true
      });
      lastIndex = match.index + match.length;
    }

    // Add remaining text
    if (lastIndex < textToProcess.length) {
      parts.push({
        text: textToProcess.substring(lastIndex),
        isPlan: false
      });
    }

    // If no matches found, return original text
    if (parts.length === 0) {
      return <div className="message-content">{text}</div>;
    }

    return (
      <div className="message-content">
        {parts.map((part, index) => {
          if (part.isPlan) {
            return (
              <span
                key={index}
                className="plan-link"
                onDoubleClick={handlePlanDoubleClick}
                title="Double-click to view plans on Stripe"
              >
                {part.text}
              </span>
            );
          }
          return <span key={index}>{part.text}</span>;
        })}
      </div>
    );
  };

  return renderTextWithPlans();
}

