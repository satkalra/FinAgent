/**
 * Service for evaluation API endpoints
 */

import { fetchEventSource, EventSourceMessage } from '@microsoft/fetch-event-source';

const SSE_BASE_URL = import.meta.env.VITE_SSE_BASE_URL || 'http://localhost:8000';

export interface EvaluationStreamCallbacks {
  onStatus?: (data: any) => void;
  onTestCaseStart?: (data: any) => void;
  onTestCaseResult?: (data: any) => void;
  onSummary?: (data: any) => void;
  onError?: (error: string) => void;
}

/**
 * Upload CSV file and stream evaluation results
 */
export async function uploadAndStreamEvaluation(
  file: File,
  callbacks: EvaluationStreamCallbacks,
  signal?: AbortSignal
): Promise<void> {
  const formData = new FormData();
  formData.append('file', file);

  await fetchEventSource(`${SSE_BASE_URL.replace('/sse', '')}/evaluations/run`, {
    method: 'POST',
    body: formData,
    signal,

    onopen: async (response) => {
      if (response.ok) {
        return; // Everything is OK
      } else if (response.status >= 400 && response.status < 500 && response.status !== 429) {
        // Client error - don't retry
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `Upload failed: ${response.statusText}`);
      } else {
        // Server error - will retry
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    },

    onmessage: (event: EventSourceMessage) => {
      try {
        const data = JSON.parse(event.data);

        // Route to appropriate callback based on event type
        switch (event.event) {
          case 'status':
            callbacks.onStatus?.(data);
            break;
          case 'test_case_start':
            callbacks.onTestCaseStart?.(data);
            break;
          case 'test_case_result':
            callbacks.onTestCaseResult?.(data);
            break;
          case 'summary':
            callbacks.onSummary?.(data);
            break;
          case 'error':
            callbacks.onError?.(data.message || 'Unknown error');
            break;
          default:
            console.log('Unknown event type:', event.event, data);
        }
      } catch (error) {
        console.error('Failed to parse SSE data:', error);
      }
    },

    onerror: (error) => {
      console.error('SSE Error:', error);
      callbacks.onError?.(error instanceof Error ? error.message : 'Connection error');
      throw error; // Stop retrying
    },

    onclose: () => {
      console.log('Evaluation stream closed');
    },
  });
}
