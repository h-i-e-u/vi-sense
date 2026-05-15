import React from 'react';
import { motion } from 'framer-motion';
import { GlassCard } from './GlassCard';

interface ChartCardProps {
  title: string;
  children: React.ReactNode;
  className?: string;
}

export const ChartCard: React.FC<ChartCardProps> = ({
  title,
  children,
  className
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <GlassCard className={className}>
        <h3 className="text-xl font-semibold text-white mb-4">{title}</h3>
        <div className="w-full">
          {children}
        </div>
      </GlassCard>
    </motion.div>
  );
};