import React from 'react';
import { cn } from '../utils/cn';

interface SentimentBadgeProps {
  sentiment: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL';
  confidence?: number;
  className?: string;
}

export const SentimentBadge: React.FC<SentimentBadgeProps> = ({
  sentiment,
  confidence,
  className
}) => {
  const getSentimentColor = () => {
    switch (sentiment) {
      case 'POSITIVE':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'NEGATIVE':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'NEUTRAL':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  return (
    <div
      className={cn(
        "inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border",
        getSentimentColor(),
        className
      )}
    >
      <span className="capitalize">{sentiment.toLowerCase()}</span>
      {confidence && (
        <span className="ml-2 text-xs opacity-75">
          ({Math.round(confidence * 100)}%)
        </span>
      )}
    </div>
  );
};