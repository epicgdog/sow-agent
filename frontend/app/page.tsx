"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Terminal } from "lucide-react";

const MOCK_LINES = [
  { delay: 0, text: "$ sow-agent init", type: "prompt" },
  { delay: 400, text: "→ Loading workspace...", type: "log" },
  { delay: 800, text: "→ Auditor ready.", type: "success" },
  { delay: 1100, text: "→ Bridge ready.", type: "success" },
  { delay: 1400, text: "→ Architect ready.", type: "success" },
  { delay: 1700, text: "→ Artisan ready.", type: "success" },
  { delay: 2000, text: "→ QA Judge ready.", type: "success" },
  { delay: 2400, text: "", type: "blank" },
  { delay: 2600, text: "All agents online. Ready when you are.", type: "highlight" },
  { delay: 3200, text: "", type: "blank" },
  { delay: 3400, text: "$ _", type: "cursor" },
];

export default function WelcomePage() {
  const [visibleLines, setVisibleLines] = useState<typeof MOCK_LINES>([]);

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = [];
    MOCK_LINES.forEach((line) => {
      const t = setTimeout(() => {
        setVisibleLines((prev) => [...prev, line]);
      }, line.delay);
      timers.push(t);
    });
    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <div
      className="flex min-h-screen flex-col items-center justify-center px-4 py-12"
      style={{ backgroundColor: "#f9fafb" }}
    >
      <div className="w-full max-w-2xl">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
        <div className="mb-6 text-center" style={{ marginBottom: "1.5rem" }}>
          <div
            className="mb-3 inline-flex items-center gap-2 rounded-2xl bg-white px-4 py-2 shadow-sm border border-slate-200/80"
            style={{
              marginBottom: "0.75rem",
              padding: "0.5rem 1rem",
              backgroundColor: "#fff",
              borderRadius: "1rem",
              border: "1px solid #e2e8f0",
            }}
          >
            <Terminal className="h-5 w-5 text-indigo-600" style={{ color: "#4f46e5" }} />
            <span className="text-sm font-semibold text-slate-700" style={{ color: "#334155", fontWeight: 600 }}>
              SOW Agent
            </span>
          </div>
          <h1
            className="text-2xl font-bold text-slate-900 sm:text-3xl"
            style={{ color: "#0f172a", fontSize: "clamp(1.5rem, 4vw, 1.875rem)", fontWeight: 700 }}
          >
            Welcome
          </h1>
          <p className="mt-2 text-slate-600" style={{ color: "#475569", marginTop: "0.5rem" }}>
            Your agents are standing by. Click Begin to open the dashboard.
          </p>
        </div>
        </motion.div>

        {/* Mock terminal */}
        <div
          className="overflow-hidden rounded-2xl border border-slate-200/80 bg-slate-900 shadow-lg"
          style={{
            backgroundColor: "#0f172a",
            borderRadius: "1rem",
            border: "1px solid #e2e8f0",
            overflow: "hidden",
          }}
        >
          <div className="flex items-center gap-2 border-b border-slate-700/80 px-4 py-3">
            <span className="h-2.5 w-2.5 rounded-full bg-rose-500/90" />
            <span className="h-2.5 w-2.5 rounded-full bg-amber-500/90" />
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-500/90" />
            <span className="ml-2 text-xs text-slate-500">sow-agent — terminal</span>
          </div>
          <div className="font-mono text-sm p-4 min-h-[240px]">
            {visibleLines.map((line, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.15 }}
                className="flex items-center gap-1"
              >
                {line.type === "prompt" && (
                  <span className="text-emerald-400 select-none">$ </span>
                )}
                {line.type === "log" && (
                  <span className="text-slate-500 select-none">  </span>
                )}
                {line.type === "success" && (
                  <span className="text-emerald-400/90 select-none">  </span>
                )}
                {line.type === "cursor" && (
                  <>
                    <span className="text-emerald-400 select-none">$ </span>
                    <span className="inline-block h-4 w-2 animate-pulse bg-emerald-400" />
                  </>
                )}
                {line.type !== "cursor" && (
                  <span
                    className={
                      line.type === "prompt"
                        ? "text-slate-300"
                        : line.type === "log"
                          ? "text-slate-400"
                          : line.type === "success"
                            ? "text-emerald-400/90"
                            : line.type === "highlight"
                              ? "text-amber-300/95"
                              : ""
                    }
                  >
                    {line.text}
                  </span>
                )}
              </motion.div>
            ))}
          </div>
        </div>

        <div className="mt-8 flex justify-center" style={{ marginTop: "2rem", justifyContent: "center" }}>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 rounded-2xl px-6 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-indigo-700"
            style={{ backgroundColor: "#4f46e5", borderRadius: "1rem" }}
          >
            Begin
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}
