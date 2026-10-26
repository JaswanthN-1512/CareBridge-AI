import React, { useState } from 'react';
import { FileText, Tag, ShieldCheck, Copy, Check } from 'lucide-react';
import { DocumentAnalysisResponse, DocumentUploadResponse } from '../types';
import { useToast } from './Toast';

interface SummaryCardProps {
  analysis: DocumentAnalysisResponse;
  documentMeta: DocumentUploadResponse | null;
}

export const SummaryCard: React.FC<SummaryCardProps> = ({
  analysis,
  documentMeta,
}) => {
  const [copied, setCopied] = useState(false);
  const { showToast } = useToast();

  const handleCopySummary = () => {
    navigator.clipboard.writeText(analysis.summary);
    setCopied(true);
    showToast('Executive summary copied to clipboard!', 'success');
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-7 shadow-soft-card space-y-5">
      {/* Header with Classification Badge */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-teal-50 text-teal-700 rounded-xl">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-teal-700 block">
              Executive Summary
            </span>
            <h3 className="text-lg font-bold text-slate-900 tracking-tight">
              {analysis.document_type}
            </h3>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {documentMeta && (
            <div className="hidden sm:flex items-center gap-2 text-xs text-slate-500 font-medium bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200/60">
              <Tag className="w-3.5 h-3.5 text-slate-400" />
              <span className="truncate max-w-[200px]" title={documentMeta.filename}>
                {documentMeta.filename}
              </span>
              <span>•</span>
              <span>{documentMeta.total_pages} {documentMeta.total_pages === 1 ? 'Page' : 'Pages'}</span>
            </div>
          )}

          <button
            onClick={handleCopySummary}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition-colors focus-ring cursor-pointer"
            title="Copy summary text"
            aria-label="Copy executive summary"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-600" />
                <span>Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy Summary</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Summary Narrative */}
      <div className="prose prose-slate max-w-none">
        <p className="text-slate-700 text-sm sm:text-base leading-relaxed whitespace-pre-line">
          {analysis.summary}
        </p>
      </div>

      {/* Grounding & Ethics Footnote */}
      <div className="pt-2 flex items-center gap-2 text-xs text-slate-400 border-t border-slate-100">
        <ShieldCheck className="w-4 h-4 text-teal-600 flex-shrink-0" />
        <span>Grounded directly in documented text • Free of unverified external extrapolations</span>
      </div>
    </div>
  );
};
