import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  BarChart3,
  FileText,
  History,
  Link as LinkIcon,
  MessageSquare,
  TrendingUp,
  LogOut,
  TableProperties,
} from "lucide-react";
import { cn } from "../utils/cn";
import toast from "react-hot-toast";

interface SidebarProps {
  className?: string;
}

const menuItems = [
  {
    path: "/dashboard",
    label: "Dashboard",
    icon: BarChart3,
  },
  {
    path: "/analyze/text",
    label: "Analyze Text",
    icon: MessageSquare,
  },
  {
    path: "/analyze/link",
    label: "Analyze Link",
    icon: LinkIcon,
  },
  {
    path: "/analyze/file",
    label: "Analyze File",
    icon: FileText,
  },
  {
    path: "/history",
    label: "History",
    icon: History,
  },
  {
    path: "/analytics",
    label: "Analytics",
    icon: TrendingUp,
  },
  {
    path: "/sentences",
    label: "All Sentences",
    icon: TableProperties,
  },
];

export const Sidebar: React.FC<SidebarProps> = ({ className }) => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleSignOut = () => {
    localStorage.removeItem("access_token");
    toast.success("Signed out successfully");
    navigate("/login");
  };

  return (
    <div
  className={cn(
    // h-screen: Khóa sidebar bằng chiều cao màn hình
    // sticky top-0: Ghim sidebar cố định tại chỗ khi cuộn trang
    "w-64 glass rounded-xl p-6 flex flex-col h-screen sticky top-0 justify-between overflow-hidden",
    className,
  )}
>
  {/* Phần trên: Logo và Menu */}
  <div className="flex-1 flex flex-col min-h-0">
    <div className="mb-8 shrink-0">
      <h2 className="text-2xl font-bold text-white mb-2">Vi-Sense</h2>
      <p className="text-white/60 text-sm">Sentiment Analysis</p>
    </div>

    {/* Chỉ có phần menu này được phép cuộn nếu màn hình quá thấp hoặc quá nhiều mục */}
    <nav className="space-y-2 overflow-y-auto flex-1 pr-1 custom-scrollbar">
      {menuItems.map((item) => {
        const isActive = location.pathname === item.path;
        const Icon = item.icon;

        return (
          <Link key={item.path} to={item.path}>
            <motion.div
              className={cn(
                "flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-300",
                isActive
                  ? "bg-purple-500/20 text-purple-300 border border-purple-500/30"
                  : "text-white/70 hover:text-white hover:bg-white/10",
              )}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Icon className="h-5 w-5" />
              <span className="font-medium">{item.label}</span>
            </motion.div>
          </Link>
        );
      })}
    </nav>
  </div>

  {/* Phần dưới: Luôn nằm cố định ở đáy Sidebar, không bao giờ bị đẩy xuống dưới */}
  <div className="shrink-0 mt-6 pt-6 border-t border-white/10 space-y-4">
    <button
      onClick={handleSignOut}
      className="w-full flex items-center justify-center space-x-2 px-4 py-3 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-300 hover:text-red-200 border border-red-500/30 transition-all duration-300"
    >
      <LogOut className="h-5 w-5" />
      <span className="font-medium">Sign Out</span>
    </button>
    
    <div className="text-white/60 text-xs text-center leading-relaxed">
      <p>© 2026 Vi-Sense</p>
      <p>Vietnamese Sentiment Analysis</p>
      <p className="font-medium">D.C Hieu</p>
    </div>
  </div>
</div>

  );
};
