"use client";

import { motion } from "framer-motion";
import { FileText, Sparkles } from "lucide-react";

export type HistoryItem = {
  id: string;
  title: string;
  updatedAt?: string;
};

type SidebarProps = {
  history: HistoryItem[];
  onSelect?: (id: string) => void;
  selectedId?: string | null;
};

const emptyMessage = "No runs yet. Let's build something!";

export function Sidebar({ history, onSelect, selectedId }: SidebarProps) {
  const isEmpty = !history.length;

  return (
    <aside className="flex h-full w-64 flex-col border-r border-slate-200/80 bg-white">
      <div className="flex items-center gap-2 border-b border-slate-200/80 px-5 py-4">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-sm">
          <FileText className="h-5 w-5" />
        </div>
        <span className="text-lg font-semibold tracking-tight text-slate-900">
          SOW Agent
        </span>
      </div>

      <div className="flex-1 overflow-auto p-4">
        <p className="mb-3 text-xs font-medium uppercase tracking-wider text-slate-500">
          History
        </p>

        {isEmpty ? (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-2xl border border-dashed border-slate-200 bg-slate-50/80 p-6 text-center"
          >
            <Sparkles className="mx-auto mb-3 h-10 w-10 text-slate-300" />
            <p className="text-sm font-medium text-slate-600">{emptyMessage}</p>
          </motion.div>
        ) : (
          <ul className="space-y-2">
            {history.map((item) => (
              <motion.li
                key={item.id}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                className="list-none"
              >
                <button
                  type="button"
                  onClick={() => onSelect?.(item.id)}
                  className={`w-full rounded-2xl border p-3 text-left shadow-sm transition-all hover:border-slate-200 hover:shadow-sm ${
                    selectedId === item.id
                      ? "border-indigo-200 bg-indigo-50/50 shadow-sm"
                      : "border-slate-200/80 bg-white"
                  }`}
                >
                  <p className="text-sm font-medium text-slate-900 truncate">
                    {item.title}
                  </p>
                  {item.updatedAt && (
                    <p className="mt-1 text-xs text-slate-500">{item.updatedAt}</p>
                  )}
                </button>
              </motion.li>
            ))}
          </ul>
        )}
      </div>
    </aside>
  );
}
