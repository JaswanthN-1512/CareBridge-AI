/**
 * Shared TypeScript type definitions for CareBridge AI.
 * Aligned 1:1 with backend Pydantic models.
 */

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  file_size_bytes: number;
  total_pages: number;
  total_chunks: number;
  status: string;
  message: string;
}

export interface KeyInformationItem {
  category: string;
  label: string;
  value: string;
  source_page?: number | null;
}

export interface ActionItem {
  id: string;
  description: string;
  completed: boolean;
  source_page?: number | null;
}

export interface DocumentAnalysisResponse {
  document_id: string;
  document_type: string;
  summary: string;
  key_information: KeyInformationItem[];
  action_items: ActionItem[];
  questions_for_clinician: string[];
  safety_note: string;
}

export interface SourceReference {
  page: number;
  chunk_id?: number | null;
  snippet: string;
}

export interface DocumentChatResponse {
  document_id: string;
  question: string;
  answer: string;
  sources: SourceReference[];
  is_grounded: boolean;
}

export interface SampleDocumentMeta {
  id: string;
  title: string;
  filename: string;
  description: string;
  page_count: number;
}

export type ProcessingStatus =
  | 'idle'
  | 'reading'
  | 'extracting'
  | 'indexing'
  | 'analyzing'
  | 'ready'
  | 'error';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceReference[];
  isGrounded?: boolean;
  timestamp: string;
}
