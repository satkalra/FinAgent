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
  const abortControllerRef = useRef<AbortController | null>(null);

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

        const abortController = new AbortController();
        abortControllerRef.current = abortController;

        await uploadAndStreamEvaluation(
          file,
          {
            onStatus: (data) => {
              if (!isMounted) return;
              console.log('Status:', data);
            },

            onTestCaseStart: (data) => {
              if (!isMounted) return;
              setProgress({ current: data.current, total: data.total });
              setCurrentQuery(data.query);
            },

            onTestCaseResult: (result) => {
              if (!isMounted) return;
              setResults(prev => [...prev, result]);
            },

            onSummary: (summaryData) => {
              if (!isMounted) return;
              setSummary(summaryData);
              setIsRunning(false);
              setCurrentQuery(null);
              abortControllerRef.current = null;
              setFile(null); // Clear file to prevent restart on re-render
            },

            onError: (errorMessage) => {
              if (!isMounted) return;
              setError(errorMessage);
              setIsRunning(false);
              abortControllerRef.current = null;
            },
          },
          abortController.signal
        );

      } catch (err) {
        if (!isMounted) return;
        const message = err instanceof Error ? err.message : 'Unknown error occurred';
        setError(message);
        setIsRunning(false);
        abortControllerRef.current = null;
      }
    };

    startStream();

    return () => {
      isMounted = false;
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
        abortControllerRef.current = null;
      }
    };
  }, [file]);

  const startEvaluation = (newFile: File) => {
    setFile(newFile);
  };

  const reset = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
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
