import React, { useState } from 'react';
import { SourceReference as SourceReferenceType } from '../types';
import { FileText, ChevronDown, ChevronUp, Copy, Check, Bookmark } from 'lucide-react';
import { useToast } from './Toast';

interface SourceReferenceProps {
  source: SourceReferenceType;
  index?: number;
  initiallyExpanded?: boolean;
}

export const SourceReference: React.FC<SourceReferenceProps> = ({
  source,
  index,
  initiallyExpanded = false,
}) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(initiallyExpanded);
  const [copied, setCopied] = useState<boolean>(false);
  const { showToast } = useToast();

  const handleCopySnippet = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(source.snippet);
    setCopied(true);
    showToast(`Page ${source.page} excerpt copied!`, 'success');
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="border border-slate-200/90 rounded-xl overflow-hidden bg-white shadow-xs transition-all hover:border-teal-300">
      {/* Header Bar / Collapsible Trigger */}
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-3 py-2 bg-slate-50/80 hover:bg-slate-100/80 text-left flex items-center justify-between gap-2 transition-colors cursor-pointer"
        aria-expanded={isExpanded}
        title="Toggle excerpt citation"
      >
        <div className="flex items-center gap-2 min-w-0">
          <div className="p-1 rounded bg-teal-50 text-teal-700 border border-teal-200/60 flex-shrink-0">
            <Bookmark className="w-3.5 h-3.5" />
          </div>

          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-xs font-bold text-slate-800">
              {index !== undefined ? `[Source ${index + 1}]` : 'Citation'}
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-teal-100/70 text-teal-900 border border-teal-200/50">
              <FileText className="w-3 h-3" />
              Page {source.page}
            </span>
            {source.chunk_id !== null && source.chunk_id !== undefined && (
              <span className="text-[10px] text-slate-400 font-mono hidden sm:inline">
                chunk #{source.chunk_id}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1.5 flex-shrink-0">
          <span className="text-[11px] text-teal-700 font-medium hidden sm:inline">
            {isExpanded ? 'Hide Excerpt' : 'View Excerpt'}
          </span>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          )}
        </div>
      </button>

      {/* Snippet Block (Accordion) */}
      {isExpanded && (
        <div className="p-3 bg-slate-50/40 border-t border-slate-100 text-xs text-slate-700 space-y-2 animate-in fade-in duration-150">
          <div className="flex items-start justify-between gap-2">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
              Direct Record Excerpt
            </span>
            <button
              type="button"
              onClick={handleCopySnippet}
              className="inline-flex items-center gap-1 text-[11px] text-slate-500 hover:text-slate-800 transition-colors p-1 rounded hover:bg-slate-200/60"
              title="Copy excerpt to clipboard"
            >
              {copied ? (
                <>
                  <Check className="w-3 h-3 text-emerald-600" />
                  <span className="text-emerald-700 font-medium">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3" />
                  <span>Copy</span>
                </>
              )}
            </button>
          </div>

          <blockquote className="p-2.5 rounded-lg bg-white border-l-2 border-teal-500 text-slate-700 italic leading-relaxed font-serif text-[12px] shadow-xs">
            "{source.snippet}"
          </blockquote>
        </div>
      )}
    </div>
  );
};
