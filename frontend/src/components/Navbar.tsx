import React from 'react';
import { Activity, RefreshCw, Printer } from 'lucide-react';

interface NavbarProps {
  backendStatus: string;
  hasActiveDocument: boolean;
  hasAnalysis?: boolean;
  onReset: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  backendStatus,
  hasActiveDocument,
  hasAnalysis = false,
  onReset,
}) => {
  const handlePrint = () => {
    window.print();
  };

  return (
    <header role="banner" className="border-b border-slate-200/80 bg-white/90 backdrop-blur-md sticky top-0 z-40 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Identity */}
        <div 
          className="flex items-center gap-3 cursor-pointer group focus-ring rounded-xl p-1" 
          onClick={onReset}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') onReset(); }}
          aria-label="CareBridge AI Home"
        >
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-teal-700 to-teal-500 flex items-center justify-center text-white shadow-sm ring-1 ring-teal-600/20 group-hover:scale-105 transition-transform">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <span className="font-bold text-lg text-slate-900 tracking-tight flex items-center gap-1.5">
              CareBridge <span className="text-teal-600">AI</span>
            </span>
            <span className="text-[10px] text-slate-500 block -mt-1 font-medium tracking-wide uppercase">
              Healthcare Document Intelligence
            </span>
          </div>
        </div>

        {/* Action Controls & Health Telemetry */}
        <div className="flex items-center gap-2 sm:gap-3">
          <div className="hidden sm:flex items-center gap-2 text-xs text-slate-500">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100/80 border border-slate-200/80 font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              {backendStatus}
            </span>
          </div>

          {hasAnalysis && (
            <button
              onClick={handlePrint}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-teal-50 hover:bg-teal-100 text-teal-800 border border-teal-200 transition-colors focus-ring"
              title="Print or export consultation agenda for doctor appointment"
              aria-label="Print consultation agenda"
            >
              <Printer className="w-3.5 h-3.5 text-teal-700" />
              <span className="hidden sm:inline">Print Agenda</span>
            </button>
          )}

          {hasActiveDocument && (
            <button
              onClick={onReset}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 transition-colors focus-ring"
              title="Upload another document"
              aria-label="Start new document analysis"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>New Document</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
