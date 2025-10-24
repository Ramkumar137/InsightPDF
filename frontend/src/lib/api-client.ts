/**
 * API Client for PDF Summarizer Backend
 * UPDATED: Added debug logging and better error messages
 */

import { supabase } from "@/integrations/supabase/client";

// API Configuration - with debug logging
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

// Debug log on module load
console.log('🔧 API Client Configuration:', {
  VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
  API_BASE_URL,
  allEnvVars: import.meta.env
});

/**
 * Get authentication token from Supabase
 */
async function getAuthToken(): Promise<string | null> {
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token || null;
}

/**
 * Handle API errors with proper error messages
 */
function handleApiError(error: any): never {
  console.error('❌ API Error:', error);
  
  if (error.response) {
    const apiError = error.response.data?.error;
    if (apiError) {
      throw new Error(apiError.message);
    }
  }
  throw new Error(error.message || "An unexpected error occurred");
}

/**
 * Upload PDFs and generate summary
 */
export async function uploadAndSummarize(
  files: File[],
  contextType: string
): Promise<{
  summaryId: string;
  content: {
    overview: string;
    keyInsights: string;
    risks: string;
    recommendations: string;
  };
  metadata: {
    fileName: string;
    fileNames: string[];
    contextType: string;
    createdAt: string;
  };
}> {
  try {
    const token = await getAuthToken();
    console.log('🔑 Auth token:', token ? 'Present' : 'Missing');
    
    if (!token) {
      throw new Error("Not authenticated");
    }

    const formData = new FormData();
    files.forEach(file => {
      formData.append("files", file);
    });
    formData.append("contextType", contextType);

    const url = `${API_BASE_URL}/api/summarize`;
    console.log('📤 Uploading to:', url);

    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    console.log('📥 Response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json();
      console.error('❌ Error response:', errorData);
      throw new Error(errorData.error?.message || "Failed to generate summary");
    }

    const data = await response.json();
    console.log('✅ Success:', data);
    return data;
  } catch (error) {
    console.error('💥 Upload failed:', error);
    return handleApiError(error);
  }
}

/**
 * Refine an existing summary
 */
export async function refineSummary(
  summaryId: string,
  action: "shorten" | "refine" | "regenerate"
): Promise<{
  summaryId: string;
  content: {
    overview: string;
    keyInsights: string;
    risks: string;
    recommendations: string;
  };
  updatedAt: string;
}> {
  try {
    const token = await getAuthToken();
    if (!token) {
      throw new Error("Not authenticated");
    }

    const formData = new FormData();
    formData.append("action", action);

    const response = await fetch(
      `${API_BASE_URL}/api/summaries/${summaryId}/refine`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || "Failed to refine summary");
    }

    return await response.json();
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Get summary history
 */
export async function getSummaryHistory(
  limit: number = 50,
  offset: number = 0
): Promise<{
  summaries: Array<{
    id: string;
    fileName: string;
    contextType: string;
    timestamp: string;
    previewText: string;
  }>;
  total: number;
  limit: number;
  offset: number;
}> {
  try {
    const token = await getAuthToken();
    if (!token) {
      throw new Error("Not authenticated");
    }

    const response = await fetch(
      `${API_BASE_URL}/api/summaries?limit=${limit}&offset=${offset}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || "Failed to fetch summaries");
    }

    return await response.json();
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Get a specific summary by ID
 */
export async function getSummary(summaryId: string): Promise<{
  summaryId: string;
  content: {
    overview: string;
    keyInsights: string;
    risks: string;
    recommendations: string;
  };
  metadata: {
    fileName: string;
    fileNames: string[];
    contextType: string;
    createdAt: string;
    updatedAt: string;
  };
}> {
  try {
    const token = await getAuthToken();
    if (!token) {
      throw new Error("Not authenticated");
    }

    const response = await fetch(
      `${API_BASE_URL}/api/summaries/${summaryId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || "Failed to fetch summary");
    }

    return await response.json();
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Download summary in specified format
 */
export async function downloadSummary(
  summaryId: string,
  format: "txt" | "pdf" | "docx"
): Promise<void> {
  try {
    const token = await getAuthToken();
    if (!token) {
      throw new Error("Not authenticated");
    }

    const response = await fetch(
      `${API_BASE_URL}/api/summaries/${summaryId}/download?format=${format}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || "Failed to download summary");
    }

    // Get filename from Content-Disposition header
    const contentDisposition = response.headers.get("Content-Disposition");
    const filenameMatch = contentDisposition?.match(/filename="(.+)"/);
    const filename = filenameMatch ? filenameMatch[1] : `summary.${format}`;

    // Download file
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Delete a summary
 */
export async function deleteSummary(summaryId: string): Promise<void> {
  try {
    const token = await getAuthToken();
    if (!token) {
      throw new Error("Not authenticated");
    }

    const response = await fetch(
      `${API_BASE_URL}/api/summaries/${summaryId}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || "Failed to delete summary");
    }
  } catch (error) {
    return handleApiError(error);
  }
}

/**
 * Check API health - UPDATED with better error handling
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    console.log('🏥 Checking API health at:', `${API_BASE_URL}/health`);
    
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      // Add timeout
      signal: AbortSignal.timeout(5000)
    });
    
    const isHealthy = response.ok;
    console.log(isHealthy ? '✅ API is healthy' : '❌ API returned error');
    
    return isHealthy;
  } catch (error) {
    console.error('❌ API health check failed:', error);
    console.error('Attempted URL:', `${API_BASE_URL}/health`);
    return false;
  }
}