import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, Calendar, RefreshCw } from "lucide-react";
import { Sidebar } from "../components/Sidebar";
import { GlassCard } from "../components/GlassCard";
import { ChartCard } from "../components/ChartCard";
import { SentimentBadge } from "../components/SentimentBadge";
import { analyticsAPI, analysisAPI, historyAPI } from "../services/api";
import { AnalyticsSummary, AnalysisJob } from "../types";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const DetailAnalytics: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const [job, setJob] = useState<AnalysisJob | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!jobId) return;

      try {
        setLoading(true);
        setError(null);
        const [jobData, analyticsData] = await Promise.all([
          historyAPI.getJobById(jobId),
          analyticsAPI.getJobAnalytics(jobId),
        ]);
        setJob(jobData);
        setAnalytics(analyticsData);
        console.log(jobData)
        console.log(analyticsData)
      } catch (err) {
        console.error("Failed to fetch analytics:", err);
        setError("Failed to load analytics. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [jobId]);

  const handleRefresh = async () => {
    if (!jobId) return;

    setRefreshing(true);
    try {
      const refreshedJob = await analysisAPI.refreshAnalysis(jobId);
      setJob(refreshedJob);

      // Also refresh the analytics data
      const analyticsData = await analyticsAPI.getJobAnalytics(refreshedJob.id);
      setAnalytics(analyticsData);

      alert("Analysis refreshed successfully!");
      navigate(`/analytics/${refreshedJob.id}`, { replace: true });
    } catch (err) {
      console.error("Failed to refresh analysis:", err);
      alert("Failed to refresh analysis. Please try again.");
    } finally {
      setRefreshing(false);
    }
  };

  const getJobTypeIcon = (type: string) => {
    switch (type) {
      case "text":
        return "💬";
      case "link":
        return "🔗";
      case "file":
        return "📄";
      default:
        return "📋";
    }
  };

  const getJobTypeLabel = (type: string) => {
    switch (type) {
      case "text":
        return "Text Analysis";
      case "link":
        return "Link Analysis";
      case "file":
        return "File Analysis";
      default:
        return "Analysis";
    }
  };

  const formatDateLabel = (date: string) => {
    const d = new Date(date);
    if (Number.isNaN(d.getTime())) return date;
    return d.toLocaleDateString("vi-VN", {
      day: "2-digit",
      month: "2-digit",
    });
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

  if (error || !job || !analytics) {
    return (
      <div className="min-h-screen p-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-4 gap-6">
            <div className="lg:col-span-1">
              <Sidebar />
            </div>
            <div className="lg:col-span-3">
              <GlassCard className="p-8 text-center">
                <h3 className="text-xl font-semibold text-white mb-2">
                  {error || "Job not found"}
                </h3>
                <button
                  onClick={() => navigate("/history")}
                  className="mt-4 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
                >
                  Back to History
                </button>
              </GlassCard>
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
              <button
                onClick={() => navigate("/history")}
                className="flex items-center gap-2 text-blue-400 hover:text-blue-300 mb-4"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to History
              </button>

              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-3xl">{getJobTypeIcon(job.type)}</span>
                    <h1 className="text-3xl font-bold text-white">
                      {getJobTypeLabel(job.type)} Details
                    </h1>
                  </div>
                  <p className="text-white/60">
                    Created on {new Date(job.created_at).toLocaleDateString()}
                  </p>
                </div>

                {(job.type === "link") &&
                  job.status === "completed" && (
                    <button
                      onClick={handleRefresh}
                      disabled={refreshing}
                      className="flex items-center gap-2 px-4 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg transition-colors disabled:opacity-50"
                    >
                      <RefreshCw
                        className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`}
                      />
                      Refresh
                    </button>
                  )}
              </div>
            </motion.div>

            {/* Analytics Summary */}
            <div className="grid grid-cols-3 gap-4">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <GlassCard className="p-6 text-center">
                  <h3 className="text-white/60 text-sm mb-2">Total Comments</h3>
                  <p className="text-3xl font-bold text-white">
                    {analytics.sentiment_distribution.positive +
                      analytics.sentiment_distribution.neutral +
                      analytics.sentiment_distribution.negative}
                  </p>
                </GlassCard>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <GlassCard className="p-6 text-center">
                  <h3 className="text-white/60 text-sm mb-2">Positive</h3>
                  <p className="text-3xl font-bold text-green-400">
                    {analytics.sentiment_distribution.positive}
                  </p>
                </GlassCard>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <GlassCard className="p-6 text-center">
                  <h3 className="text-white/60 text-sm mb-2">Negative</h3>
                  <p className="text-3xl font-bold text-red-400">
                    {analytics.sentiment_distribution.negative}
                  </p>
                </GlassCard>
              </motion.div>
            </div>

            {/* Sentiment Distribution */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <GlassCard className="p-6">
                <h2 className="text-xl font-bold text-white mb-6">
                  Sentiment Distribution
                </h2>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-white">Positive</span>
                      <span className="text-green-400">
                        {analytics.sentiment_distribution.positive}
                      </span>
                    </div>
                    <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
                      <div
                        className="bg-green-500 h-full"
                        style={{
                          width: `${
                            (analytics.sentiment_distribution.positive /
                              (analytics.sentiment_distribution.positive +
                                analytics.sentiment_distribution.neutral +
                                analytics.sentiment_distribution.negative)) *
                            100
                          }%`,
                        }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-white">Neutral</span>
                      <span className="text-yellow-400">
                        {analytics.sentiment_distribution.neutral}
                      </span>
                    </div>
                    <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
                      <div
                        className="bg-yellow-500 h-full"
                        style={{
                          width: `${
                            (analytics.sentiment_distribution.neutral /
                              (analytics.sentiment_distribution.positive +
                                analytics.sentiment_distribution.neutral +
                                analytics.sentiment_distribution.negative)) *
                            100
                          }%`,
                        }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-white">Negative</span>
                      <span className="text-red-400">
                        {analytics.sentiment_distribution.negative}
                      </span>
                    </div>
                    <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
                      <div
                        className="bg-red-500 h-full"
                        style={{
                          width: `${
                            (analytics.sentiment_distribution.negative /
                              (analytics.sentiment_distribution.positive +
                                analytics.sentiment_distribution.neutral +
                                analytics.sentiment_distribution.negative)) *
                            100
                          }%`,
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              </GlassCard>
            </motion.div>

            {/* Trend Data for Link/File */}
            {(job.type === "link" || job.type === "file") &&
              analytics.trend_data.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                >
                  <ChartCard title="Sentiment Trend (Last 7 Days)">
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={analytics.trend_data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis
                          dataKey="date"
                          stroke="#9CA3AF"
                          fontSize={12}
                          tickFormatter={formatDateLabel}
                          interval={0}
                          angle={-35}
                          textAnchor="end"
                        />
                        <YAxis stroke="#9CA3AF" fontSize={12} />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: "rgba(0, 0, 0, 0.8)",
                            border: "1px solid rgba(255, 255, 255, 0.2)",
                            borderRadius: "8px",
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
                  </ChartCard>{" "}
                </motion.div>
              )}

            {/* Top Keywords */}
            {analytics.top_keywords.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
              >
                <GlassCard className="p-6">
                  <h2 className="text-xl font-bold text-white mb-6">
                    Top Keywords
                  </h2>
                  <div className="flex flex-wrap gap-2">
                    {analytics.top_keywords.map((keyword, index) => (
                      <div
                        key={index}
                        className="px-4 py-2 bg-blue-500/20 rounded-full border border-blue-500/50"
                      >
                        <span className="text-blue-400">
                          {keyword.word}
                          <span className="ml-2 text-blue-500/60">
                            ({keyword.count})
                          </span>
                        </span>
                      </div>
                    ))}
                  </div>
                </GlassCard>
              </motion.div>
            )}

            {/* Top Comments */}
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Positive Comments */}
              {analytics.top_positive_comments.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.7 }}
                >
                  <GlassCard className="p-6">
                    <h3 className="text-lg font-bold text-green-400 mb-4">
                      Top Positive Comments
                    </h3>
                    <div className="space-y-3">
                      {analytics.top_positive_comments.map((comment) => (
                        <div
                          key={comment.id}
                          className="p-4 bg-slate-800/50 rounded-lg"
                        >
                          <p className="text-white/80 text-sm mb-2">
                            {comment.text}
                          </p>
                          <div className="flex justify-between items-center">
                            <span className="text-green-400 text-xs">
                              Confidence:{" "}
                              {(comment.sentiment.confidence * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </GlassCard>
                </motion.div>
              )}

              {/* Negative Comments */}
              {analytics.top_negative_comments.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.8 }}
                >
                  <GlassCard className="p-6">
                    <h3 className="text-lg font-bold text-red-400 mb-4">
                      Top Negative Comments
                    </h3>
                    <div className="space-y-3">
                      {analytics.top_negative_comments.map((comment) => (
                        <div
                          key={comment.id}
                          className="p-4 bg-slate-800/50 rounded-lg"
                        >
                          <p className="text-white/80 text-sm mb-2">
                            {comment.text}
                          </p>
                          <div className="flex justify-between items-center">
                            <span className="text-red-400 text-xs">
                              Confidence:{" "}
                              {(comment.sentiment.confidence * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </GlassCard>
                </motion.div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DetailAnalytics;
