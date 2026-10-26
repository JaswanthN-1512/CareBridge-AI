import React, { useState, useRef, useEffect } from 'react';
import { UploadCloud, FileText, ArrowRight, Sparkles } from 'lucide-react';
import { SampleDocumentMeta } from '../types';
import { apiService } from '../services/api';

interface UploadBoxProps {
  onFileSelect: (file: File) => void;
  onSampleSelect: (sampleId: string) => void;
  isProcessing: boolean;
  onError: (msg: string) => void;
}

export const UploadBox: React.FC<UploadBoxProps> = ({
  onFileSelect,
  onSampleSelect,
  isProcessing,
  onError,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [samples, setSamples] = useState<SampleDocumentMeta[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    apiService.getSamples()
      .then((data) => setSamples(data))
      .catch(() => {

        // Fallback default sample metadata if backend offline
        setSamples([
          {
            id: 'normal_metabolic_panel',
            title: 'Comprehensive Metabolic Panel',
            filename: 'sample_normal_lab_report.pdf',
            description: 'Routine blood chemistry panel with borderline fasting glucose.',
            page_count: 2,
          },
          {
            id: 'long_discharge_summary',
            title: 'Hospital Discharge Summary',
            filename: 'sample_long_discharge_summary.pdf',
            description: 'Post-operative laparoscopic appendectomy discharge instructions.',
            page_count: 3,
          },
        ]);
      });
  }, []);


  const validateAndSelectFile = (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') {
      onError('Unsupported file type. Please select a valid PDF (.pdf) document.');
      return;
    }

    const maxBytes = 10 * 1024 * 1024; // 10 MB
    if (file.size > maxBytes) {
      onError(`File size exceeds 10 MB limit (${(file.size / (1024 * 1024)).toFixed(1)} MB provided).`);
      return;
    }

    if (file.size === 0) {
      onError('Selected file is empty (0 bytes).');
      return;
    }

    onFileSelect(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isProcessing) setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (isProcessing) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSelectFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSelectFile(e.target.files[0]);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      {/* Drag & Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !isProcessing && fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-3xl p-8 sm:p-12 text-center transition-all cursor-pointer ${
          isDragging
            ? 'border-teal-500 bg-teal-50/80 scale-[1.01]'
            : 'border-slate-300 hover:border-teal-400 bg-white hover:bg-slate-50/50 shadow-soft-card'
        } ${isProcessing ? 'pointer-events-none opacity-60' : ''}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleFileInputChange}
          className="hidden"
          disabled={isProcessing}
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-teal-50 text-teal-600 flex items-center justify-center ring-8 ring-teal-50/50">
            <UploadCloud className="w-8 h-8" />
          </div>

          <div className="space-y-1.5">
            <h3 className="text-lg font-bold text-slate-900 tracking-tight">
              Upload your healthcare document
            </h3>
            <p className="text-xs sm:text-sm text-slate-500 max-w-sm mx-auto">
              Drag and drop your PDF here, or <span className="text-teal-600 font-semibold underline underline-offset-2">browse files</span>
            </p>
          </div>

          <div className="pt-2 flex items-center gap-3 text-[11px] text-slate-400">
            <span>PDF files up to 10 MB</span>
            <span>•</span>
            <span>Multi-page reports supported</span>
          </div>
        </div>
      </div>

      {/* Synthetic Benchmark Sample Document Quick Loader */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-700 tracking-wide uppercase flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-teal-600" />
            Or evaluate with a synthetic sample document
          </span>
          <span className="text-[11px] text-slate-400">One-click testing</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {samples.map((sample) => (
            <button
              key={sample.id}
              onClick={() => onSampleSelect(sample.id)}
              disabled={isProcessing}
              className="p-4 rounded-xl border border-slate-200 bg-white hover:border-teal-300 hover:bg-teal-50/40 text-left transition-all shadow-sm hover:shadow group focus-ring disabled:opacity-50"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start gap-2.5">
                  <div className="p-2 rounded-lg bg-teal-50 text-teal-700 group-hover:bg-teal-600 group-hover:text-white transition-colors">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-900 group-hover:text-teal-950">
                      {sample.title}
                    </h4>
                    <p className="text-[11px] text-slate-500 line-clamp-2 mt-0.5">
                      {sample.description}
                    </p>
                    <span className="inline-block mt-2 text-[10px] text-teal-700 font-semibold bg-teal-50 px-2 py-0.5 rounded-md">
                      {sample.page_count} Pages
                    </span>
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-300 group-hover:text-teal-600 group-hover:translate-x-0.5 transition-all flex-shrink-0 mt-1" />
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
