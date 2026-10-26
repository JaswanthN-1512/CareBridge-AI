/**
 * Axios API service gateway for communicating with the CareBridge AI backend.
 */

import axios, { AxiosError } from 'axios';
import {
  DocumentUploadResponse,
  DocumentAnalysisResponse,
  DocumentChatResponse,
  SampleDocumentMeta,
} from '../types';

// In development, Vite proxies '/api' to 'http://localhost:8000/api'
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Accept': 'application/json',
  },
  timeout: 60000, // 60s timeout for multi-page document analyses
});

export function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ message?: string; detail?: string }>;
    if (axiosError.response?.data?.message) {
      return axiosError.response.data.message;
    }
    if (axiosError.response?.data?.detail) {
      return typeof axiosError.response.data.detail === 'string'
        ? axiosError.response.data.detail
        : JSON.stringify(axiosError.response.data.detail);
    }
    if (axiosError.message) {
      return axiosError.message;
    }
  }
  return error instanceof Error ? error.message : 'An unexpected network error occurred.';
}

export const apiService = {
  /**
   * Upload and index a PDF document via multipart/form-data.
   */
  async uploadPDF(
    file: File,
    onProgress?: (percent: number) => void,
  ): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<DocumentUploadResponse>('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      },
    });
    return response.data;
  },

  /**
   * Trigger multi-prompt document intelligence analysis.
   */
  async analyzeDocument(documentId: string): Promise<DocumentAnalysisResponse> {
    const response = await apiClient.post<DocumentAnalysisResponse>('/api/analyze', {
      document_id: documentId,
    });
    return response.data;
  },

  /**
   * Send a question to the document's RAG knowledge index.
   */
  async askQuestion(documentId: string, question: string): Promise<DocumentChatResponse> {
    const response = await apiClient.post<DocumentChatResponse>('/api/chat', {
      document_id: documentId,
      question: question.trim(),
    });
    return response.data;
  },

  /**
   * Fetch list of synthetic demonstration documents.
   */
  async getSamples(): Promise<SampleDocumentMeta[]> {
    const response = await apiClient.get<SampleDocumentMeta[]>('/api/samples');
    return response.data;
  },

  /**
   * Load and index a pre-configured synthetic sample document.
   */
  async loadSample(sampleId: string): Promise<DocumentUploadResponse> {
    const response = await apiClient.post<DocumentUploadResponse>(`/api/samples/${sampleId}/load`);
    return response.data;
  },

  /**
   * Check backend health and operational status.
   */
  async getHealth(): Promise<{ status: string; environment: string; llm_provider: string }> {
    const response = await apiClient.get('/api/health');
    return response.data;
  },
};
