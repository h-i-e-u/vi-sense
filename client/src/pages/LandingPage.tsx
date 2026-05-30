import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, BarChart3, MessageSquare, Zap } from "lucide-react";
import { AnimatedButton } from "../components/AnimatedButton";
import { GlassCard } from "../components/GlassCard";

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative py-20 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-5xl md:text-7xl font-bold text-white mb-6"
          >
            Vi-
            <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
              Sense
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-xl text-white/80 mb-8 max-w-2xl mx-auto"
          >
            Advanced Vietnamese sentiment analysis powered by AI. Analyze
            YouTube comments, <s>Shopee reviews</s>, and text in real-time.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <Link to="/register">
              <AnimatedButton size="lg">
                Get Started
                <ArrowRight className="ml-2 h-5 w-5" />
              </AnimatedButton>
            </Link>
            <Link to="/login">
              <AnimatedButton variant="outline" size="lg">
                Sign In
              </AnimatedButton>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Demo Card */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
          >
            <GlassCard className="p-8">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-white mb-2">
                  Try It Now
                </h2>
                <p className="text-white/60">
                  See sentiment analysis in action
                </p>
              </div>

              <div className="bg-white/5 rounded-lg p-4 mb-4">
                <p className="text-white text-lg italic">
                  "Sản phẩm này tuyệt vời, chất lượng rất tốt!"
                </p>
              </div>

              <div className="flex items-center justify-center space-x-4">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-green-400 font-medium">POSITIVE</span>
                  <span className="text-white/60">(95%)</span>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-4xl font-bold text-white text-center mb-12"
          >
            Powerful Features
          </motion.h2>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: MessageSquare,
                title: "Real-time Analysis",
                description:
                  "Instant sentiment analysis for Vietnamese text with high accuracy",
              },
              {
                icon: BarChart3,
                title: "Multi-source Support",
                description:
                  "Analyze sentiment from YouTube, Shopee, Tiki, and uploaded files",
              },
              {
                icon: Zap,
                title: "AI-Powered",
                description:
                  "Built with state-of-the-art PhoBERT model for Vietnamese NLP",
              },
            ].map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
              >
                <GlassCard className="text-center p-6 h-full">
                  <feature.icon className="h-12 w-12 text-purple-400 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-white/70">{feature.description}</p>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
          >
            <GlassCard className="p-8">
              <h2 className="text-3xl font-bold text-white mb-4">
                Ready to Analyze Sentiment?
              </h2>
              <p className="text-white/70 mb-6">
                Join <s>thousands</s> of users analyzing Vietnamese sentiment
                with AI precision.
              </p>
              <p className="text-white/70 mb-6">
                Enemy can't guess my sentiment cuz i don't have any.{" "}
                <s>Sun Tzu, The Art Of War</s>
              </p>
              <Link to="/register">
                <AnimatedButton size="lg">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </AnimatedButton>
              </Link>
            </GlassCard>
          </motion.div>
        </div>
      </section>
      {/* Tối giản Footer chỉ còn 1 dòng duy nhất */}
      <footer className="w-full mt-auto py-6 px-6 border-t border-white/5 bg-white/[0.02] backdrop-blur-sm">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-white/40">
          {/* Trái: Copyright */}
          <div>
            &copy; {new Date().getFullYear()} Vi-Sense. All rights reserved.
          </div>

          {/* Giữa: Các link pháp lý nhanh */}
          <div className="flex space-x-6">
            <Link
              to="/privacy"
              className="hover:text-white/80 transition-colors"
            >
              Privacy
            </Link>
            <Link to="/terms" className="hover:text-white/80 transition-colors">
              Terms
            </Link>
            <Link to="/docs" className="hover:text-white/80 transition-colors">
              API Docs
            </Link>
          </div>

          {/* Phải: Icon Mạng xã hội sử dụng SVG trực tiếp thay cho Lucide */}
          <div className="flex items-center space-x-4">
            {/* GitHub SVG */}
            <a
              href="https://github.com/h-i-e-u/vi-sense"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-white/80 transition-colors"
              aria-label="GitHub"
            >
              <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24">
                <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" />
              </svg>
            </a>

            {/* X / Twitter SVG */}
            {/* <a
              href="https://twitter.com"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-white/80 transition-colors"
              aria-label="Twitter"
            >
              <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
            </a> */}
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
