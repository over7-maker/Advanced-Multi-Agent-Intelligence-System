/**
 * Custom hook for real-time updates via WebSocket
 */

import { useEffect, useState } from 'react';
import { websocketService } from '../services/websocket';

export function useRealtimeUpdates<T>(
  eventType: string,
  initialData: T,
  updateFn: (current: T, update: any) => T
): T {
  const [data, setData] = useState<T>(initialData);

  useEffect(() => {
    websocketService.connect();
    const unsubscribe = websocketService.on(eventType, (update: any) => {
      setData((current) => updateFn(current, update));
    });

    return () => {
      unsubscribe();
    };
  }, [eventType, updateFn]);

  return data;
}

