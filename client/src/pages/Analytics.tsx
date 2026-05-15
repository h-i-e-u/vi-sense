import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, MessageSquare, ThumbsUp, ThumbsDown } from 'lucide-react';
import { Sidebar } from '../components/Sidebar';
import { ChartCard } from '../components/ChartCard';
import { GlassCard } from '../components/GlassCard';
import { SentimentBadge } from '../components/SentimentBadge';
import { analyticsAPI } from '../services/api';
import { AnalyticsSummary } from '../types';
import { PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar } from 'recharts';

const Analytics: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const data = await analyticsAPI.getSummary();
        setAnalytics(data);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  const pieData = analytics ? [
    { name: 'Positive', value: analytics.sentiment_distribution.positive, color: '#10B981' },
    { name: 'Neutral', value: analytics.sentiment_distribution.neutral, color: '#F59E0B' },
    { name: 'Negative', value: analytics.sentiment_distribution.negative, color: '#EF4444' },
  ] : [];

  const keywordData = analytics?.top_keywords?.slice(0, 10).map((kw, index) => ({
    name: kw.word,
    value: kw.count,
    fill: `hsl(${index * 36}, 70%, 50%)`
  })) || [];

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
              <h1 className="text-3xl font-bold text-white mb-2">Analytics Dashboard</h1>
              <p className="text-white/60">Comprehensive insights into your sentiment analysis data</p>
            </motion.div>

            {/* Key Metrics */}
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <GlassCard className="p-6 text-center">
                <TrendingUp className="h-8 w-8 text-blue-400 mx-auto mb-3" />
                <h3 className="text-2xl font-bold text-white mb-1">{analytics?.total_analyses || 0}</h3>
                <p className="text-white/60 text-sm">Total Analyses</p>
              </GlassCard>

              <GlassCard className="p-6 text-center">
                <ThumbsUp className="h-8 w-8 text-green-400 mx-auto mb-3" />
                <h3 className="text-2xl font-bold text-white mb-1">{analytics?.sentiment_distribution.positive || 0}</h3>
                <p className="text-white/60 text-sm">Positive Sentiments</p>
              </GlassCard>

              <GlassCard className="p-6 text-center">
                <MessageSquare className="h-8 w-8 text-yellow-400 mx-auto mb-3" />
                <h3 className="text-2xl font-bold text-white mb-1">{analytics?.sentiment_distribution.neutral || 0}</h3>
                <p className="text-white/60 text-sm">Neutral Sentiments</p>
              </GlassCard>

              <GlassCard className="p-6 text-center">
                <ThumbsDown className="h-8 w-8 text-red-400 mx-auto mb-3" />
                <h3 className="text-2xl font-bold text-white mb-1">{analytics?.sentiment_distribution.negative || 0}</h3>
                <p className="text-white/60 text-sm">Negative Sentiments</p>
              </GlassCard>
            </div>

            {/* Charts */}
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Sentiment Distribution */}
              <ChartCard title="Sentiment Distribution">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </ChartCard>

              {/* Trend Chart */}
              <ChartCard title="Sentiment Trends (7 Days)">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={analytics?.trend_data || []}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis
                      dataKey="date"
                      stroke="#9CA3AF"
                      fontSize={12}
                    />
                    <YAxis stroke="#9CA3AF" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        borderRadius: '8px'
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="positive"
                      stroke="#10B981"
                      strokeWidth={2}
                      name="Positive"
                    />
                    <Line
                      type="monotone"
                      dataKey="neutral"
                      stroke="#F59E0B"
                      strokeWidth={2}
                      name="Neutral"
                    />
                    <Line
                      type="monotone"
                      dataKey="negative"
                      stroke="#EF4444"
                      strokeWidth={2}
                      name="Negative"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>

            {/* Top Keywords */}
            <ChartCard title="Top Keywords">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={keywordData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis
                    dataKey="name"
                    stroke="#9CA3AF"
                    fontSize={12}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis stroke="#9CA3AF" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(0, 0, 0, 0.8)',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      borderRadius: '8px'
                    }}
                  />
                  <Bar dataKey="value" fill="#8B5CF6" />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>

            {/* Top Comments */}
            <div className="grid lg:grid-cols-2 gap-6">
              <ChartCard title="Top Positive Comments">
                <div className="space-y-4">
                  {analytics?.top_positive_comments?.slice(0, 5).map((comment, index) => (
                    <motion.div
                      key={comment.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5, delay: index * 0.1 }}
                      className="p-4 bg-green-500/10 rounded-lg border border-green-500/20"
                    >
                      <p className="text-white text-sm line-clamp-3 mb-2">{comment.text}</p>
                      <div className="flex justify-between items-center">
                        <span className="text-white/60 text-xs">
                          {new Date(comment.created_at).toLocaleDateString()}
                        </span>
                        <SentimentBadge sentiment="POSITIVE" />
                      </div>
                    </motion.div>
                  ))}
                </div>
              </ChartCard>

              <ChartCard title="Top Negative Comments">
                <div className="space-y-4">
                  {analytics?.top_negative_comments?.slice(0, 5).map((comment, index) => (
                    <motion.div
                      key={comment.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5, delay: index * 0.1 }}
                      className="p-4 bg-red-500/10 rounded-lg border border-red-500/20"
                    >
                      <p className="text-white text-sm line-clamp-3 mb-2">{comment.text}</p>
                      <div className="flex justify-between items-center">
                        <span className="text-white/60 text-xs">
                          {new Date(comment.created_at).toLocaleDateString()}
                        </span>
                        <SentimentBadge sentiment="NEGATIVE" />
                      </div>
                    </motion.div>
                  ))}
                </div>
              </ChartCard>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;