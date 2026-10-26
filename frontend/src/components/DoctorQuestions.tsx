import React, { useState } from 'react';
import { HelpCircle, Copy, Check, Bot } from 'lucide-react';
import { useToast } from './Toast';

interface DoctorQuestionsProps {
  questions: string[];
  onAskQuestion?: (question: string) => void;
}

export const DoctorQuestions: React.FC<DoctorQuestionsProps> = ({
  questions,
  onAskQuestion,
}) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [copiedAll, setCopiedAll] = useState(false);
  const { showToast } = useToast();

  const handleCopySingle = (q: string, idx: number) => {
    navigator.clipboard.writeText(q);
    setCopiedIndex(idx);
    showToast('Question copied to clipboard!', 'success');
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const handleCopyAll = () => {
    const formatted = questions.map((q, i) => `${i + 1}. ${q}`).join('\n\n');
    navigator.clipboard.writeText(formatted);
    setCopiedAll(true);
    showToast('All consultation questions copied!', 'success');
    setTimeout(() => setCopiedAll(false), 2000);
  };

  if (!questions || questions.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-6 text-center text-sm text-slate-500">
        No specific questions generated for this document.
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-7 shadow-soft-card space-y-6">
      {/* Header with Copy-All Button */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-amber-50 text-amber-700 rounded-xl">
            <HelpCircle className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-amber-700 block">
              Consultation Preparation
            </span>
            <h3 className="text-lg font-bold text-slate-900 tracking-tight">
              Questions for Your Doctor
            </h3>
          </div>
        </div>

        <button
          onClick={handleCopyAll}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition-colors focus-ring cursor-pointer"
          title="Copy all questions to clipboard"
        >
          {copiedAll ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-600" />
              <span>Copied All!</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>Copy All Questions</span>
            </>
          )}
        </button>
      </div>

      <p className="text-xs text-slate-500 leading-relaxed -mt-2">
        Bring these questions to your next clinical visit to discuss what these findings mean for your health plan. You can also ask CareBridge AI right now to see what your document says about them.
      </p>

      {/* Numbered Questions Grid */}
      <div className="space-y-3">
        {questions.map((question, idx) => {
          const isCopied = copiedIndex === idx;

          return (
            <div
              key={idx}
              className="p-4 rounded-xl border border-slate-200/80 bg-slate-50/50 hover:bg-white hover:border-slate-300 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 group"
            >
              <div className="flex items-start gap-3 flex-1">
                <span className="w-6 h-6 rounded-full bg-amber-100 text-amber-900 font-bold text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
                  {idx + 1}
                </span>
                <p className="text-sm text-slate-800 font-medium leading-relaxed">
                  {question}
                </p>
              </div>

              <div className="flex items-center gap-2 self-end sm:self-center flex-shrink-0">
                {onAskQuestion && (
                  <button
                    type="button"
                    onClick={() => onAskQuestion(question)}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-teal-50 hover:bg-teal-100 text-teal-800 border border-teal-200 text-xs font-semibold transition-colors cursor-pointer"
                    title="Ask CareBridge AI what your document says about this question"
                  >
                    <Bot className="w-3.5 h-3.5 text-teal-600" />
                    <span>Ask AI</span>
                  </button>
                )}

                <button
                  type="button"
                  onClick={() => handleCopySingle(question, idx)}
                  className="opacity-80 sm:opacity-0 sm:group-hover:opacity-100 text-slate-400 hover:text-slate-700 transition-opacity p-1.5 rounded hover:bg-slate-100 flex-shrink-0 cursor-pointer"
                  title="Copy question"
                  aria-label="Copy question"
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
  );
};
