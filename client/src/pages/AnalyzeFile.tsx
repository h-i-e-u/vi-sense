import React, { useState } from "react";
import { motion } from "framer-motion";
import { FileText, Download, ChevronRight } from "lucide-react";
import { Sidebar } from "../components/Sidebar";
import { GlassCard } from "../components/GlassCard";
import { FileUploader } from "../components/FileUploader";
import { AnimatedButton } from "../components/AnimatedButton";
import { LoadingOverlay } from "../components/LoadingOverlay";
import { analysisAPI, getErrorMessage } from "../services/api";
import { AnalysisJob } from "../types";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";

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

  const exportResults = () => {
    if (!result?.results) return;

    const csvContent = [
      ["Text", "Sentiment", "Confidence"],
      ...result.results.map((r) => [r.text, r.label, r.confidence.toString()]),
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
