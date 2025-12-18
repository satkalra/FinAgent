/**
 * Service for evaluation API endpoints
 */

const SSE_BASE_URL = import.meta.env.VITE_SSE_BASE_URL || 'http://localhost:8000';

export async function uploadAndStreamEvaluation(file: File): Promise<EventSource> {
  // Create FormData
  const formData = new FormData();
  formData.append('file', file);

  // Upload file via POST and get streaming response
  // Since EventSource doesn't support POST, we use fetch first
  const response = await fetch(`${SSE_BASE_URL.replace('/sse', '')}/evaluations/run`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `Upload failed: ${response.statusText}`);
  }

  // Check if response is SSE stream
  const contentType = response.headers.get('content-type');
  if (!contentType?.includes('text/event-stream')) {
    throw new Error('Server did not return SSE stream');
  }

  // Return a custom event source from the fetch stream
  return createEventSourceFromStream(response);
}

/**
 * Create an EventSource-like object from a fetch Response stream
 */
function createEventSourceFromStream(response: Response): EventSource {
  const eventSource = {
    listeners: {} as Record<string, ((event: MessageEvent) => void)[]>,
    readyState: 1, // OPEN
    url: response.url,

    addEventListener(type: string, listener: (event: MessageEvent) => void) {
      if (!this.listeners[type]) {
        this.listeners[type] = [];
      }
      this.listeners[type].push(listener);
    },

    removeEventListener(type: string, listener: (event: MessageEvent) => void) {
      if (this.listeners[type]) {
        this.listeners[type] = this.listeners[type].filter(l => l !== listener);
      }
    },

    close() {
      this.readyState = 2; // CLOSED
    },

    onopen: null as ((event: Event) => void) | null,
    onmessage: null as ((event: MessageEvent) => void) | null,
    onerror: null as ((event: Event) => void) | null,
  };

  // Process the stream
  (async () => {
    try {
      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Process complete SSE messages
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        let eventType = 'message';
        let eventData = '';

        for (const line of lines) {
          if (line.startsWith('event:')) {
            eventType = line.substring(6).trim();
          } else if (line.startsWith('data:')) {
            eventData = line.substring(5).trim();

            // Emit event
            try {
              const data = JSON.parse(eventData);
              const event = new MessageEvent(eventType, { data: JSON.stringify(data) });

              // Call type-specific listeners
              if (eventSource.listeners[eventType]) {
                eventSource.listeners[eventType].forEach(listener => listener(event));
              }

              // Call generic message handler
              if (eventSource.onmessage) {
                eventSource.onmessage(event);
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }

            // Reset for next event
            eventType = 'message';
            eventData = '';
          }
        }
      }

      eventSource.readyState = 2; // CLOSED
    } catch (error) {
      console.error('Error reading SSE stream:', error);
      if (eventSource.onerror) {
        eventSource.onerror(new Event('error'));
      }
    }
  })();

  return eventSource as unknown as EventSource;
}
