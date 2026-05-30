import React from "react";
import { Link } from "react-router-dom";
import { GlassCard } from "../components/GlassCard";
import { AnimatedButton } from "../components/AnimatedButton";

const NotFound: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 text-center">
      <GlassCard>
        <h1 className="text-6xl font-bold text-rose-400">404</h1>

        <h2 className="mt-4 text-2xl font-semibold text-orange-300">
          Page Not Found
        </h2>

        <p className="mt-2 text-gray-300 max-w-md">
          Trang bạn đang tìm kiếm không tồn tại hoặc đã bị di chuyển.
        </p>
        <AnimatedButton className="mt-4">
          <Link to="/">Go Home</Link>
        </AnimatedButton>
      </GlassCard>
    </div>
  );
};

export default NotFound;
