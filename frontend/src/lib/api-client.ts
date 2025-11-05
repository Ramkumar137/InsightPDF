/**
 * API Client - FIXED: All endpoint URLs corrected
 */

import { supabase } from "@/integrations/supabase/client";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

console.log('🔧 API Client Configuration:', { API_BASE_URL });

async function getAuthToken(): Promise<string | null> {
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token || null;
}

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

export async function uploadAndSummarize(
  files: File[],
  contextType: string,
  userRole: string = "professional",
  isPrivate: boolean = false
): Promise<any> {
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
    formData.append("userRole", userRole);
    formData.append("isPrivate", String(isPrivate));

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

export async function refineSummary(
  summaryId: string,
  action: "shorten" | "refine" | "regenerate" | "shorter" | "detailed" | "focus_methods" | "focus_results",
  focusArea?: string
): Promise<any> {
  try {
    const token = await getAuthToken();
    if (!token) {
      throw new Error("Not authenticated");
    }

    const formData = new FormData();
    formData.append("action", action);
    if (focusArea) {
      formData.append("focusArea", focusArea);
    }

    const url = `${API_BASE_URL}/api/summarize/${summaryId}/refine`;
    console.log('🔄 Refining at:', url, 'Action:', action, 'Focus:', focusArea || 'none');

    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    console.log('📥 Refine response:', response.status);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || "Failed to refine summary");
    }

    const data = await response.json();
    console.log('✅ Refined:', data);
    return data;
  } catch (error) {
    return handleApiError(error);
  }
}

export async function getSummaryHistory(
  limit: number = 50,
  offset: number = 0
): Promise<any> {
  try {
    const token = await getAuthToken();
    if (!token) {
      throw new Error("Not authenticated");
    }

    const url = `${API_BASE_URL}/api/summaries?limit=${limit}&offset=${offset}`;
    console.log('📚 Fetching history from:', url);

    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    console.log('📥 History response:', response.status);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error?.message || "Failed to fetch summaries");
    }

    const data = await response.json();
    console.log('✅ History loaded:', data.summaries?.length, 'summaries');
    return data;
  } catch (error) {
    console.error('❌ History fetch error:', error);
    return handleApiError(error);
  }
}

export async function getSummary(summaryId: string): Promise<any> {
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

    const contentDisposition = response.headers.get("Content-Disposition");
    const filenameMatch = contentDisposition?.match(/filename="(.+)"/);
    const filename = filenameMatch ? filenameMatch[1] : `summary.${format}`;

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

export async function checkApiHealth(): Promise<boolean> {
  try {
    console.log('🏥 Checking API health');
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(3000)
    });
    const isHealthy = response.ok;
    console.log(isHealthy ? '✅ API healthy' : '❌ API unhealthy');
    return isHealthy;
  } catch (error) {
    console.error('❌ Health check failed:', error);
    return false;
  }
}