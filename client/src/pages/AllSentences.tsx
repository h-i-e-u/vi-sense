import React, { useState, useEffect } from "react";
import {
  Search,
  ChevronLeft,
  ChevronRight,
  MessageSquare,
  Link as LinkIcon,
  FileText,
  Copy,
  Check,
} from "lucide-react";
import { SentenceItem } from "../types";
import { sentencesAPI } from "../services/api";
import { AnimatedButton } from "../components/AnimatedButton";
import { GlassCard } from "../components/GlassCard";
import { useNavigate } from "react-router-dom";
import { SentimentBadge } from "../components/SentimentBadge";
import toast from "react-hot-toast";

const AllSentences: React.FC = () => {
  const [sentences, setSentences] = useState<SentenceItem[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [totalPages, setTotalPages] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);

  const [page, setPage] = useState<number>(1);
  const [prevPage, setPrevPage] = useState<number>(1);
  const [limit] = useState<number>(10);

  // search là text send to api, searchInput là text user đang gõ
  const [search, setSearch] = useState<string>("");
  const [searchInput, setSearchInput] = useState<string>("");

  const [jobType, setJobType] = useState<string>("");
  const [label, setLabel] = useState<string>("");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const navigate = useNavigate();

  const fetchSentences = async (): Promise<void> => {
    setLoading(true);
    try {
      const data = await sentencesAPI.getProcessedSentences({
        page,
        limit,
        ...(search && { search }),
        ...(jobType && { job_type: jobType }),
        ...(label && { label }),
      });

      setSentences(data.items || []);
      setTotal(data.total || 0);
      setTotalPages(data.total_pages || 0);
      setPrevPage(page);
    } catch (error) {
      console.error("Lỗi khi tải danh sách câu:", error);
      toast.error("Network or server error: " + error);
      setPage(prevPage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSentences();
  }, [page, jobType, label, search]);

  const handleTriggerSearch = () => {
    setPage(1);
    setSearch(searchInput);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleTriggerSearch();
    }
  };

  const handleCopy = (text: string, id: string): void => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const renderSourceIcon = (type: string) => {
    switch (type) {
      case "text":
        return <MessageSquare className="w-4 h-4 text-blue-500" />;
      case "link":
        return <LinkIcon className="w-4 h-4 text-green-500" />;
      case "file":
        return <FileText className="w-4 h-4 text-purple-500" />;
      default:
        return null;
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <GlassCard className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-300">
            All Processed Sentences
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Xem và quản lý tất cả các câu đã được phân tích trên hệ thống.
          </p>
        </div>

        <div className="flex flex-col gap-2">
          <AnimatedButton
            onClick={() => navigate("/dashboard")}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-white rounded-lg transition-colors text-sm whitespace-nowrap"
          >
            Dashboard
            <ChevronRight className="h-4 w-4" />
          </AnimatedButton>
        </div>
      </GlassCard>

      {/* Filters */}
      <GlassCard className="p-4 flex flex-col md:flex-row gap-4 justify-between items-center">
        <div className="relative w-full md:w-96">
          <button type="button" onClick={handleTriggerSearch}>
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-200" />
          </button>
          <input
            type="text"
            placeholder="Search text..."
            className="w-full pl-9 py-2 bg-transparent border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white text-sm focus:bg-purple-950/80  focus:border-purple-400/40"
            value={searchInput}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setSearchInput(e.target.value)
            }
            onKeyDown={handleKeyDown}
          />
        </div>

        <div className="flex flex-wrap gap-3 w-full md:w-auto justify-end text-gray-200">
          <select
            className="px-3 py-2 bg-purple-950/80 border border-purple-400/40 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-white cursor-pointer"
            value={jobType}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
              setJobType(e.target.value);
              setPage(1);
            }}
          >
            <option value="" className="bg-purple-950 text-white">
              All Type
            </option>
            <option value="text" className="bg-purple-950 text-white">
              Text Input
            </option>
            <option value="link" className="bg-purple-950 text-white">
              Web Link
            </option>
            <option value="file" className="bg-purple-950 text-white">
              Uploaded File
            </option>
          </select>

          <select
            className="px-3 py-2 bg-purple-950/80 border border-purple-400/40 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-white cursor-pointer"
            value={label}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
              setLabel(e.target.value);
              setPage(1);
            }}
          >
            <option value="" className="bg-purple-950 text-white">
              All Sentiment
            </option>
            <option value="POSITIVE" className="bg-purple-950 text-white">
              Positive
            </option>
            <option value="NEGATIVE" className="bg-purple-950 text-white">
              Negative
            </option>
            <option value="NEUTRAL" className="bg-purple-950 text-white">
              Neutral
            </option>
          </select>
        </div>
      </GlassCard>

      {/* Table */}
      <GlassCard>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse ">
            <thead>
              <tr className="bg-gray-200/50 border-b rounded-md border-gray-200 text-xs font-semibold text-gray-900 uppercase tracking-wider">
                <th className="px-6 py-3 w-16 text-center">Source</th>
                <th className="px-6 py-3">text</th>
                <th className="px-6 py-3 w-32">result</th>
                <th className="px-6 py-3 w-28">confidence</th>
                <th className="px-6 py-3 w-40">create date</th>
                <th className="px-6 py-3 w-16 text-center">Copy</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 text-sm text-gray-200">
              {loading ? (
                [...Array(5)].map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan={6} className="px-6 py-4 bg-inherit h-12"></td>
                  </tr>
                ))
              ) : sentences.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-gray-200">
                    No matching data was found.
                  </td>
                </tr>
              ) : (
                sentences.map((item) => (
                  <tr
                    key={item.id}
                    className="hover:bg-gray-50/25 transition-colors"
                  >
                    <td className="px-6 py-4 text-center">
                      <div className="flex justify-center">
                        {renderSourceIcon(item.job?.type)}
                      </div>
                    </td>
                    <td className="px-6 py-4 font-medium text-gray-200 max-w-md break-words">
                      {item.text}
                    </td>
                    <td className="px-6 py-4">
                      <SentimentBadge sentiment={item.label} />
                    </td>
                    <td className="px-6 py-4 font-mono text-sm text-gray-200">
                      {(item.confidence * 100).toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-200">
                      {new Date(item.created_at).toLocaleString("vi-VN")}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <button
                        onClick={() => handleCopy(item.text, item.id)}
                        className="text-gray-400 hover:text-blue-900 transition-colors focus:outline-none"
                      >
                        {copiedId === item.id ? (
                          <Check className="w-4 h-4 text-green-500" />
                        ) : (
                          <Copy className="w-4 h-4" />
                        )}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination using AnimatedButton */}
        <div className="bg-gray-200/50 px-6 py-4 border-t border-gray-200 flex items-center justify-between">
          <div className="text-sm text-gray-700">
            Page <span className="font-semibold text-gray-900">{page}</span> out
            of <span className="font-semibold text-gray-900">{totalPages}</span>{" "}
            page of ({total} result)
          </div>
          <div className="flex items-center space-x-2">
            {/* backward */}
            <AnimatedButton
              variant="primary"
              size="md"
              onClick={() => setPage((p) => Math.max(p - 1, 1))}
              disabled={page === 1 || loading}
            >
              <ChevronLeft className="w-4 h-4" />
            </AnimatedButton>

            {/* forward */}
            <AnimatedButton
              variant="primary"
              size="md"
              onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
              disabled={page === totalPages || loading}
            >
              <ChevronRight className="w-4 h-4" />
            </AnimatedButton>
          </div>
        </div>
      </GlassCard>
    </div>
  );
};

export default AllSentences;
