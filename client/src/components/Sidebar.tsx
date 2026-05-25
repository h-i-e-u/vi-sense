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
    path: "/all-sentences",
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
        "w-64 glass rounded-xl p-6 flex flex-col h-[calc(100vh+2rem)]",
        className,
      )}
    >
      <div>
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-2">Vi-Sense</h2>
          <p className="text-white/60 text-sm">Sentiment Analysis</p>
        </div>

        <nav className="space-y-2">
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

      <div className="mt-auto pt-6 border-t border-white/10 space-y-4">
        <button
          onClick={handleSignOut}
          className="w-full flex items-center justify-center space-x-2 px-4 py-3 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-300 hover:text-red-200 border border-red-500/30 transition-all duration-300"
        >
          <LogOut className="h-5 w-5" />
          <span className="font-medium">Sign Out</span>
        </button>
      </div>
      <div className="text-white/60 text-sm mt-4 text-center">
        <p>© 2026 Vi-Sense</p>
        <p>Vietnamese Sentiment Analysis</p>
        <p>D.C Hieu</p>
      </div>
    </div>
  );
};
