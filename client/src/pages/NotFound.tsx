import React from "react";
import { Link } from "react-router-dom";

const NotFound: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 text-center">
      <h1 className="text-6xl font-bold text-rose-400">404</h1>

      <h2 className="mt-4 text-2xl font-semibold text-orange-300">
        Page Not Found
      </h2>

      <p className="mt-2 text-gray-300 max-w-md">
        Trang bạn đang tìm kiếm không tồn tại hoặc đã bị di chuyển.
      </p>

      <Link
        to="/"
        className="mt-6 inline-flex items-center justify-center rounded-xl bg-blue-600 px-6 py-3 text-white font-medium shadow-md transition hover:bg-blue-700 active:scale-95"
      >
        Go Home
      </Link>
    </div>
  );
};

export default NotFound;