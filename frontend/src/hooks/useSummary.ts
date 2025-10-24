// src/hooks/useSummary.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function useSummary(summaryId: string) {
  return useQuery({
    queryKey: ['summary', summaryId],
    queryFn: async () => {
      const token = await getAuthToken();
      const response = await fetch(
        `${API_BASE_URL}/api/summaries/${summaryId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      return response.json();
    },
    enabled: !!summaryId
  });
}

export function useRefineSummary() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ summaryId, action }: { summaryId: string, action: string }) => {
      const token = await getAuthToken();
      const formData = new FormData();
      formData.append('action', action);
      
      const response = await fetch(
        `${API_BASE_URL}/api/summaries/${summaryId}/refine`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        }
      );
      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries(['summary', data.summaryId]);
      queryClient.invalidateQueries(['summaries']);
    }
  });
}