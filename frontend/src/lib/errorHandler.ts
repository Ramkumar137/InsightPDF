// src/lib/errorHandler.ts
export function handleApiError(error: any) {
  if (error.response) {
    const apiError = error.response.data.error;
    
    switch (apiError.code) {
      case 'UNAUTHORIZED':
      case 'TOKEN_EXPIRED':
        // Redirect to login
        window.location.href = '/login';
        break;
      case 'INVALID_FILE_TYPE':
        toast.error('Only PDF files are allowed');
        break;
      case 'FILE_TOO_LARGE':
        toast.error('File size exceeds 10MB limit');
        break;
      default:
        toast.error(apiError.message || 'An error occurred');
    }
  } else {
    toast.error('Network error. Please check your connection.');
  }
}