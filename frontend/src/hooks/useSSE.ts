import { SSEEvent } from '@/types';
import { useCallback, useEffect, useRef, useState } from 'react';

const SSE_BASE_URL = import.meta.env.VITE_SSE_BASE_URL || 'http://localhost:8000/sse';

export function useSSE() {
  const [isConnected, setIsConnected] = useState(false);
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);

  const connect = useCallback((message: string, history: SSEEvent[] = []) => {
    const encodedHistory = encodeURIComponent(JSON.stringify(history));
    const url = `${SSE_BASE_URL}/chat?message=${encodeURIComponent(message)}&history=${encodedHistory}`;
    const eventSource = new EventSource(url);

    eventSourceRef.current = eventSource;
    setIsConnected(true);
    setEvents([]);

    const eventTypes = [
      'content_chunk',
      'thought',
      'tool_call',
      'tool_result',
      'status',
      'answer',
      'final_response',
      'complete',
      'error',
    ];

    eventTypes.forEach((eventType) => {
      eventSource.addEventListener(eventType, (e) => {
        try {
          const data = JSON.parse(e.data);
          setEvents((prev) => [...prev, { ...data, type: eventType as any }]);
        } catch (error) {
          console.error('Error parsing SSE event:', error);
        }
      });
    });

    eventSource.onerror = (error) => {
      console.error('SSE Error:', error);
      setIsConnected(false);
      eventSource.close();
    };

    eventSource.addEventListener('complete', () => {
      setIsConnected(false);
      eventSource.close();
    });

    return eventSource;
  }, []);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    }
  }, []);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    connect,
    disconnect,
    isConnected,
    events,
  };
}
