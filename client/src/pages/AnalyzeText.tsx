import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { MessageSquare } from 'lucide-react';
import { Sidebar } from '../components/Sidebar';
import { GlassCard } from '../components/GlassCard';
import { SentimentBadge } from '../components/SentimentBadge';
import { AnimatedButton } from '../components/AnimatedButton';
import { analysisAPI, getErrorMessage } from '../services/api';
import { SentimentResult } from '../types';
import toast from 'react-hot-toast';

const AnalyzeText: React.FC = () => {
  const [text, setText] = useState('');
  const [result, setResult] = useState<SentimentResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalyze = async () => {
    if (!text.trim()) {
      toast.error('Please enter some text to analyze');
      return;
    }

    setIsAnalyzing(true);
    try {
      const response = await analysisAPI.analyzeText({ text });
      if (response.results && response.results.length > 0) {
        setResult(response.results[0]);
        toast.success('Analysis completed!');
      }
    } catch (error: any) {
      toast.error(getErrorMessage(error));
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleAnalyze();
    }
  };

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto">
        <div className="grid lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <Sidebar />
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Header */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass rounded-xl p-6"
            >
              <h1 className="text-3xl font-bold text-white mb-2">Analyze Text</h1>
              <p className="text-white/60">Real-time sentiment analysis for Vietnamese text</p>
            </motion.div>

            {/* Input Section */}
            <GlassCard className="p-6">
              <div className="mb-4">
                <label className="block text-white/80 text-sm font-medium mb-2">
                  Enter Vietnamese Text
                </label>
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Nhập văn bản tiếng Việt để phân tích cảm xúc..."
                  className="w-full h-32 p-4 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                />
                <p className="text-white/60 text-xs mt-2">
                  Press Ctrl+Enter to analyze quickly
                </p>
              </div>

              <AnimatedButton
                onClick={handleAnalyze}
                isLoading={isAnalyzing}
                className="w-full"
              >
                {isAnalyzing ? 'Analyzing...' : 'Analyze Sentiment'}
              </AnimatedButton>
            </GlassCard>

            {/* Result Section */}
            {result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <GlassCard className="p-6">
                  <h3 className="text-xl font-semibold text-white mb-4">Analysis Result</h3>

                  <div className="space-y-4">
                    <div>
                      <p className="text-white/80 text-sm mb-2">Original Text:</p>
                      <div className="bg-white/5 rounded-lg p-4">
                        <p className="text-white italic">"{text}"</p>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-white/80">Sentiment:</span>
                      <SentimentBadge sentiment={result.label} confidence={result.confidence} />
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-white/80">Confidence:</span>
                      <span className="text-white font-medium">
                        {Math.round(result.confidence * 100)}%
                      </span>
                    </div>
                  </div>
                </GlassCard>
              </motion.div>
            )}

            {/* Tips */}
            <GlassCard className="p-6">
              <h3 className="text-lg font-semibold text-white mb-3">Tips for Better Results</h3>
              <ul className="text-white/70 space-y-2 text-sm">
                <li>• Use complete sentences for more accurate analysis</li>
                <li>• Include context when analyzing ambiguous text</li>
                <li>• The model works best with Vietnamese text</li>
                <li>• Results are based on the PhoBERT model fine-tuned for sentiment</li>
              </ul>
            </GlassCard>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyzeText;