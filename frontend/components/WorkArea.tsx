"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { RefreshCw, ChevronDown, ChevronRight, Terminal } from "lucide-react";

const PLACEHOLDER_SOW = `# Statement of Work

## Objective
Describe the scope and deliverables for this engagement.

## Requirements
- Clear acceptance criteria
- Timeline and milestones
- Success metrics

## Notes
Add any context that helps the agent understand your needs.
`;

const SAMPLE_DIFF_OLD = `export function oldHelper() {
  return "legacy";
}
`;

const SAMPLE_DIFF_NEW = `export function newHelper() {
  return "updated";
}
`;

type WorkAreaProps = {
  refinementMode: boolean;
  onRefinementToggle: (value: boolean) => void;
};

export function WorkArea({
  refinementMode,
  onRefinementToggle,
}: WorkAreaProps) {
  const [sowContent, setSowContent] = useState(PLACEHOLDER_SOW);
  const [technicalOpen, setTechnicalOpen] = useState(false);
  const [showDiff, setShowDiff] = useState(false);

  return (
    <div className="flex flex-1 flex-col gap-6">
      {/* Refinement Mode badge */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => onRefinementToggle(!refinementMode)}
          className={`inline-flex items-center gap-2 rounded-2xl border px-4 py-2 text-sm font-medium shadow-sm transition-all ${
            refinementMode
              ? "border-indigo-200 bg-indigo-50 text-indigo-700"
              : "border-slate-200 bg-white text-slate-600 hover:border-slate-300"
          }`}
        >
          <RefreshCw
            className={`h-4 w-4 ${refinementMode ? "animate-spin" : ""}`}
          />
          {refinementMode ? "Refinement mode — Perfecting the code" : "Refinement mode"}
        </button>
      </div>

      {/* SOW Editor + Diff area */}
      <div className="grid min-h-0 flex-1 gap-6 lg:grid-cols-2">
        {/* SOW Editor */}
        <motion.div
          layout
          className="flex flex-col rounded-2xl border border-slate-200/80 bg-white shadow-sm"
        >
          <div className="border-b border-slate-200/80 px-4 py-3">
            <h3 className="text-sm font-semibold text-slate-700">
              Statement of Work
            </h3>
          </div>
          <div className="flex-1 overflow-auto p-4">
            <textarea
              value={sowContent}
              onChange={(e) => setSowContent(e.target.value)}
              placeholder="Describe your requirements..."
              className="min-h-[280px] w-full resize-none rounded-xl border border-slate-200 bg-slate-50/50 p-4 text-sm text-slate-800 placeholder:text-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
              spellCheck={false}
            />
          </div>
        </motion.div>

        {/* Visual Diff */}
        <motion.div
          layout
          className="flex flex-col rounded-2xl border border-slate-200/80 bg-white shadow-sm"
        >
          <div className="flex items-center justify-between border-b border-slate-200/80 px-4 py-3">
            <h3 className="text-sm font-semibold text-slate-700">
              Document comparison
            </h3>
            <button
              type="button"
              onClick={() => setShowDiff(!showDiff)}
              className="text-xs font-medium text-indigo-600 hover:text-indigo-700"
            >
              {showDiff ? "Hide" : "Show"} sample diff
            </button>
          </div>
          <div className="flex-1 overflow-auto p-4">
            {showDiff ? (
              <div className="rounded-xl border border-slate-200 bg-slate-50/50 font-mono text-sm">
                <div className="border-b border-slate-200 bg-slate-100/80 px-3 py-2 text-xs font-medium text-slate-500">
                  Before → After
                </div>
                <div className="divide-y divide-slate-200">
                  <div className="diff-line-remove">{SAMPLE_DIFF_OLD.trim()}</div>
                  <div className="diff-line-add">{SAMPLE_DIFF_NEW.trim()}</div>
                </div>
              </div>
            ) : (
              <p className="text-sm text-slate-500">
                Run the agent to see a clean document-style comparison here.
              </p>
            )}
          </div>
        </motion.div>
      </div>

      {/* View Technical Details accordion */}
      <motion.div
        layout
        className="rounded-2xl border border-slate-200/80 bg-white shadow-sm overflow-hidden"
      >
        <button
          type="button"
          onClick={() => setTechnicalOpen(!technicalOpen)}
          className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-slate-50/80"
        >
          <span className="flex items-center gap-2 text-sm font-medium text-slate-700">
            {technicalOpen ? (
              <ChevronDown className="h-4 w-4 text-slate-500" />
            ) : (
              <ChevronRight className="h-4 w-4 text-slate-500" />
            )}
            View technical details
          </span>
          <Terminal className="h-4 w-4 text-slate-400" />
        </button>
        <AnimatePresence initial={false}>
          {technicalOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="border-t border-slate-200/80 bg-slate-50/50 overflow-hidden"
            >
              <pre className="overflow-auto p-4 text-xs text-slate-600 font-mono whitespace-pre">
                {`[SOW Agent] Pipeline started
[Auditor] Parsing requirements...
[Bridge] Scanning repository...
[Architect] Generating plan...
[Artisan] Applying changes...
[QA] Running checks...
[OK] Complete.`}
              </pre>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
