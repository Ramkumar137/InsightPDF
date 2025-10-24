// src/hooks/useDownload.ts
export async function downloadSummary(
  summaryId: string,
  format: 'txt' | 'pdf' | 'docx'
) {
  const token = await getAuthToken();
  
  const response = await fetch(
    `${API_BASE_URL}/api/summaries/${summaryId}/download?format=${format}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  if (!response.ok) {
    throw new Error('Download failed');
  }
  
  // Get filename from Content-Disposition header
  const contentDisposition = response.headers.get('Content-Disposition');
  const filenameMatch = contentDisposition?.match(/filename="(.+)"/);
  const filename = filenameMatch ? filenameMatch[1] : `summary.${format}`;
  
  // Download file
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}