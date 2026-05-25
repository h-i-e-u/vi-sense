import React, { useState, useEffect } from 'react';
import { 
  Search, ChevronLeft, ChevronRight, 
  MessageSquare, Link as LinkIcon, FileText, Copy, Check 
} from 'lucide-react';
import { SentenceItem } from '../types';
import { sentencesAPI } from '../services/api';
import { AnimatedButton } from '../components/AnimatedButton';
import { Sidebar } from '../components/Sidebar';
import { GlassCard } from '../components/GlassCard';

const AllSentences: React.FC = () => {
  const [sentences, setSentences] = useState<SentenceItem[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [totalPages, setTotalPages] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);

  const [page, setPage] = useState<number>(1);
  const [limit] = useState<number>(10);
  const [search, setSearch] = useState<string>('');
  const [jobType, setJobType] = useState<string>('');
  const [label, setLabel] = useState<string>('');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const fetchSentences = async (): Promise<void> => {
    setLoading(true);
    try {
      const data = await sentencesAPI.getProcessedSentences({
        page,
        limit,
        ...(search && { search }),
        ...(jobType && { job_type: jobType }),
        ...(label && { label })
      });
      
      setSentences(data.items || []);
      setTotal(data.total || 0);
      setTotalPages(data.total_pages || 0);
    } catch (error) {
      console.error("Lỗi khi tải danh sách câu:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSentences();
  }, [page, jobType, label]);

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      setPage(1);
      fetchSentences();
    }, 500);

    return () => clearTimeout(delayDebounceFn);
  }, [search]);

  const handleCopy = (text: string, id: string): void => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const renderSourceIcon = (type: string) => {
    switch (type) {
      case 'text': return <MessageSquare className="w-4 h-4 text-blue-500" />;
      case 'link': return <LinkIcon className="w-4 h-4 text-green-500" />;
      case 'file': return <FileText className="w-4 h-4 text-purple-500" />;
      default: return null;
    }
  };

  const renderLabelBadge = (sentimentLabel: string) => {
    const styles: Record<string, string> = {
      POSITIVE: 'bg-green-100 text-green-800 border-green-200',
      NEGATIVE: 'bg-red-100 text-red-800 border-red-200',
      NEUTRAL: 'bg-gray-100 text-gray-800 border-gray-200'
    };
    return (
      <span className={`px-2.5 py-1 text-xs font-semibold rounded-full border ${styles[sentimentLabel] || styles.NEUTRAL}`}>
        {sentimentLabel}
      </span>
    );
  };

  return (    
    <div className="p-6 max-w-7xl mx-auto space-y-6">

      {/* Header */}
      <GlassCard>
        <h1 className="text-2xl font-bold text-gray-300">All Processed Sentences</h1>
        <p className="text-sm text-gray-500 mt-1">Xem và quản lý tất cả các câu đã được phân tích trên hệ thống.</p>
      </GlassCard>

      {/* Filters */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 flex flex-col md:flex-row gap-4 justify-between items-center">
        <div className="relative w-full md:w-96">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search text..."
            className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            value={search}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearch(e.target.value)}
          />
        </div>

        <div className="flex flex-wrap gap-3 w-full md:w-auto justify-end">
          <select
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={jobType}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => { setJobType(e.target.value); setPage(1); }}
          >
            <option value="">All Type</option>
            <option value="text">Text Input</option>
            <option value="link">Web Link</option>
            <option value="file">Uploaded File</option>
          </select>

          <select
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={label}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => { setLabel(e.target.value); setPage(1); }}
          >
            <option value="">All Sentiment</option>
            <option value="POSITIVE">Positive</option>
            <option value="NEGATIVE">Negative</option>
            <option value="NEUTRAL">Neutral</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200 text-xs font-semibold text-gray-600 uppercase tracking-wider">
                <th className="px-6 py-3 w-16 text-center">Source</th>
                <th className="px-6 py-3">text</th>
                <th className="px-6 py-3 w-32">result</th>
                <th className="px-6 py-3 w-28">confidence</th>
                <th className="px-6 py-3 w-40">create date</th>
                <th className="px-6 py-3 w-16 text-center">Copy</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 text-sm text-gray-700">
              {loading ? (
                [...Array(5)].map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan={6} className="px-6 py-4 bg-gray-50/50 h-12"></td>
                  </tr>
                ))
              ) : sentences.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-gray-400">
                    No matching data was found.
                  </td>
                </tr>
              ) : (
                sentences.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 text-center">
                      <div className="flex justify-center">{renderSourceIcon(item.job?.type)}</div>
                    </td>
                    <td className="px-6 py-4 font-medium text-gray-900 max-w-md break-words">
                      {item.text}
                    </td>
                    <td className="px-6 py-4">
                      {renderLabelBadge(item.label)}
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-gray-500">
                      {(item.confidence * 100).toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 text-xs text-gray-500">
                      {new Date(item.created_at).toLocaleString('vi-VN')}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <button 
                        onClick={() => handleCopy(item.text, item.id)}
                        className="text-gray-400 hover:text-blue-600 transition-colors focus:outline-none"
                      >
                        {copiedId === item.id ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination using AnimatedButton */}
        <div className="bg-white px-6 py-4 border-t border-gray-200 flex items-center justify-between">
          <div className="text-xs text-gray-500">
            Page <span className="font-semibold text-gray-700">{page}</span> out of <span className="font-semibold text-gray-700">{totalPages}</span> page of ({total} result)
          </div>
          <div className="flex items-center space-x-2">
            {/* backward */}
            <AnimatedButton
              variant="primary"
              size="md"
              onClick={() => setPage(p => Math.max(p - 1, 1))}
              disabled={page === 1 || loading}
            >
              <ChevronLeft className="w-4 h-4" />
            </AnimatedButton>

            {/* forward */}
            <AnimatedButton
              variant="primary"
              size="md"
              onClick={() => setPage(p => Math.min(p + 1, totalPages))}
              disabled={page === totalPages || loading}
            >
              <ChevronRight className="w-4 h-4" />
            </AnimatedButton>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AllSentences;
