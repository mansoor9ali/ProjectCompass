import { useState, useEffect, useCallback, useRef } from 'react';
import { formatApiError } from '../utils/errorHandler';

/**
 * Generic hook for data fetching with loading and error states
 */
export function useDataFetching<T>(
  fetchFn: () => Promise<{ data: T }>,
  initialData: T,
  autoFetch: boolean = true,
  refreshInterval?: number
) {
  const [data, setData] = useState<T>(initialData);
  const [isLoading, setIsLoading] = useState<boolean>(autoFetch);
  const [error, setError] = useState<string | null>(null);
  
  // Use refs to avoid dependency issues in the useEffect
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef<boolean>(true);

  const fetchData = useCallback(async () => {
    // Prevent fetching if the component is unmounted
    if (!mountedRef.current) return;
    
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await fetchFn();
      
      // Safety check for component unmounting during fetch
      if (mountedRef.current) {
        setData(response.data);
        setIsLoading(false);
      }
    } catch (err) {
      console.error('Error fetching data:', err);
      
      // Safety check for component unmounting during fetch
      if (mountedRef.current) {
        setError(formatApiError(err));
        setIsLoading(false);
      }
    }
  }, [fetchFn]);

  useEffect(() => {
    // Mark component as mounted
    mountedRef.current = true;
    
    // Initial fetch if autoFetch is true
    if (autoFetch) {
      fetchData();
    }

    // Set up interval for auto-refresh if specified
    if (refreshInterval && refreshInterval > 0) {
      // Clear any existing interval first to prevent duplicates
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      
      intervalRef.current = setInterval(fetchData, refreshInterval);
    }
    
    // Clean up interval and mark component as unmounted on cleanup
    return () => {
      mountedRef.current = false;
      
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [fetchData, autoFetch, refreshInterval]);

  return { data, isLoading, error, refetch: fetchData };
}
