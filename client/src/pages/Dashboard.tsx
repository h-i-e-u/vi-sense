import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BarChart3, MessageSquare, FileText, TrendingUp } from "lucide-react";
import { Sidebar } from "../components/Sidebar";
import { GlassCard } from "../components/GlassCard";
import { ChartCard } from "../components/ChartCard";
import { analyticsAPI } from "../services/api";
import { UserAnalyticsSummary } from "../types";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

const Dashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<UserAnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const dailyData = analytics?.daily_analysis_counts || [];

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const data = await analyticsAPI.getSummary();
        setAnalytics(data);
      } catch (error) {
        console.error("Failed to fetch analytics:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  const pieData = analytics
    ? [
        {
          name: "Positive",
          value: analytics.sentiment_distribution.positive,
          color: "#10B981",
        },
        {
          name: "Neutral",
          value: analytics.sentiment_distribution.neutral,
          color: "#F59E0B",
        },
        {
          name: "Negative",
          value: analytics.sentiment_distribution.negative,
          color: "#EF4444",
        },
      ]
    : [];

  const stats = [
    {
      title: "Total Analyses",
      value: analytics?.total_analyses || 0,
      icon: BarChart3,
      color: "text-blue-400",
    },
    {
      title: "Text Analyses",
      value: analytics?.text_analyses || 0,
      icon: MessageSquare,
      color: "text-green-400",
    },
    {
      title: "File Analyses",
      value: analytics?.file_analyses || 0,
      icon: FileText,
      color: "text-purple-400",
    },
    {
      title: "Link Analyses",
      value: analytics?.link_analyses || 0,
      icon: TrendingUp,
      color: "text-orange-400",
    },
  ];

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
              <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
              <p className="text-white/60">
                Welcome to Vi-Sense sentiment analysis platform
              </p>
            </motion.div>

            {/* Stats Cards */}
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {stats.map((stat, index) => (
                <motion.div
                  key={stat.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                >
                  <GlassCard className="p-6 text-center">
                    <stat.icon
                      className={`h-8 w-8 ${stat.color} mx-auto mb-3`}
                    />
                    <h3 className="text-2xl font-bold text-white mb-1">
                      {stat.value}
                    </h3>
                    <p className="text-white/60 text-sm">{stat.title}</p>
                  </GlassCard>
                </motion.div>
              ))}
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
                      label={({ name, percent }) =>
                        `${name} ${(percent * 100).toFixed(0)}%`
                      }
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </ChartCard>

              {/*  Chart */}
              <ChartCard title="Daily Analyses">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={dailyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis
                      dataKey="date"
                      stroke="#9CA3AF"
                      fontSize={12}
                      tickFormatter={(date) =>
                        new Date(date).toLocaleDateString("vi-VN", {
                          day: "2-digit",
                          month: "2-digit",
                        })
                      }
                      interval={0}
                      angle={-30}
                      textAnchor="end"
                    />
                    <YAxis stroke="#9CA3AF" fontSize={12} />
                    <Tooltip
                      labelFormatter={(label) =>
                        new Date(label).toLocaleDateString("vi-VN", {
                          weekday: "short",
                          day: "2-digit",
                          month: "2-digit",
                        })
                      }
                      formatter={(value) => [value, "Analyses"]}
                      contentStyle={{
                        backgroundColor: "rgba(0, 0, 0, 0.8)",
                        border: "1px solid rgba(255, 255, 255, 0.2)",
                        borderRadius: "8px",
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="count"
                      stroke="#38BDF8"
                      strokeWidth={2}
                      name="Daily Analyses"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>

          
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
