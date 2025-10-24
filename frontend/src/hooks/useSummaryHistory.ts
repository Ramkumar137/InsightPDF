// src/hooks/useSummaryHistory.ts
import { useQuery } from '@tanstack/react-query';

export function useSummaryHistory() {
  return useQuery({
    queryKey: ['summaries'],
    queryFn: async () => {
      const token = await getAuthToken();
      const response = await fetch(
        `${API_BASE_URL}/api/summaries?limit=50&offset=0`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      const data = await response.json();
      return data.summaries;
    }
  });
}