import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Hero } from './components/Hero';
import { UploadBox } from './components/UploadBox';
import { FilePreview } from './components/FilePreview';
import { ProcessingStatus } from './components/ProcessingStatus';
import { SummaryCard } from './components/SummaryCard';
import { KeyInformationCard } from './components/KeyInformationCard';
import { ActionChecklist } from './components/ActionChecklist';
import { DoctorQuestions } from './components/DoctorQuestions';
import { ChatInterface } from './components/ChatInterface';
import { SafetyNotice } from './components/SafetyNotice';
import { ErrorState } from './components/ErrorState';
import {
  DocumentUploadResponse,
  DocumentAnalysisResponse,
  ProcessingStatus as StatusType,
} from './types';
import { apiService, getApiErrorMessage } from './services/api';
import { FileText, Database, CheckSquare, HelpCircle, LayoutGrid, Bot } from 'lucide-react';

export function App() {
  const [backendHealth, setBackendHealth] = useState<string>('Checking...');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [activeDocument, setActiveDocument] = useState<DocumentUploadResponse | null>(null);
  const [analysisReport, setAnalysisReport] = useState<DocumentAnalysisResponse | null>(null);
  const [processingStatus, setProcessingStatus] = useState<StatusType>('idle');
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'all' | 'summary' | 'key_info' | 'actions' | 'questions' | 'chat'>('all');
  const [externalChatQuery, setExternalChatQuery] = useState<string | null>(null);

  useEffect(() => {
    apiService.getHealth()
      .then((data) => setBackendHealth(`${data.status} • ${data.llm_provider.toUpperCase()}`))
      .catch(() => setBackendHealth('Offline (Demo Ready)'));
  }, []);

  const handleReset = () => {
    setSelectedFile(null);
    setActiveDocument(null);
    setAnalysisReport(null);
    setProcessingStatus('idle');
    setUploadProgress(0);
    setErrorMessage(null);
    setActiveTab('all');
    setExternalChatQuery(null);
  };

  const handleAskDoctorQuestion = (question: string) => {
    setExternalChatQuery(question);
    setActiveTab('chat');
  };

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setErrorMessage(null);
  };

  const handleStartAnalysis = async () => {
    if (!selectedFile) return;

    try {
      setErrorMessage(null);
      setProcessingStatus('reading');
      setUploadProgress(15);

      // 1. Upload & Vectorize
      const uploadRes = await apiService.uploadPDF(selectedFile, (progress) => {
        setUploadProgress(progress);
        if (progress >= 100) {
          setProcessingStatus('extracting');
        }
      });

      setActiveDocument(uploadRes);
      setProcessingStatus('analyzing');

      // 2. Structured Analysis
      const analysisRes = await apiService.analyzeDocument(uploadRes.document_id);
      setAnalysisReport(analysisRes);
      setProcessingStatus('ready');

    } catch (err) {
      setProcessingStatus('error');
      setErrorMessage(getApiErrorMessage(err));
    }
  };

  const handleSampleSelect = async (sampleId: string) => {
    try {
      setErrorMessage(null);
      setProcessingStatus('reading');
      setUploadProgress(40);

      // 1. Load Synthetic Benchmark Sample
      const uploadRes = await apiService.loadSample(sampleId);
      setActiveDocument(uploadRes);
      setProcessingStatus('analyzing');

      // 2. Multi-prompt Analysis
      const analysisRes = await apiService.analyzeDocument(uploadRes.document_id);
      setAnalysisReport(analysisRes);
      setProcessingStatus('ready');

    } catch (err) {
      setProcessingStatus('error');
      setErrorMessage(getApiErrorMessage(err));
    }
  };

  const isWorking = processingStatus !== 'idle' && processingStatus !== 'ready' && processingStatus !== 'error';

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800">
      {/* Top Header & Navbar */}
      <Navbar
        backendStatus={backendHealth}
        hasActiveDocument={Boolean(activeDocument || selectedFile)}
        hasAnalysis={Boolean(analysisReport)}
        onReset={handleReset}
      />

      {/* Global Safety Alert Banner (hidden on print) */}
      <div className="no-print bg-amber-50/90 border-b border-amber-200 px-4 py-2 text-xs text-amber-900 text-center font-medium">
        <span>Informational Healthcare Document Navigator • Does not provide diagnoses or treatment plans • In an emergency call 911</span>
      </div>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
        {/* Error Notification */}
        {errorMessage && (
          <div className="no-print max-w-2xl mx-auto mb-6">
            <ErrorState
              message={errorMessage}
              onDismiss={() => setErrorMessage(null)}
              onRetry={selectedFile ? handleStartAnalysis : undefined}
            />
          </div>
        )}

        {/* View 1: Ingestion & Upload Experience (Before Analysis) */}
        {!analysisReport && (
          <div className="space-y-8 animate-in fade-in duration-300">
            <Hero />

            {/* Stepper Display during processing */}
            {isWorking && (
              <ProcessingStatus
                status={processingStatus}
                uploadProgress={uploadProgress}
              />
            )}

            {/* Selected File Card before triggering analysis */}
            {selectedFile && !isWorking && (
              <FilePreview
                file={selectedFile}
                isProcessing={isWorking}
                onRemove={() => setSelectedFile(null)}
                onAnalyze={handleStartAnalysis}
              />
            )}

            {/* Drag & Drop Zone + Sample Picker */}
            {!selectedFile && !isWorking && (
              <UploadBox
                onFileSelect={handleFileSelect}
                onSampleSelect={handleSampleSelect}
                isProcessing={isWorking}
                onError={(msg) => setErrorMessage(msg)}
              />
            )}
          </div>
        )}

        {/* View 2: Analysis Dashboard (When Report is Ready) */}
        {analysisReport && (
          <div className="space-y-8 animate-in fade-in duration-300">
            {/* Dedicated Print-Only Clinical Encounter Header */}
            <div className="hidden print-only mb-6 border-b-2 border-slate-900 pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-black text-slate-900">CareBridge AI — Consultation Preparation Agenda</h1>
                  <p className="text-sm font-semibold text-slate-700 mt-1">
                    Document Category: {analysisReport.document_type}
                  </p>
                </div>
                <div className="text-right text-xs text-slate-500">
                  <p>Prepared for Clinical Encounter</p>
                  <p>{new Date().toLocaleDateString()}</p>
                </div>
              </div>
              <p className="text-xs text-slate-600 mt-2 italic">
                Notice for Attending Clinician: This patient-prepared discussion agenda synthesizes key documented findings 
                and formulated questions. All conclusions are educational and subject to your clinical evaluation.
              </p>
            </div>

            {/* Dashboard Header Bar & Tab Switcher (hidden on print) */}
            <div className="no-print bg-white border border-slate-200 rounded-2xl p-4 sm:p-5 shadow-soft-card flex flex-wrap items-center justify-between gap-4">
              <div>
                <span className="text-[11px] font-bold text-teal-700 tracking-wider uppercase block">
                  AI Document Analysis
                </span>
                <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">
                  {analysisReport.document_type}
                </h2>
              </div>

              {/* Navigation Tabs with Accessibility Roles */}
              <div
                role="tablist"
                aria-label="Document analysis sections"
                className="no-scrollbar flex items-center gap-1.5 bg-slate-100 p-1.5 rounded-xl border border-slate-200/80 text-xs font-semibold overflow-x-auto max-w-full"
              >
                <button
                  role="tab"
                  aria-selected={activeTab === 'all'}
                  onClick={() => setActiveTab('all')}
                  className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all whitespace-nowrap focus-ring ${
                    activeTab === 'all'
                      ? 'bg-white text-slate-900 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <LayoutGrid className="w-3.5 h-3.5" />
                  <span>Overview</span>
                </button>

                <button
                  role="tab"
                  aria-selected={activeTab === 'summary'}
                  onClick={() => setActiveTab('summary')}
                  className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all whitespace-nowrap focus-ring ${
                    activeTab === 'summary'
                      ? 'bg-white text-slate-900 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>Summary</span>
                </button>

                <button
                  role="tab"
                  aria-selected={activeTab === 'key_info'}
                  onClick={() => setActiveTab('key_info')}
                  className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all whitespace-nowrap focus-ring ${
                    activeTab === 'key_info'
                      ? 'bg-white text-slate-900 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <Database className="w-3.5 h-3.5" />
                  <span>Key Findings</span>
                </button>

                <button
                  role="tab"
                  aria-selected={activeTab === 'actions'}
                  onClick={() => setActiveTab('actions')}
                  className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all whitespace-nowrap focus-ring ${
                    activeTab === 'actions'
                      ? 'bg-white text-slate-900 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <CheckSquare className="w-3.5 h-3.5" />
                  <span>Actions</span>
                </button>

                <button
                  role="tab"
                  aria-selected={activeTab === 'questions'}
                  onClick={() => setActiveTab('questions')}
                  className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all whitespace-nowrap focus-ring ${
                    activeTab === 'questions'
                      ? 'bg-white text-slate-900 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                  <span>Doctor Questions</span>
                </button>

                <button
                  role="tab"
                  aria-selected={activeTab === 'chat'}
                  onClick={() => setActiveTab('chat')}
                  className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all whitespace-nowrap focus-ring ${
                    activeTab === 'chat'
                      ? 'bg-teal-600 text-white shadow-sm'
                      : 'text-teal-700 hover:text-teal-900 hover:bg-teal-50'
                  }`}
                >
                  <Bot className="w-3.5 h-3.5" />
                  <span>Ask Document (Chat)</span>
                </button>
              </div>
            </div>

            {/* Dashboard Content Grid */}
            <div className="space-y-6">
              {(activeTab === 'all' || activeTab === 'summary') && (
                <div className="card-print">
                  <SummaryCard
                    analysis={analysisReport}
                    documentMeta={activeDocument}
                  />
                </div>
              )}

              {(activeTab === 'all' || activeTab === 'key_info') && (
                <div className="card-print">
                  <KeyInformationCard
                    items={analysisReport.key_information}
                  />
                </div>
              )}

              {(activeTab === 'all' || activeTab === 'actions') && (
                <div className="card-print">
                  <ActionChecklist
                    initialActions={analysisReport.action_items}
                  />
                </div>
              )}

              {(activeTab === 'all' || activeTab === 'questions') && (
                <div className="card-print">
                  <DoctorQuestions
                    questions={analysisReport.questions_for_clinician}
                    onAskQuestion={handleAskDoctorQuestion}
                  />
                </div>
              )}

              {(activeTab === 'all' || activeTab === 'chat') && activeDocument && (
                <div className={`no-print ${activeTab === 'all' ? 'pt-2' : ''}`}>
                  {activeTab === 'all' && (
                    <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <Bot className="w-5 h-5 text-teal-600" />
                        <h3 className="text-lg font-bold text-slate-900 tracking-tight">
                          Interactive Document Q&A (RAG Assistant)
                        </h3>
                      </div>
                      <span className="text-xs text-slate-500">
                        Ask any question to receive grounded responses with exact page citations
                      </span>
                    </div>
                  )}
                  <ChatInterface
                    documentId={activeDocument.document_id}
                    documentType={analysisReport.document_type}
                    suggestedQuestions={analysisReport.questions_for_clinician}
                    externalTriggerQuery={externalChatQuery}
                    onClearExternalTrigger={() => setExternalChatQuery(null)}
                  />
                </div>
              )}

              {/* Safety Banner */}
              <div className="card-print">
                <SafetyNotice />
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
        <p>© 2026 CareBridge AI. Built for healthcare document comprehension & clinical encounter preparation.</p>
      </footer>
    </div>
  );
}

export default App;
