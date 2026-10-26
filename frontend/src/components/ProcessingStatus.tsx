import React from 'react';
import { CheckCircle2, Loader2, FileUp, Cpu, Database, Sparkles } from 'lucide-react';
import { ProcessingStatus as StatusType } from '../types';

interface ProcessingStatusProps {
  status: StatusType;
  uploadProgress: number;
}

export const ProcessingStatus: React.FC<ProcessingStatusProps> = ({
  status,
  uploadProgress,
}) => {
  const steps = [
    {
      id: 'reading',
      title: 'Reading Document',
      description: uploadProgress < 100 ? `Uploading PDF (${uploadProgress}%)` : 'Validating PDF structure',
      icon: FileUp,
    },
    {
      id: 'extracting',
      title: 'Extracting Content',
      description: 'Parsing pages and tables via PyMuPDF',
      icon: Cpu,
    },
    {
      id: 'indexing',
      title: 'Indexing Knowledge',
      description: 'Generating semantic vector embeddings',
      icon: Database,
    },
    {
      id: 'analyzing',
      title: 'AI Intelligence',
      description: 'Synthesizing summary, actions & questions',
      icon: Sparkles,
    },
  ];

  const getStepState = (stepId: string) => {
    const order = ['reading', 'extracting', 'indexing', 'analyzing', 'ready'];
    const currentIndex = order.indexOf(status);
    const stepIndex = order.indexOf(stepId);

    if (status === 'error') return 'pending';
    if (currentIndex > stepIndex || status === 'ready') return 'completed';
    if (currentIndex === stepIndex) return 'active';
    return 'pending';
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-soft-card max-w-2xl mx-auto my-6 animate-in fade-in duration-300">
      <div className="text-center mb-6">
        <h3 className="text-base font-bold text-slate-900 tracking-tight">Processing Document Intelligence</h3>
        <p className="text-xs text-slate-500 mt-1">
          Analyzing pages and building an isolated, source-grounded knowledge base
        </p>
      </div>

      {/* Progress Bar for Upload */}
      {status === 'reading' && uploadProgress < 100 && (
        <div className="mb-6">
          <div className="flex justify-between text-xs text-slate-500 mb-1.5 font-medium">
            <span>Uploading file stream...</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
            <div
              className="bg-teal-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Stepper Display */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
        {steps.map((step) => {
          const state = getStepState(step.id);
          const Icon = step.icon;

          return (
            <div
              key={step.id}
              className={`p-3.5 rounded-xl border flex items-start gap-3 transition-all duration-200 ${
                state === 'completed'
                  ? 'bg-emerald-50/60 border-emerald-200 text-emerald-900'
                  : state === 'active'
                  ? 'bg-teal-50 border-teal-300 shadow-sm text-teal-950 ring-2 ring-teal-500/10'
                  : 'bg-slate-50/60 border-slate-200 text-slate-400'
              }`}
            >
              <div className="mt-0.5 flex-shrink-0">
                {state === 'completed' ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                ) : state === 'active' ? (
                  <Loader2 className="w-5 h-5 text-teal-600 animate-spin" />
                ) : (
                  <Icon className="w-5 h-5 text-slate-300" />
                )}
              </div>
              <div>
                <h4
                  className={`text-xs font-bold ${
                    state === 'active' ? 'text-teal-900' : state === 'completed' ? 'text-emerald-900' : 'text-slate-500'
                  }`}
                >
                  {step.title}
                </h4>
                <p
                  className={`text-[11px] mt-0.5 ${
                    state === 'active' ? 'text-teal-700' : state === 'completed' ? 'text-emerald-700' : 'text-slate-400'
                  }`}
                >
                  {step.description}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
