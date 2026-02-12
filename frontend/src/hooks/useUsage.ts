import { useQuery } from '@tanstack/react-query';
import { usageApi } from '../api/usage';

export const useUsage = () => {
  const usageQuery = useQuery({
    queryKey: ['usage', 'current-period'],
    queryFn: () => usageApi.getCurrentPeriod(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const historyQuery = useQuery({
    queryKey: ['usage', 'history'],
    queryFn: () => usageApi.getHistory(10),
    staleTime: 1000 * 60 * 1, // 1 minute
  });

  return {
    stats: usageQuery.data,
    history: historyQuery.data || [],
    isLoading: usageQuery.isLoading || historyQuery.isLoading,
    error: usageQuery.error || historyQuery.error,
    refetch: () => {
      usageQuery.refetch();
      historyQuery.refetch();
    },
  };
};
