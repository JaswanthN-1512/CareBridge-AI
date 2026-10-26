import React, { useState } from 'react';
import { Database, Copy, Check, Bookmark, Layers } from 'lucide-react';
import { KeyInformationItem } from '../types';
import { useToast } from './Toast';

interface KeyInformationCardProps {
  items: KeyInformationItem[];
}

export const KeyInformationCard: React.FC<KeyInformationCardProps> = ({ items }) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const { showToast } = useToast();

  const handleCopy = (text: string, index: number, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    showToast(`Copied ${label}: ${text}`, 'success');
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  if (!items || items.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-6 text-center text-sm text-slate-500">
        No specific key measurements extracted from this document.
      </div>
    );
  }

  // Group by category
  const grouped = items.reduce<Record<string, KeyInformationItem[]>>((acc, item) => {
    const cat = item.category || 'General Findings';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(item);
    return acc;
  }, {});

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-7 shadow-soft-card space-y-6">
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-blue-50 text-blue-700 rounded-xl">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-blue-700 block">
              Extracted Data Points
            </span>
            <h3 className="text-lg font-bold text-slate-900 tracking-tight">
              Key Document Information
            </h3>
          </div>
        </div>
        <span className="text-xs text-slate-400 font-medium">
          {items.length} {items.length === 1 ? 'finding' : 'findings'} extracted
        </span>
      </div>

      {/* Categorized Grids */}
      <div className="space-y-6">
        {Object.entries(grouped).map(([category, catItems]) => (
          <div key={category} className="space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-600 uppercase tracking-wider">
              <Layers className="w-3.5 h-3.5 text-slate-400" />
              <span>{category}</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {catItems.map((item, idx) => {
                const globalIdx = items.indexOf(item);
                const isCopied = copiedIndex === globalIdx;

                return (
                  <div
                    key={idx}
                    className="p-3.5 rounded-xl border border-slate-200/80 bg-slate-50/50 hover:bg-white hover:border-slate-300 transition-all flex flex-col justify-between group"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <span className="text-xs font-medium text-slate-500">
                        {item.label}
                      </span>
                      {item.source_page && (
                        <span className="text-[10px] font-semibold bg-white text-slate-600 border border-slate-200 px-2 py-0.5 rounded-md flex-shrink-0 flex items-center gap-1">
                          <Bookmark className="w-2.5 h-2.5 text-teal-600" />
                          Page {item.source_page}
                        </span>
                      )}
                    </div>

                    <div className="mt-2 flex items-baseline justify-between gap-2">
                      <span className="text-sm font-bold text-slate-900 tracking-tight break-words">
                        {item.value}
                      </span>
                      <button
                        onClick={() => handleCopy(`${item.label}: ${item.value}`, globalIdx, item.label)}
                        className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-slate-700 transition-opacity p-1 rounded hover:bg-slate-100"
                        title="Copy to clipboard"
                        aria-label="Copy finding"
                      >
                        {isCopied ? (
                          <Check className="w-3.5 h-3.5 text-emerald-600" />
                        ) : (
                          <Copy className="w-3.5 h-3.5" />
                        )}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
