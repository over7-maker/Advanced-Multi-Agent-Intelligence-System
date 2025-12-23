/**
 * Custom hook for API data fetching with loading and error states
 */

import { useEffect, useState } from 'react';

interface UseApiDataResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useApiData<T>(
  fetchFn: () => Promise<{ data?: T; error?: string }>,
  dependencies: any[] = []
): UseApiDataResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async (): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchFn();
      if (response.error) {
        setError(response.error);
      } else if (response.data !== undefined) {
        setData(response.data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies);

  return { data, loading, error, refetch: fetchData };
}

