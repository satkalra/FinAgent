import { useState, useEffect, useRef } from 'react';
import { EvaluationResult, EvaluationSummary } from '../types/evaluation';
import { uploadAndStreamEvaluation } from '../services/evaluationService';

interface UseEvaluationSSEReturn {
  results: EvaluationResult[];
  summary: EvaluationSummary | null;
  isRunning: boolean;
  error: string | null;
  progress: { current: number; total: number };
  currentQuery: string | null;
  startEvaluation: (file: File) => void;
  reset: () => void;
}

export function useEvaluationSSE(): UseEvaluationSSEReturn {
  const [file, setFile] = useState<File | null>(null);
  const [results, setResults] = useState<EvaluationResult[]>([]);
  const [summary, setSummary] = useState<EvaluationSummary | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const [currentQuery, setCurrentQuery] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!file) return;

    let isMounted = true;

    const startStream = async () => {
      try {
        setIsRunning(true);
        setError(null);
        setResults([]);
        setSummary(null);
        setProgress({ current: 0, total: 0 });
        setCurrentQuery(null);

        const eventSource = await uploadAndStreamEvaluation(file);
        if (!isMounted) {
          eventSource.close();
          return;
        }

        eventSourceRef.current = eventSource;

        // Listen for status events
        eventSource.addEventListener('status', (e: MessageEvent) => {
          if (!isMounted) return;
          const data = JSON.parse(e.data);
          console.log('Status:', data);
        });

        // Listen for test_case_start events
        eventSource.addEventListener('test_case_start', (e: MessageEvent) => {
          if (!isMounted) return;
          const data = JSON.parse(e.data);
          setProgress({ current: data.current, total: data.total });
          setCurrentQuery(data.query);
        });

        // Listen for test_case_result events
        eventSource.addEventListener('test_case_result', (e: MessageEvent) => {
          if (!isMounted) return;
          const result = JSON.parse(e.data);
          setResults(prev => [...prev, result]);
        });

        // Listen for summary event
        eventSource.addEventListener('summary', (e: MessageEvent) => {
          if (!isMounted) return;
          const summaryData = JSON.parse(e.data);
          setSummary(summaryData);
          setIsRunning(false);
          setCurrentQuery(null);
        });

        // Listen for error events
        eventSource.addEventListener('error', (e: MessageEvent) => {
          if (!isMounted) return;
          const errorData = JSON.parse(e.data);
          setError(errorData.message);

          if (!errorData.continue) {
            setIsRunning(false);
            eventSource.close();
          }
        });

      } catch (err) {
        if (!isMounted) return;
        const message = err instanceof Error ? err.message : 'Unknown error occurred';
        setError(message);
        setIsRunning(false);
      }
    };

    startStream();

    return () => {
      isMounted = false;
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, [file]);

  const startEvaluation = (newFile: File) => {
    setFile(newFile);
  };

  const reset = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setFile(null);
    setResults([]);
    setSummary(null);
    setIsRunning(false);
    setError(null);
    setProgress({ current: 0, total: 0 });
    setCurrentQuery(null);
  };

  return {
    results,
    summary,
    isRunning,
    error,
    progress,
    currentQuery,
    startEvaluation,
    reset,
  };
}
