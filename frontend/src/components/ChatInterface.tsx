import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage as ChatMessageType, SourceReference } from '../types';
import { ChatMessage } from './ChatMessage';
import { apiService, getApiErrorMessage } from '../services/api';
import {
  Send,
  Sparkles,
  RotateCcw,
  AlertTriangle,
  Bot,
  HelpCircle,
  FileQuestion,
  CornerDownLeft,
  PhoneCall,
  Loader2,
} from 'lucide-react';

interface ChatInterfaceProps {
  documentId: string;
  documentType?: string;
  suggestedQuestions?: string[];
  externalTriggerQuery?: string | null;
  onClearExternalTrigger?: () => void;
}

// Emergency trigger keywords for immediate clinical safety guardrail
const EMERGENCY_KEYWORDS = [
  'chest pain',
  'heart attack',
  'shortness of breath',
  'cant breathe',
  "can't breathe",
  'difficulty breathing',
  'stroke',
  'suicide',
  'suicidal',
  'kill myself',
  'overdose',
  'severe bleeding',
  'unconscious',
  'anaphylaxis',
];

const DEFAULT_SUGGESTIONS = [
  'Explain my key lab results and any abnormal flags in plain English.',
  'What are my next scheduled appointments and follow-up tests?',
  'What medications or prescriptions are listed in this report?',
  'Are there any dietary or physical activity restrictions mentioned?',
];

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  documentId,
  documentType = 'Medical Document',
  suggestedQuestions = [],
  externalTriggerQuery,
  onClearExternalTrigger,
}) => {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [emergencyAlert, setEmergencyAlert] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Handle external query trigger (e.g., clicked from Doctor Questions component)
  useEffect(() => {
    if (externalTriggerQuery && externalTriggerQuery.trim()) {
      handleSendMessage(externalTriggerQuery.trim());
      if (onClearExternalTrigger) {
        onClearExternalTrigger();
      }
    }
  }, [externalTriggerQuery]);

  const checkEmergencyKeywords = (text: string): boolean => {
    const lower = text.toLowerCase();
    return EMERGENCY_KEYWORDS.some((kw) => lower.includes(kw));
  };

  const handleSendMessage = async (queryText?: string) => {
    const query = (queryText || inputQuery).trim();
    if (!query || isLoading) return;

    setErrorMessage(null);

    // Check emergency guardrail
    if (checkEmergencyKeywords(query)) {
      setEmergencyAlert(
        'Immediate Medical Notice: Your query mentions acute medical emergency symptoms. If you or someone you are caring for is in distress, please immediately call 911 (US) or your local emergency services, or proceed to the nearest emergency room. CareBridge AI is an informational tool and cannot assist in urgent medical crises.'
      );
    } else {
      setEmergencyAlert(null);
    }

    const userMessage: ChatMessageType = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!queryText) {
      setInputQuery('');
    }
    setIsLoading(true);

    try {
      const response = await apiService.askQuestion(documentId, query);

      const assistantMessage: ChatMessageType = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.answer,
        sources: response.sources as SourceReference[],
        isGrounded: response.is_grounded,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setErrorMessage(getApiErrorMessage(err));
    } finally {
      setIsLoading(false);
      // Re-focus input
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleClearChat = () => {
    if (messages.length > 0 && window.confirm('Clear conversation history for this document?')) {
      setMessages([]);
      setErrorMessage(null);
      setEmergencyAlert(null);
    }
  };

  // Compile prompt suggestions
  const promptSuggestions = [
    ...suggestedQuestions.slice(0, 3),
    ...DEFAULT_SUGGESTIONS,
  ].slice(0, 5);

  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-soft-card flex flex-col h-[700px] overflow-hidden">
      {/* Chat Pane Header */}
      <div className="p-4 sm:p-5 border-b border-slate-200 bg-slate-50/70 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-teal-600 text-white flex items-center justify-center shadow-xs flex-shrink-0">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-slate-900 tracking-tight">
                Ask Document • RAG Assistant
              </h3>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Indexed & Ready
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Grounded specifically in <span className="font-medium text-slate-700">{documentType}</span>
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {messages.length > 0 && (
            <button
              type="button"
              onClick={handleClearChat}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 text-slate-600 text-xs font-semibold transition-colors"
              title="Reset conversation"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>

      {/* Emergency Guidance Banner */}
      {emergencyAlert && (
        <div className="bg-rose-50 border-b border-rose-200 p-3 sm:p-4 text-xs text-rose-900 flex items-start gap-2.5 animate-in fade-in duration-200">
          <PhoneCall className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5 animate-bounce" />
          <div className="space-y-1">
            <span className="font-bold uppercase tracking-wide text-rose-800 block text-[11px]">
              Emergency Protocol Activated
            </span>
            <p className="leading-relaxed">{emergencyAlert}</p>
          </div>
        </div>
      )}

      {/* Messages Scroll Area */}
      <div className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-6 bg-slate-50/30">
        {/* Welcome Empty State */}
        {messages.length === 0 && (
          <div className="max-w-xl mx-auto py-8 text-center space-y-6 animate-in fade-in duration-300">
            <div className="w-14 h-14 rounded-2xl bg-teal-50 border border-teal-200 text-teal-600 flex items-center justify-center mx-auto shadow-xs">
              <Sparkles className="w-7 h-7" />
            </div>

            <div className="space-y-2">
              <h4 className="text-lg font-bold text-slate-900">
                What would you like to know about this record?
              </h4>
              <p className="text-xs text-slate-500 leading-relaxed max-w-md mx-auto">
                CareBridge AI performs semantic vector searches across your document pages to give exact answers backed by page citations.
              </p>
            </div>

            {/* Starter Suggestion Pills */}
            <div className="text-left space-y-2 pt-2">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block px-1">
                Suggested Questions
              </span>
              <div className="grid grid-cols-1 gap-2">
                {promptSuggestions.map((prompt, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSendMessage(prompt)}
                    className="p-3 text-left rounded-xl border border-slate-200 bg-white hover:border-teal-400 hover:bg-teal-50/40 transition-all text-xs font-medium text-slate-700 flex items-center justify-between gap-3 group shadow-2xs"
                  >
                    <div className="flex items-center gap-2">
                      <HelpCircle className="w-3.5 h-3.5 text-teal-600 flex-shrink-0" />
                      <span>{prompt}</span>
                    </div>
                    <CornerDownLeft className="w-3.5 h-3.5 text-slate-300 group-hover:text-teal-600 transition-colors flex-shrink-0" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Render Conversation Messages */}
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
            onAskFollowUp={handleSendMessage}
          />
        ))}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex justify-start gap-3 items-start animate-in fade-in duration-200">
            <div className="w-8 h-8 rounded-full bg-teal-600 text-white flex items-center justify-center flex-shrink-0 mt-1 shadow-sm">
              <Bot className="w-4 h-4" />
            </div>
            <div className="p-4 rounded-2xl rounded-tl-xs bg-white border border-slate-200 shadow-soft-card flex items-center gap-3">
              <Loader2 className="w-4 h-4 text-teal-600 animate-spin" />
              <div className="space-y-1">
                <span className="text-xs font-semibold text-slate-700">
                  Synthesizing answer from document embeddings...
                </span>
                <span className="text-[11px] text-slate-400 block">
                  Grounding citations against source pages
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Error Notification */}
        {errorMessage && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-600 flex-shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              type="button"
              onClick={() => setErrorMessage(null)}
              className="font-bold underline hover:text-rose-950"
            >
              Dismiss
            </button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Chips Bar (When active conversation exists) */}
      {messages.length > 0 && !isLoading && (
        <div className="px-4 py-2 border-t border-slate-100 bg-slate-50/50 flex items-center gap-2 overflow-x-auto no-scrollbar">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1 flex-shrink-0">
            <FileQuestion className="w-3 h-3 text-teal-600" />
            Suggested:
          </span>
          {promptSuggestions.slice(0, 3).map((prompt, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSendMessage(prompt)}
              className="px-2.5 py-1 rounded-full border border-slate-200 bg-white hover:bg-teal-50 hover:border-teal-300 text-slate-600 hover:text-teal-900 text-[11px] font-medium transition-colors flex-shrink-0 truncate max-w-xs"
              title={prompt}
            >
              {prompt}
            </button>
          ))}
        </div>
      )}

      {/* Input Area */}
      <div className="p-3 sm:p-4 border-t border-slate-200 bg-white">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="relative flex items-center gap-2"
        >
          <textarea
            ref={inputRef}
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about this document... (e.g., 'What were my cholesterol numbers?')"
            rows={1}
            disabled={isLoading}
            className="w-full px-4 py-3 pr-12 rounded-xl border border-slate-200 focus:border-teal-500 focus:ring-2 focus:ring-teal-100 outline-none text-sm text-slate-800 placeholder-slate-400 resize-none transition-all disabled:opacity-60 disabled:bg-slate-50"
            style={{ maxHeight: '120px' }}
          />

          <button
            type="submit"
            disabled={!inputQuery.trim() || isLoading}
            className="absolute right-2.5 p-2 rounded-lg bg-teal-600 hover:bg-teal-700 text-white disabled:opacity-40 disabled:hover:bg-teal-600 transition-colors cursor-pointer shadow-xs"
            title="Send query (Enter)"
            aria-label="Send query"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </form>

        <div className="flex items-center justify-between text-[11px] text-slate-400 mt-2 px-1">
          <span>Press <kbd className="px-1 py-0.5 rounded bg-slate-100 border border-slate-200 text-[10px] font-mono text-slate-600">Enter ↵</kbd> to send</span>
          <span>Information grounded in document pages</span>
        </div>
      </div>
    </div>
  );
};
