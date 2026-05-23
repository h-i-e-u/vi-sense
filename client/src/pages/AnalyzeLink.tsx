import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ChevronRight, Link as LinkIcon } from "lucide-react";
import { Sidebar } from "../components/Sidebar";
import { GlassCard } from "../components/GlassCard";
import { SentimentBadge } from "../components/SentimentBadge";
import { AnimatedButton } from "../components/AnimatedButton";
import { LoadingOverlay } from "../components/LoadingOverlay";
import { analysisAPI, getErrorMessage, historyAPI } from "../services/api";
import { AnalysisJob } from "../types";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";

const AnalyzeLink: React.FC = () => {
  const [url, setUrl] = useState("");
  const [platform, setPlatform] = useState<"youtube" | "shopee" | "tiki">(
    "youtube",
  );
  const [result, setResult] = useState<AnalysisJob | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [existingJob, setExistingJob] = useState<AnalysisJob | null>(null);
  const navigate = useNavigate();

  const platformExamples = {
    youtube: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    shopee: "https://shopee.vn/product/123456789/987654321",
    tiki: "https://tiki.vn/product-p123456.html",
  };

  const handleAnalyze = async () => {
    if (!url.trim()) {
      toast.error("Please enter a URL to analyze");
      return;
    }

    setIsAnalyzing(true);
    try {
      const response = await analysisAPI.analyzeLink({ url, type: platform });
      setResult(response);
      toast.success("Analysis completed!");
    } catch (error: any) {
      toast.error(getErrorMessage(error));
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getPlatformColor = (plat: string) => {
    switch (plat) {
      case "youtube":
        return "text-red-400";
      case "shopee":
        return "text-orange-400";
      case "tiki":
        return "text-blue-400";
      default:
        return "text-white";
    }
  };

  const checkExistingLink = async () => {
    if (!url.trim()) {
      setExistingJob(null);
      return;
    }
    try {
      const history = await historyAPI.getHistory();
      const found = history.find(
        (job) =>
          job.type === "link" &&
          job.metadata?.source_url === url &&
          job.status === "completed",
      );
      setExistingJob(found || null);
    } catch (error) {
      console.error("Không thể kiểm tra history", error);
    }
  };
  useEffect(() => {
    checkExistingLink();
  }, [url]);

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
                Analyze Link
              </h1>
              <p className="text-white/60">
                Extract and analyze sentiment from YouTube, Shopee, or Tiki
              </p>
            </motion.div>

            {/* Platform Selection */}
            <GlassCard className="p-6">
              <h3 className="text-xl font-semibold text-white mb-4">
                Select Platform
              </h3>
              <div className="grid md:grid-cols-3 gap-4 mb-6">
                {[
                  { id: "youtube", name: "YouTube", icon: "📺" },
                  { id: "shopee", name: "Shopee", icon: "🛒" },
                  { id: "tiki", name: "Tiki", icon: "📦" },
                ].map((plat) => (
                  <button
                    key={plat.id}
                    onClick={() => setPlatform(plat.id as any)}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      platform === plat.id
                        ? "border-purple-400 bg-purple-500/20"
                        : "border-white/20 hover:border-white/40"
                    }`}
                  >
                    <div className="text-2xl mb-2">{plat.icon}</div>
                    <div className={`font-medium ${getPlatformColor(plat.id)}`}>
                      {plat.name}
                    </div>
                  </button>
                ))}
              </div>

              {/* URL Input */}
              <div className="mb-4">
                <label className="block text-white/80 text-sm font-medium mb-2">
                  {platform.charAt(0).toUpperCase() + platform.slice(1)} URL
                </label>
                <div className="relative">
                  <LinkIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-white/40" />
                  <input
                    type="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder={platformExamples[platform]}
                    className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                <p className="text-white/60 text-xs mt-2">
                  Example: {platformExamples[platform]}
                </p>
              </div>
              {existingJob && (
                <div className="mb-4 rounded-xl bg-yellow-500/10 border border-yellow-400/30 p-4 text-yellow-100">
                  Link này đã được phân tích trước đó.
                  <div className="mt-3 flex flex-wrap gap-2">
                    <AnimatedButton
                      onClick={() => navigate(`/analytics/${existingJob.id}`)}
                      className="px-4 py-2 bg-blue-500 text-white rounded-lg"
                    >
                      Detail
                      <ChevronRight className="h-4 w-4" />

                    </AnimatedButton>
                  </div>
                </div>
              )}

              <AnimatedButton
                onClick={handleAnalyze}
                isLoading={isAnalyzing}
                className="w-full"
              >
                {isAnalyzing
                  ? "Analyzing..."
                  : `Analyze ${platform.charAt(0).toUpperCase() + platform.slice(1)}`}
              </AnimatedButton>
            </GlassCard>

            {/* Results */}
            {result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <GlassCard className="p-6">
                  <div className="mt-6 mb-10 flex flex-auto gap-3 items-center justify-between">
                  <h3 className="text-xl font-semibold text-white mb-4">
                    Analysis Results
                  </h3>
                    <AnimatedButton
                      onClick={() => navigate(`/analytics/${result.id}`)}
                      className=""
                      >
                      Detail
                        <ChevronRight className="h-4 w-4" />
                    </AnimatedButton>
                  </div>
                  {/* Summary Stats */}
                  <div className="grid md:grid-cols-4 gap-4 mb-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-white">
                        {result.metadata?.total_comments || 0}
                      </div>
                      <div className="text-white/60 text-sm">
                        Total Comments
                      </div>
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

                  {/* Comments List */}
                  <div className="space-y-4">
                    <h4 className="text-lg font-medium text-white">
                      Recent Comments
                    </h4>
                    {result.results?.slice(0, 10).map((sentiment, index) => (
                      <div
                        key={index}
                        className="flex items-start space-x-3 p-4 bg-white/5 rounded-lg"
                      >
                        <div className="flex-1">
                          <p className="text-white text-sm line-clamp-3">
                            {sentiment.text}
                          </p>
                        </div>
                        <SentimentBadge
                          sentiment={sentiment.label}
                          confidence={sentiment.confidence}
                        />
                      </div>
                    ))}
                  </div>
                </GlassCard>
              </motion.div>
            )}

            <LoadingOverlay
              isLoading={isAnalyzing}
              message={`Analyzing ${platform} content...`}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyzeLink;
