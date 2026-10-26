import React, { useState } from 'react';
import { CheckSquare, Bookmark, Check, RotateCcw } from 'lucide-react';
import { ActionItem } from '../types';

interface ActionChecklistProps {
  initialActions: ActionItem[];
}

export const ActionChecklist: React.FC<ActionChecklistProps> = ({ initialActions }) => {
  const [actions, setActions] = useState<ActionItem[]>(initialActions);

  const toggleAction = (id: string) => {
    setActions((prev) =>
      prev.map((item) => (item.id === id ? { ...item, completed: !item.completed } : item))
    );
  };

  const completedCount = actions.filter((a) => a.completed).length;
  const totalCount = actions.length;
  const progressPercent = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  const resetAll = () => {
    setActions((prev) => prev.map((item) => ({ ...item, completed: false })));
  };

  if (!actions || actions.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-6 text-center text-sm text-slate-500">
        No specific follow-up actions recorded in this document.
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-7 shadow-soft-card space-y-6">
      {/* Header & Progress Counter */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-emerald-50 text-emerald-700 rounded-xl">
            <CheckSquare className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-700 block">
              Patient Care Journey
            </span>
            <h3 className="text-lg font-bold text-slate-900 tracking-tight">
              Your Action Checklist
            </h3>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold text-slate-600 bg-slate-100 px-3 py-1 rounded-full border border-slate-200">
            {completedCount} of {totalCount} Completed ({progressPercent}%)
          </span>
          {completedCount > 0 && (
            <button
              onClick={resetAll}
              className="text-xs text-slate-400 hover:text-slate-600 flex items-center gap-1 transition-colors"
              title="Reset checklist"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
        <div
          className="bg-emerald-500 h-1.5 rounded-full transition-all duration-300"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Checklist Items */}
      <div className="space-y-3">
        {actions.map((item) => (
          <div
            key={item.id}
            onClick={() => toggleAction(item.id)}
            className={`p-4 rounded-xl border transition-all cursor-pointer flex items-start gap-3.5 select-none ${
              item.completed
                ? 'bg-emerald-50/40 border-emerald-200/80'
                : 'bg-white border-slate-200/90 hover:border-slate-300 hover:bg-slate-50/50'
            }`}
          >
            {/* Custom Checkbox */}
            <div
              className={`w-5 h-5 rounded-md flex items-center justify-center flex-shrink-0 mt-0.5 transition-colors ${
                item.completed
                  ? 'bg-emerald-600 text-white'
                  : 'border-2 border-slate-300 bg-white'
              }`}
            >
              {item.completed && <Check className="w-3.5 h-3.5 stroke-[3]" />}
            </div>

            {/* Description & Page Reference */}
            <div className="flex-1 min-w-0">
              <p
                className={`text-sm leading-relaxed transition-all ${
                  item.completed
                    ? 'line-through text-slate-400'
                    : 'text-slate-800 font-medium'
                }`}
              >
                {item.description}
              </p>
              {item.source_page && (
                <div className="mt-1 flex items-center gap-1 text-[11px] text-slate-400">
                  <Bookmark className="w-3 h-3 text-teal-600" />
                  <span>Documented on Page {item.source_page}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
