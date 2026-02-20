"use client";

import { motion, AnimatePresence } from "framer-motion";
import {
  MessageSquare,
  Code2,
  PenTool,
  Sparkles,
  CheckCircle2,
  Loader2,
} from "lucide-react";

const STEPS = [
  {
    key: "auditor",
    label: "Understanding your requirements...",
    icon: MessageSquare,
  },
  {
    key: "bridge",
    label: "Checking your current code...",
    icon: Code2,
  },
  {
    key: "architect",
    label: "Designing the solution...",
    icon: PenTool,
  },
  {
    key: "artisan",
    label: "Applying the magic (Writing code)...",
    icon: Sparkles,
  },
  {
    key: "qa",
    label: "Double-checking everything...",
    icon: CheckCircle2,
  },
] as const;

export type StepKey = (typeof STEPS)[number]["key"];
export type StepStatus = "idle" | "active" | "done";

type ProgressTimelineProps = {
  currentStep: StepKey | null;
  stepStatus: Record<StepKey, StepStatus>;
};

export function ProgressTimeline({ currentStep, stepStatus }: ProgressTimelineProps) {
  return (
    <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">
        Progress
      </h3>
      <ul className="space-y-0">
        {STEPS.map((step, index) => {
          const status = stepStatus[step.key];
          const isActive = status === "active";
          const isDone = status === "done";
          const Icon = step.icon;

          return (
            <motion.li
              key={step.key}
              initial={false}
              animate={{
                opacity: 1,
              }}
              transition={{ duration: 0.2 }}
              className="relative flex items-start gap-4"
            >
              {/* vertical line */}
              {index < STEPS.length - 1 && (
                <div
                  className="absolute left-[11px] top-8 h-[calc(100%+8px)] w-px bg-slate-200"
                  aria-hidden
                />
              )}

              <div
                className={`relative z-10 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2 ${
                  isDone
                    ? "border-emerald-500 bg-emerald-500 text-white"
                    : isActive
                      ? "border-indigo-600 bg-indigo-600 text-white"
                      : "border-slate-200 bg-white text-slate-400"
                }`}
              >
                {isActive ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : isDone ? (
                  <CheckCircle2 className="h-3.5 w-3.5" />
                ) : (
                  <Icon className="h-3.5 w-3.5" />
                )}
              </div>

              <div className="flex-1 pb-6">
                <p
                  className={`text-sm font-medium ${
                    isActive ? "text-slate-900" : isDone ? "text-slate-700" : "text-slate-500"
                  }`}
                >
                  {step.label}
                </p>
              </div>
            </motion.li>
          );
        })}
      </ul>
    </div>
  );
}

export { STEPS };
