import React from 'react';
import { ShieldAlert, AlertTriangle } from 'lucide-react';

interface SafetyNoticeProps {
  compact?: boolean;
}

export const SafetyNotice: React.FC<SafetyNoticeProps> = ({ compact = false }) => {
  if (compact) {
    return (
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-900 flex items-start gap-2.5">
        <ShieldAlert className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold">Informational Assistant:</span> CareBridge AI does not provide medical diagnoses or treatment recommendations. Always discuss document findings with your healthcare professional.
        </div>
      </div>
    );
  }

  return (
    <div className="bg-amber-50/80 border border-amber-200 rounded-xl p-4 sm:p-5 text-amber-950 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="p-2 bg-amber-100 rounded-lg text-amber-700 flex-shrink-0">
          <AlertTriangle className="w-5 h-5" />
        </div>
        <div className="space-y-1">
          <h4 className="text-sm font-bold text-amber-900 tracking-tight">
            Important Medical Safety & Informational Notice
          </h4>
          <p className="text-xs text-amber-800 leading-relaxed">
            CareBridge AI is designed exclusively as an educational document-navigation tool. It is <strong>not a medical doctor, diagnostic device, or prescription system</strong>. Information extracted from uploaded records must never be interpreted as clinical advice or used to alter medication regimens without qualified medical supervision.
          </p>
          <div className="pt-1.5 flex items-center gap-1.5 text-[11px] font-semibold text-amber-900">
            <span>In an emergency, immediately dial 911 (US/CA), 988 (Crisis), or go to the nearest emergency room.</span>
          </div>
        </div>
      </div>
    </div>
  );
};
