import React from 'react';
import { FileText, X, Sparkles, Loader2 } from 'lucide-react';

interface FilePreviewProps {
  file: File;
  isProcessing: boolean;
  onRemove: () => void;
  onAnalyze: () => void;
}

export const FilePreview: React.FC<FilePreviewProps> = ({
  file,
  isProcessing,
  onRemove,
  onAnalyze,
}) => {
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-soft-card max-w-xl mx-auto">
      <div className="flex items-center justify-between gap-4">
        {/* File Details */}
        <div className="flex items-center gap-3.5 min-w-0">
          <div className="w-12 h-12 rounded-xl bg-teal-50 border border-teal-200 text-teal-700 flex items-center justify-center flex-shrink-0">
            <FileText className="w-6 h-6" />
          </div>
          <div className="truncate">
            <h4 className="text-sm font-semibold text-slate-900 truncate" title={file.name}>
              {file.name}
            </h4>
            <p className="text-xs text-slate-500 mt-0.5">
              PDF Document • {formatFileSize(file.size)}
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {!isProcessing && (
            <button
              onClick={onRemove}
              className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors focus-ring"
              title="Remove file"
              aria-label="Remove file"
            >
              <X className="w-5 h-5" />
            </button>
          )}

          <button
            onClick={onAnalyze}
            disabled={isProcessing}
            className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white shadow-md transition-all focus-ring ${
              isProcessing
                ? 'bg-teal-400 cursor-not-allowed'
                : 'bg-teal-600 hover:bg-teal-700 hover:shadow-lg hover:-translate-y-0.5 active:translate-y-0'
            }`}
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Analyze Document</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
