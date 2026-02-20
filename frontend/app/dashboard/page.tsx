"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play } from "lucide-react";
import { Sidebar, type HistoryItem } from "@/components/Sidebar";
import {
  ProgressTimeline,
  type StepKey,
  type StepStatus,
} from "@/components/ProgressTimeline";
import { WorkArea } from "@/components/WorkArea";

const DEMO_HISTORY: HistoryItem[] = [
  { id: "1", title: "Update Auth Module", updatedAt: "2 hours ago" },
  { id: "2", title: "Add payment integration", updatedAt: "Yesterday" },
  { id: "3", title: "Refactor API routes", updatedAt: "Last week" },
];

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

export default function DashboardPage() {
  const [history] = useState<HistoryItem[]>(DEMO_HISTORY);
  const [selectedId, setSelectedId] = useState<string | null>("1");
  const [currentStep, setCurrentStep] = useState<StepKey | null>(null);
  const [refinementMode, setRefinementMode] = useState(false);
  const [isRunning, setIsRunning] = useState(false);

  const handleStart = useCallback(() => {
    if (isRunning) return;
    setIsRunning(true);
    setCurrentStep("auditor");

    let stepIndex = 0;
    const interval = setInterval(() => {
      stepIndex += 1;
      if (stepIndex >= STEP_ORDER.length) {
        clearInterval(interval);
        setCurrentStep(null);
        setIsRunning(false);
        return;
      }
      setCurrentStep(STEP_ORDER[stepIndex]);
    }, 1400);
  }, [isRunning]);

  const stepStatusMap = buildStepStatusMap(currentStep);

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        history={history}
        selectedId={selectedId}
        onSelect={setSelectedId}
      />

      <main className="flex min-w-0 flex-1 flex-col overflow-hidden bg-[#F9FAFB]">
        {/* Top bar + Start */}
        <header className="flex shrink-0 items-center justify-between border-b border-slate-200/80 bg-white px-6 py-4 shadow-sm">
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
            />
          </motion.div>
        </div>
      </main>
    </div>
  );
}
