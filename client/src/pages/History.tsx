import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { History as HistoryIcon, Calendar, FileText } from 'lucide-react';
import { Sidebar } from '../components/Sidebar';
import { GlassCard } from '../components/GlassCard';
import { SentimentBadge } from '../components/SentimentBadge';
import { historyAPI } from '../services/api';
import { AnalysisJob } from '../types';

const History: React.FC = () => {
  const [jobs, setJobs] = useState<AnalysisJob[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await historyAPI.getHistory();
        setJobs(data);
      } catch (error) {
        console.error('Failed to fetch history:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  const getJobTypeIcon = (type: string) => {
    switch (type) {
      case 'text': return '💬';
      case 'link': return '🔗';
      case 'file': return '📄';
      default: return '📋';
    }
  };

  const getJobTypeLabel = (type: string) => {
    switch (type) {
      case 'text': return 'Text Analysis';
      case 'link': return 'Link Analysis';
      case 'file': return 'File Analysis';
      default: return 'Analysis';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen p-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-4 gap-6">
            <div className="lg:col-span-1">
              <Sidebar />
            </div>
            <div className="lg:col-span-3 flex items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

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
              <h1 className="text-3xl font-bold text-white mb-2">Analysis History</h1>
              <p className="text-white/60">View your previous sentiment analysis jobs</p>
            </motion.div>

            {/* History List */}
            {jobs.length === 0 ? (
              <GlassCard className="p-8 text-center">
                <HistoryIcon className="h-16 w-16 text-white/40 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">No Analysis History</h3>
                <p className="text-white/60">Start by analyzing some text, links, or files</p>
              </GlassCard>
            ) : (
              <div className="space-y-4">
                {jobs.map((job, index) => (
                  <motion.div
                    key={job.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                  >
                    <GlassCard className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-4">
                          <div className="text-2xl">{getJobTypeIcon(job.type)}</div>
                          <div className="flex-1">
                            <h3 className="text-lg font-semibold text-white mb-1">
                              {getJobTypeLabel(job.type)}
                            </h3>
                            <div className="flex items-center space-x-4 text-white/60 text-sm mb-3">
                              <div className="flex items-center space-x-1">
                                <Calendar className="h-4 w-4" />
                                <span>{new Date(job.created_at).toLocaleDateString()}</span>
                              </div>
                              <div className={`px-2 py-1 rounded text-xs ${
                                job.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                                job.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                                'bg-yellow-500/20 text-yellow-400'
                              }`}>
                                {job.status}
                              </div>
                            </div>

                            {job.metadata && (
                              <div className="grid grid-cols-3 gap-4 text-sm">
                                <div>
                                  <span className="text-white/60">Total: </span>
                                  <span className="text-white">{job.metadata.total_comments || 0}</span>
                                </div>
                                <div>
                                  <span className="text-white/60">Positive: </span>
                                  <span className="text-green-400">
                                    {job.metadata.positive_ratio ? Math.round(job.metadata.positive_ratio * 100) : 0}%
                                  </span>
                                </div>
                                <div>
                                  <span className="text-white/60">Negative: </span>
                                  <span className="text-red-400">
                                    {job.metadata.negative_ratio ? Math.round(job.metadata.negative_ratio * 100) : 0}%
                                  </span>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>

                        {job.results && job.results.length > 0 && (
                          <div className="flex flex-col items-end space-y-2">
                            <SentimentBadge
                              sentiment={job.results[0].label}
                              confidence={job.results[0].confidence}
                            />
                            {job.results.length > 1 && (
                              <span className="text-white/60 text-xs">
                                +{job.results.length - 1} more
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </GlassCard>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default History;