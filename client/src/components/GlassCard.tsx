import React from 'react';
import { cn } from '../utils/cn';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className,
  hover = false
}) => {
  return (
    <div
      className={cn(
        "glass rounded-xl p-6 shadow-lg",
        hover && "hover:shadow-xl hover:scale-105 transition-all duration-300",
        className
      )}
    >
      {children}
    </div>
  );
};