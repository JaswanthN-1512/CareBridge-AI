import React, { useState } from 'react';
import { ChatMessage as ChatMessageType } from '../types';
import { SourceReference } from './SourceReference';
import { useToast } from './Toast';
import {
  ShieldCheck,
  AlertCircle,
  Copy,
  Check,
  User,
  Bot,
  FileCheck2,
} from 'lucide-react';

interface ChatMessageProps {
  message: ChatMessageType;
  onAskFollowUp?: (query: string) => void;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const [copied, setCopied] = useState(false);
  const { showToast } = useToast();
  const isUser = message.role === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    showToast('Message text copied to clipboard!', 'success');
    setTimeout(() => setCopied(false), 2000);
  };

  // Helper to format text with bullet points or paragraphs cleanly
  const renderFormattedContent = (content: string) => {
    const lines = content.split('\n');
    return (
      <div className="space-y-2 text-sm leading-relaxed">
        {lines.map((line, idx) => {
          const trimmed = line.trim();
          if (!trimmed) {
            return <div key={idx} className="h-1.5" />;
          }

          // Bullet point line
          if (trimmed.startsWith('- ') || trimmed.startsWith('• ') || trimmed.startsWith('* ')) {
            return (
              <div key={idx} className="flex items-start gap-2 pl-2">
                <span className="text-teal-600 font-bold text-base leading-none mt-0.5">•</span>
                <span className="flex-1">{trimmed.substring(2)}</span>
              </div>
            );
          }

          // Numbered list item (e.g. "1. ")
          const matchNum = trimmed.match(/^(\d+)\.\s+(.*)/);
          if (matchNum) {
            return (
              <div key={idx} className="flex items-start gap-2 pl-2">
                <span className="text-teal-700 font-bold text-xs bg-teal-50 px-1.5 py-0.5 rounded border border-teal-200 mt-0.5">
                  {matchNum[1]}
                </span>
                <span className="flex-1">{matchNum[2]}</span>
              </div>
            );
          }

          return <p key={idx}>{line}</p>;
        })}
      </div>
    );
  };

  if (isUser) {
    return (
      <div className="flex justify-end gap-3 items-start animate-in fade-in duration-200">
        <div className="max-w-[85%] sm:max-w-[75%] space-y-1">
          <div className="p-4 rounded-2xl rounded-tr-xs bg-slate-900 text-white shadow-md text-sm leading-relaxed selection:bg-teal-500 selection:text-white">
            <p className="whitespace-pre-wrap">{message.content}</p>
          </div>
          <div className="flex items-center justify-end gap-2 text-[10px] text-slate-400 px-1">
            <span>{message.timestamp}</span>
            <span>•</span>
            <span className="font-semibold text-slate-500">You</span>
          </div>
        </div>

        <div className="w-8 h-8 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center flex-shrink-0 mt-1 shadow-xs border border-slate-300">
          <User className="w-4 h-4" />
        </div>
      </div>
    );
  }

  // Assistant Response
  const isGrounded = message.isGrounded !== false;
  const sources = message.sources || [];

  return (
    <div className="flex justify-start gap-3 items-start animate-in fade-in duration-200">
      {/* Bot Avatar */}
      <div className="w-8 h-8 rounded-full bg-teal-600 text-white flex items-center justify-center flex-shrink-0 mt-1 shadow-sm border border-teal-700">
        <Bot className="w-4 h-4" />
      </div>

      {/* Main Message Bubble */}
      <div className="max-w-[92%] sm:max-w-[85%] space-y-3 flex-1">
        <div className="p-5 rounded-2xl rounded-tl-xs bg-white border border-slate-200 shadow-soft-card space-y-4">
          {/* Header Row: Sender + Grounding Badge + Copy Button */}
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-2.5">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-900 tracking-tight">
                CareBridge AI Assistant
              </span>
              <span className="text-[10px] text-slate-400">
                {message.timestamp}
              </span>
            </div>

            <div className="flex items-center gap-2">
              {/* Grounding Status Pill */}
              {isGrounded ? (
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Grounded in Records</span>
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-800 border border-amber-200">
                  <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                  <span>Context Unverified</span>
                </span>
              )}

              {/* Copy Response Button */}
              <button
                type="button"
                onClick={handleCopy}
                className="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
                title="Copy answer"
                aria-label="Copy answer to clipboard"
              >
                {copied ? (
                  <Check className="w-3.5 h-3.5 text-emerald-600" />
                ) : (
                  <Copy className="w-3.5 h-3.5" />
                )}
              </button>
            </div>
          </div>

          {/* Formatted Content */}
          <div className="text-slate-800 font-normal">
            {renderFormattedContent(message.content)}
          </div>

          {/* Source Citations Section */}
          {sources.length > 0 && (
            <div className="border-t border-slate-100 pt-3 space-y-2">
              <div className="flex items-center gap-1.5 text-slate-600 text-xs font-semibold">
                <FileCheck2 className="w-4 h-4 text-teal-600" />
                <span>Source Citations ({sources.length})</span>
              </div>

              <div className="grid grid-cols-1 gap-2">
                {sources.map((source, idx) => (
                  <SourceReference
                    key={idx}
                    source={source}
                    index={idx}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Safety Footnote */}
          <div className="border-t border-slate-100 pt-2 text-[10px] text-slate-400 flex items-center justify-between gap-2">
            <span>Answers synthesized from uploaded document excerpts. Not a substitute for professional clinical advice.</span>
          </div>
        </div>
      </div>
    </div>
  );
};
