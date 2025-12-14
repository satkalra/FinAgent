import { useEffect, useRef, useState, useCallback } from 'react';
import { SSEEvent } from '@/types';

const SSE_BASE_URL = import.meta.env.VITE_SSE_BASE_URL || 'http://localhost:8000/sse';

export function useSSE(conversationId: number | null) {
  const [isConnected, setIsConnected] = useState(false);
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);

  const connect = useCallback((message: string) => {
    if (!conversationId) {
      console.error('No conversation ID provided');
      return;
    }

    const url = `${SSE_BASE_URL}/chat/${conversationId}?message=${encodeURIComponent(message)}`;
    const eventSource = new EventSource(url);

    eventSourceRef.current = eventSource;
    setIsConnected(true);
    setEvents([]);

    // Listen to all event types
    const eventTypes = [
      'user_message',
      'content_chunk',
      'tool_call',
      'tool_result',
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
  }, [conversationId]);

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
