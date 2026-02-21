"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, Github } from "lucide-react";
import { Sidebar, type HistoryItem } from "@/components/Sidebar";
import {
  ProgressTimeline,
  type StepKey,
  type StepStatus,
} from "@/components/ProgressTimeline";
import { WorkArea } from "@/components/WorkArea";

export type Run = {
  id: string;
  title: string;
  sowContent: string;
  updatedAt: string;
  logLines: string[];
};

function makeRunId() {
  return `run-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

function titleFromSow(sow: string): string {
  const first = sow.trim().split(/\n/)[0]?.replace(/^#\s*/, "").trim();
  return first || "Untitled run";
}

const STEP_ORDER: StepKey[] = ["auditor", "bridge", "architect", "artisan", "qa"];

function getStepStatus(
  currentStep: StepKey | null,
  stepKey: StepKey
): StepStatus {
  if (!currentStep) return "idle";
  const currentIndex = STEP_ORDER.indexOf(currentStep);
  const stepIndex = STEP_ORDER.indexOf(stepKey);
  if (stepIndex < currentIndex) return "done";
  if (stepIndex === currentIndex) return "active";
  return "idle";
}

function buildStepStatusMap(currentStep: StepKey | null): Record<StepKey, StepStatus> {
  return STEP_ORDER.reduce(
    (acc, key) => {
      acc[key] = getStepStatus(currentStep, key);
      return acc;
    },
    {} as Record<StepKey, StepStatus>
  );
}

const STEP_LOG_LINES: Record<StepKey, string[]> = {
  auditor: ["[SOW Agent] Pipeline started", "[Auditor] Parsing requirements..."],
  bridge: ["[Bridge] Scanning repository..."],
  architect: ["[Architect] Generating plan..."],
  artisan: ["[Artisan] Applying changes..."],
  qa: ["[QA] Running checks...", "[OK] Complete."],
};

const INITIAL_SOW = `# Statement of Work

## Objective
Describe the scope and deliverables for this engagement.

## Requirements
- Clear acceptance criteria
- Timeline and milestones
- Success metrics

## Notes
Add any context that helps the agent understand your needs.
`;

const INITIAL_RUNS: Run[] = [
  {
    id: "1",
    title: "Update Auth Module",
    sowContent: INITIAL_SOW,
    updatedAt: "2 hours ago",
    logLines: [],
  },
  {
    id: "2",
    title: "Add payment integration",
    sowContent: INITIAL_SOW,
    updatedAt: "Yesterday",
    logLines: [],
  },
  {
    id: "3",
    title: "Refactor API routes",
    sowContent: INITIAL_SOW,
    updatedAt: "Last week",
    logLines: [],
  },
];

export default function DashboardPage() {
  const [runs, setRuns] = useState<Run[]>(INITIAL_RUNS);
  const [selectedId, setSelectedId] = useState<string | null>("1");
  const [currentStep, setCurrentStep] = useState<StepKey | null>(null);
  const [refinementMode, setRefinementMode] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [runningRunId, setRunningRunId] = useState<string | null>(null);
  const [repoUrl, setRepoUrl] = useState("");
  const [autoPush, setAutoPush] = useState(false);

  const selectedRun = selectedId ? runs.find((r) => r.id === selectedId) : null;
  const history: HistoryItem[] = runs.map((r) => ({
    id: r.id,
    title: r.title,
    updatedAt: r.updatedAt,
  }));

  const updateRunSow = useCallback((id: string, sowContent: string) => {
    setRuns((prev) =>
      prev.map((r) =>
        r.id === id ? { ...r, sowContent, title: titleFromSow(sowContent) || r.title } : r
      )
    );
  }, []);

  const handleStart = useCallback(async () => {
    if (isRunning || !selectedRun) return;
    const sow = selectedRun.sowContent;
    const newRun: Run = {
      id: makeRunId(),
      title: titleFromSow(sow),
      sowContent: sow,
      updatedAt: "Just now",
      logLines: [],
    };
    setRuns((prev) => [newRun, ...prev]);
    setSelectedId(newRun.id);
    setRunningRunId(newRun.id);
    setIsRunning(true);
    setCurrentStep("auditor");

    const appendLog = (lines: string[]) => {
      setRuns((prev) =>
        prev.map((r) =>
          r.id === newRun.id ? { ...r, logLines: [...r.logLines, ...lines] } : r
        )
      );
    };

    // If repo URL is set, call real API; otherwise run mock steps
    if (repoUrl.trim()) {
      // Show progress while waiting
      let stepIndex = 0;
      const progressInterval = setInterval(() => {
        const step = STEP_ORDER[stepIndex];
        if (STEP_LOG_LINES[step]) appendLog(STEP_LOG_LINES[step]);
        stepIndex += 1;
        if (stepIndex >= STEP_ORDER.length) {
          clearInterval(progressInterval);
          setCurrentStep(null);
        } else {
          setCurrentStep(STEP_ORDER[stepIndex]);
        }
      }, 2000);

      try {
        const res = await fetch("/api/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            repoUrl: repoUrl.trim(),
            sowContent: sow,
            autoPush,
          }),
        });
        clearInterval(progressInterval);
        const data = await res.json();
        if (!res.ok) {
          appendLog([`[ERROR] ${data.error || res.statusText}: ${data.detail || ""}`]);
        } else {
          setRuns((prev) =>
            prev.map((r) =>
              r.id === newRun.id
                ? { ...r, logLines: data.log?.split("\n").filter(Boolean) ?? r.logLines }
                : r
            )
          );
        }
      } catch (err) {
        clearInterval(progressInterval);
        appendLog([`[ERROR] ${err instanceof Error ? err.message : "Request failed"}`]);
      } finally {
        setCurrentStep(null);
        setIsRunning(false);
        setRunningRunId(null);
      }
      return;
    }

    // Mock pipeline
    let stepIndex = 0;
    const interval = setInterval(() => {
      const step = STEP_ORDER[stepIndex];
      if (STEP_LOG_LINES[step]) appendLog(STEP_LOG_LINES[step]);
      stepIndex += 1;
      if (stepIndex >= STEP_ORDER.length) {
        clearInterval(interval);
        setCurrentStep(null);
        setIsRunning(false);
        setRunningRunId(null);
        return;
      }
      setCurrentStep(STEP_ORDER[stepIndex]);
    }, 1400);
  }, [isRunning, selectedRun, repoUrl, autoPush]);

  const stepStatusMap = buildStepStatusMap(currentStep);

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        history={history}
        selectedId={selectedId}
        onSelect={setSelectedId}
      />

      <main className="flex min-w-0 flex-1 flex-col overflow-hidden bg-[#F9FAFB]">
        {/* Top bar + Repo + Start */}
        <header className="flex shrink-0 flex-col gap-3 border-b border-slate-200/80 bg-white px-6 py-4 shadow-sm">
          <div className="flex items-center justify-between">
            <h1 className="text-lg font-semibold text-slate-900">
              {selectedId
                ? history.find((h) => h.id === selectedId)?.title ?? "Dashboard"
                : "Dashboard"}
            </h1>
            <motion.button
              type="button"
              onClick={handleStart}
              disabled={isRunning}
              whileHover={!isRunning ? { scale: 1.02 } : {}}
              whileTap={!isRunning ? { scale: 0.98 } : {}}
              className="inline-flex items-center gap-2 rounded-2xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 disabled:opacity-70 disabled:cursor-not-allowed"
            >
              <Play className="h-4 w-4" />
              Start
            </motion.button>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex min-w-0 flex-1 items-center gap-2 rounded-xl border border-slate-200/80 bg-slate-50/50 px-3 py-2">
              <Github className="h-4 w-4 shrink-0 text-slate-400" />
              <input
                type="url"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="https://github.com/owner/repo (optional — run real agent & push)"
                className="min-w-0 flex-1 bg-transparent text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none"
              />
            </div>
            <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-600">
              <input
                type="checkbox"
                checked={autoPush}
                onChange={(e) => setAutoPush(e.target.checked)}
                className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
              />
              Auto-push to GitHub
            </label>
          </div>
        </header>

        <div className="flex flex-1 gap-6 overflow-hidden p-6">
          {/* Progress Timeline (left column) */}
          <div className="w-72 shrink-0">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentStep ?? "idle"}
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 12 }}
                transition={{ duration: 0.25 }}
              >
                <ProgressTimeline
                  currentStep={currentStep}
                  stepStatus={stepStatusMap}
                />
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Work area (SOW + Diff + Refinement + Technical accordion) */}
          <motion.div
            layout
            className="min-w-0 flex-1 overflow-auto"
          >
            <WorkArea
              refinementMode={refinementMode}
              onRefinementToggle={setRefinementMode}
              sowContent={selectedRun?.sowContent ?? ""}
              onSowChange={(content) => selectedId && updateRunSow(selectedId, content)}
              runLog={selectedRun?.logLines ?? []}
              isRunning={isRunning && runningRunId === selectedId}
            />
          </motion.div>
        </div>
      </main>
    </div>
  );
}
