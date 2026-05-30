import React, { useState } from "react";
import { motion } from "framer-motion";
import { FileText, Download, ChevronRight, Tags } from "lucide-react";
import { Sidebar } from "../components/Sidebar";
import { GlassCard } from "../components/GlassCard";
import { FileUploader } from "../components/FileUploader";
import { AnimatedButton } from "../components/AnimatedButton";
import { LoadingOverlay } from "../components/LoadingOverlay";
import { analysisAPI, getErrorMessage } from "../services/api";
import { AnalysisJob } from "../types";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";
import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const AnalyzeFile: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<AnalysisJob | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const navigate = useNavigate();

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      toast.error("Please select a file to analyze");
      return;
    }

    setIsAnalyzing(true);
    try {
      const response = await analysisAPI.analyzeFile({ file: selectedFile });
      setResult(response);
      toast.success("File analysis completed!");
    } catch (error: any) {
      toast.error(getErrorMessage(error));
    } finally {
      setIsAnalyzing(false);
    }
  };

  const absaChartData = result?.metadata?.absa_summary
    ? Object.entries(result.metadata.absa_summary.aspect_counts)
        .map(([aspect, count]) => ({
          aspect,
          count,
          ...(result.metadata?.absa_summary?.aspect_sentiments[aspect] ?? {}),
        }))
        .sort((a, b) => b.count - a.count)
    : [];

  const absaSentiments = result?.metadata?.absa_summary
    ? Object.keys(result.metadata.absa_summary.sentiment_counts)
    : [];

  const absaSentimentColors: Record<string, string> = {
    Positive: "#22C55E",
    POSITIVE: "#22C55E",
    Negative: "#EF4444",
    NEGATIVE: "#EF4444",
    Neutral: "#F59E0B",
    NEUTRAL: "#F59E0B",
  };

  const exportResults = () => {
    if (!result?.results) return;

    const absaByIndex = new Map(
      result.metadata?.absa_results?.map((item) => [item.index, item.aspects]) ??
        [],
    );
    const csvContent = [
      ["Text", "Sentiment", "Confidence", "ABSA"],
      ...result.results.map((r, index) => [
        r.text,
        r.label,
        r.confidence.toString(),
        (absaByIndex.get(index) ?? [])
          .map((item) => `${item.aspect}:${item.sentiment}`)
          .join("; "),
      ]),
    ]
      .map((row) => row.map((cell) => `"${cell}"`).join(","))
      .join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "sentiment_analysis_results.csv";
    a.click();
    window.URL.revokeObjectURL(url);
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
              <h1 className="text-3xl font-bold text-white mb-2">
                Analyze File
              </h1>
              <p className="text-white/60">
                Upload CSV, XLSX, or TXT files for batch sentiment analysis
              </p>
            </motion.div>

            {/* File Upload */}
            <GlassCard className="p-6">
              <FileUploader
                onFileSelect={handleFileSelect}
                acceptedTypes=".csv,.xlsx,.txt"
                maxSize={10}
              />
              <p className="text-sm text-white/60 mt-3">
                {" "}
                Accepted: CSV/XLSX with one text column (date column optional).
                TXT: each line either "YYYY-MM-DD[TAB]text" or plain text.{" "}
              </p>

              {selectedFile && (
                <div className="mt-6">
                  <AnimatedButton
                    onClick={handleAnalyze}
                    isLoading={isAnalyzing}
                    className="w-full"
                  >
                    {isAnalyzing ? "Analyzing..." : "Analyze File"}
                  </AnimatedButton>
                </div>
              )}
            </GlassCard>

            {/* Results */}
            {result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <GlassCard className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-semibold text-white">
                      Analysis Results
                    </h3>
                    <div className="flex space-x-2">
                      <AnimatedButton onClick={exportResults} size="sm">
                        <Download className="h-4 w-4 mr-2" />
                        Export CSV
                      </AnimatedButton>
                      <AnimatedButton
                        size="sm"
                        onClick={() => navigate(`/analytics/${result.id}`)}
                        className=""
                      >
                        Detail
                        <ChevronRight className="h-4 w-4" />
                      </AnimatedButton>
                    </div>
                  </div>

                  {/* Summary Stats */}
                  <div className="grid md:grid-cols-4 gap-4 mb-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-white">
                        {result.metadata?.total_comments || 0}
                      </div>
                      <div className="text-white/60 text-sm">Total Texts</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-400">
                        {result.metadata?.positive_ratio
                          ? Math.round(result.metadata.positive_ratio * 100)
                          : 0}
                        %
                      </div>
                      <div className="text-white/60 text-sm">Positive</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-yellow-400">
                        {result.metadata?.neutral_ratio
                          ? Math.round(result.metadata.neutral_ratio * 100)
                          : 0}
                        %
                      </div>
                      <div className="text-white/60 text-sm">Neutral</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-400">
                        {result.metadata?.negative_ratio
                          ? Math.round(result.metadata.negative_ratio * 100)
                          : 0}
                        %
                      </div>
                      <div className="text-white/60 text-sm">Negative</div>
                    </div>
                  </div>

                  {result.metadata?.absa_enabled && result.metadata.absa_summary && (
                    <div className="mb-6 rounded-lg bg-white/5 p-4">
                      <div className="flex items-center justify-between gap-3 mb-3">
                        <div className="flex items-center gap-2">
                          <Tags className="h-5 w-5 text-cyan-300" />
                          <h4 className="text-lg font-medium text-white">
                            ABSA Summary
                          </h4>
                        </div>
                        <div className="text-sm text-white/60">
                          {
                            result.metadata.absa_summary
                              .total_aspect_mentions
                          }{" "}
                          mentions
                        </div>
                      </div>
                      <div className="mb-3 flex flex-wrap gap-3">
                        {absaSentiments.map((sentiment) => (
                          <div
                            key={sentiment}
                            className="flex items-center gap-2 text-xs text-white/70"
                          >
                            <span
                              className="h-2.5 w-2.5 rounded-full"
                              style={{
                                backgroundColor:
                                  absaSentimentColors[sentiment] ?? "#38BDF8",
                              }}
                            />
                            {sentiment}
                          </div>
                        ))}
                      </div>
                      <div className="h-72">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart
                            data={absaChartData}
                            layout="vertical"
                            margin={{
                              top: 8,
                              right: 32,
                              bottom: 8,
                              left: 16,
                            }}
                          >
                            <CartesianGrid
                              strokeDasharray="3 3"
                              stroke="rgba(255,255,255,0.12)"
                              horizontal={false}
                            />
                            <XAxis
                              type="number"
                              allowDecimals={false}
                              stroke="#9CA3AF"
                              fontSize={12}
                            />
                            <YAxis
                              type="category"
                              dataKey="aspect"
                              width={96}
                              stroke="#D1D5DB"
                              fontSize={12}
                            />
                            <Tooltip
                              cursor={{ fill: "rgba(255,255,255,0.06)" }}
                              contentStyle={{
                                backgroundColor: "rgba(12, 18, 32, 0.96)",
                                border: "1px solid rgba(255,255,255,0.16)",
                                borderRadius: "8px",
                                color: "#FFFFFF",
                              }}
                              formatter={(value, name) => [value, name]}
                            />
                            {absaSentiments.map((sentiment, index) => (
                              <Bar
                                key={sentiment}
                                dataKey={sentiment}
                                stackId="sentiment"
                                fill={
                                  absaSentimentColors[sentiment] ?? "#38BDF8"
                                }
                                radius={
                                  index === absaSentiments.length - 1
                                    ? [0, 6, 6, 0]
                                    : [0, 0, 0, 0]
                                }
                                barSize={18}
                              >
                                {index === absaSentiments.length - 1 && (
                                  <LabelList
                                    dataKey="count"
                                    position="right"
                                    fill="#E5E7EB"
                                    fontSize={12}
                                  />
                                )}
                              </Bar>
                            ))}
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  )}

                  {result.metadata?.absa_error && (
                    <div className="mb-6 rounded-lg border border-yellow-400/30 bg-yellow-400/10 p-4 text-sm text-yellow-100">
                      ABSA model chưa sẵn sàng: {result.metadata.absa_error}
                    </div>
                  )}

                  {/* Sample Results */}
                  <div className="space-y-4">
                    <h4 className="text-lg font-medium text-white">
                      Sample Results (First 10)
                    </h4>
                    {result.results?.slice(0, 10).map((sentiment, index) => (
                      <div
                        key={index}
                        className="flex items-start space-x-3 p-4 bg-white/5 rounded-lg"
                      >
                        <FileText className="h-5 w-5 text-white/40 mt-1" />
                        <div className="flex-1">
                          <p className="text-white text-sm line-clamp-2">
                            {sentiment.text}
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="text-white/60 text-xs">
                            {Math.round(sentiment.confidence * 100)}%
                          </div>
                          <div
                            className={`text-xs font-medium ${
                              sentiment.label === "POSITIVE"
                                ? "text-green-400"
                                : sentiment.label === "NEGATIVE"
                                  ? "text-red-400"
                                  : "text-yellow-400"
                            }`}
                          >
                            {sentiment.label}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </GlassCard>
              </motion.div>
            )}

            <LoadingOverlay
              isLoading={isAnalyzing}
              message="Analyzing file content..."
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyzeFile;
