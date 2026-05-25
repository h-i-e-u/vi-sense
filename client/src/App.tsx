import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import Dashboard from "./pages/Dashboard";
import AnalyzeLink from "./pages/AnalyzeLink";
import AnalyzeText from "./pages/AnalyzeText";
import AnalyzeFile from "./pages/AnalyzeFile";
import History from "./pages/History";
import Analytics from "./pages/Analytics";
import DetailAnalytics from "./pages/DetailAnalytics";
import NotFound from "./pages/NotFound";
// import './App.css'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/analyze/link" element={<AnalyzeLink />} />
          <Route path="/analyze/text" element={<AnalyzeText />} />
          <Route path="/analyze/file" element={<AnalyzeFile />} />
          <Route path="/history" element={<History />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/analytics/:jobId" element={<DetailAnalytics />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
        <Toaster position="top-right" />
      </div>
    </Router>
  );
}

export default App;
