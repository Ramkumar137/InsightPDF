import api from './api';

// ==========================================
// TYPES
// ==========================================
export interface SummaryResponse {
  summary_id: string;
  summary: string;
  context_type: string;
  file_names: string[];
  created_at: string;
}

export interface SummaryHistoryItem {
  summary_id: string;
  file_names: string[];
  context_type: string;
  created_at: string;
  updated_at?: string;
}

export type ContextType = 'executive' | 'student' | 'analyst' | 'general';
export type RefinementAction = 'shorten' | 'refine' | 'regenerate';
export type DownloadFormat = 'txt' | 'pdf' | 'docx';

// ==========================================
// SUMMARIZATION API
// ==========================================

/**
 * Upload PDFs and create summary
 */
export const createSummary = async (
  files: File[],
  contextType: ContextType
): Promise<SummaryResponse> => {
  const formData = new FormData();
  
  // Append all files
  files.forEach((file) => {
    formData.append('files', file);
  });
  
  // Append context type
  formData.append('context_type', contextType);
  
  try {
    const response = await api.post<SummaryResponse>('/summarize', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error: any) {
    console.error('Error creating summary:', error);
    throw new Error(
      error.response?.data?.detail || 'Failed to create summary'
    );
  }
};

/**
 * Refine existing summary
 */
export const refineSummary = async (
  summaryId: string,
  action: RefinementAction,
  contextType: ContextType
): Promise<SummaryResponse> => {
  try {
    const response = await api.post<SummaryResponse>(
      `/summarize`,
      null,
      {
        params: {
          action,
          summary_id: summaryId,
          context_type: contextType,
        },
      }
    );
    return response.data;
  } catch (error: any) {
    console.error('Error refining summary:', error);
    throw new Error(
      error.response?.data?.detail || 'Failed to refine summary'
    );
  }
};

/**
 * Get all user summaries
 */
export const getUserSummaries = async (): Promise<SummaryHistoryItem[]> => {
  try {
    const response = await api.get<SummaryHistoryItem[]>('/summaries');
    return response.data;
  } catch (error: any) {
    console.error('Error fetching summaries:', error);
    throw new Error(
      error.response?.data?.detail || 'Failed to fetch summaries'
    );
  }
};

/**
 * Get single summary by ID
 */
export const getSummary = async (summaryId: string): Promise<SummaryResponse> => {
  try {
    const response = await api.get<SummaryResponse>(`/summaries/${summaryId}`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching summary:', error);
    throw new Error(
      error.response?.data?.detail || 'Failed to fetch summary'
    );
  }
};

/**
 * Delete summary
 */
export const deleteSummary = async (summaryId: string): Promise<void> => {
  try {
    await api.delete(`/summaries/${summaryId}`);
  } catch (error: any) {
    console.error('Error deleting summary:', error);
    throw new Error(
      error.response?.data?.detail || 'Failed to delete summary'
    );
  }
};

// ==========================================
// DOWNLOAD API
// ==========================================

/**
 * Download summary in specified format
 */
export const downloadSummary = async (
  summaryId: string,
  format: DownloadFormat
): Promise<void> => {
  try {
    const response = await api.get('/download', {
      params: {
        summary_id: summaryId,
        type: format,
      },
      responseType: 'blob',
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `summary_${summaryId.substring(0, 8)}.${format}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error: any) {
    console.error('Error downloading summary:', error);
    throw new Error(
      error.response?.data?.detail || 'Failed to download summary'
    );
  }
};

// ==========================================
// HEALTH CHECK
// ==========================================

/**
 * Check API health
 */
export const checkAPIHealth = async (): Promise<boolean> => {
  try {
    const response = await api.get('/health');
    return response.status === 200;
  } catch (error) {
    console.error('API health check failed:', error);
    return false;
  }
};