import React from 'react';
import { Sparkles, FileText, CheckSquare, MessageSquare, HelpCircle, ShieldCheck } from 'lucide-react';

export const Hero: React.FC = () => {
  return (
    <div className="text-center max-w-4xl mx-auto pt-6 pb-10 px-4">
      {/* Category Pill */}
      <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-teal-50 border border-teal-200 text-teal-800 text-xs font-semibold mb-6 shadow-sm">
        <Sparkles className="w-3.5 h-3.5 text-teal-600" />
        AI-Powered Healthcare Navigation & Document Intelligence
      </div>

      {/* Main Value Proposition Title */}
      <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.15] mb-5">
        Understand your healthcare documents.
        <span className="block bg-gradient-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">
          Prepare better conversations.
        </span>
      </h1>

      {/* Supporting Explanation */}
      <p className="text-slate-600 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed mb-8">
        Translate complex medical terminology into clear explanations, extract clinician instructions into an actionable checklist, and ask questions with source-grounded page citations.
      </p>

      {/* Value Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-3xl mx-auto text-left">
        <div className="p-3 bg-white rounded-xl border border-slate-200 shadow-sm flex items-center gap-2.5">
          <div className="p-2 bg-teal-50 text-teal-700 rounded-lg">
            <FileText className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-slate-900">Document Summary</div>
            <div className="text-[10px] text-slate-500">Plain-language breakdown</div>
          </div>
        </div>

        <div className="p-3 bg-white rounded-xl border border-slate-200 shadow-sm flex items-center gap-2.5">
          <div className="p-2 bg-blue-50 text-blue-700 rounded-lg">
            <MessageSquare className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-slate-900">RAG Document Q&A</div>
            <div className="text-[10px] text-slate-500">Verified page citations</div>
          </div>
        </div>

        <div className="p-3 bg-white rounded-xl border border-slate-200 shadow-sm flex items-center gap-2.5">
          <div className="p-2 bg-emerald-50 text-emerald-700 rounded-lg">
            <CheckSquare className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-slate-900">Action Checklist</div>
            <div className="text-[10px] text-slate-500">Direct from clinician notes</div>
          </div>
        </div>

        <div className="p-3 bg-white rounded-xl border border-slate-200 shadow-sm flex items-center gap-2.5">
          <div className="p-2 bg-amber-50 text-amber-700 rounded-lg">
            <HelpCircle className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-slate-900">Doctor Questions</div>
            <div className="text-[10px] text-slate-500">Tailored visit agendas</div>
          </div>
        </div>
      </div>

      {/* Safety Micro-line */}
      <div className="mt-6 flex items-center justify-center gap-1.5 text-xs text-slate-400">
        <ShieldCheck className="w-3.5 h-3.5 text-teal-600" />
        <span>Strict privacy: Documents are processed in-memory and never shared or used to train models.</span>
      </div>
    </div>
  );
};
