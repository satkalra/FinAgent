import { AlertCircle, RefreshCcw } from 'lucide-react';
import FileUploader from '../components/evaluation/FileUploader';
import EvaluationProgress from '../components/evaluation/EvaluationProgress';
import TestCaseResult from '../components/evaluation/TestCaseResult';
import EvaluationSummary from '../components/evaluation/EvaluationSummary';
import { useEvaluationSSE } from '../hooks/useEvaluationSSE';

export default function EvaluationPage() {
  const {
    results,
    summary,
    isRunning,
    error,
    progress,
    currentQuery,
    startEvaluation,
    reset,
  } = useEvaluationSSE();

  const handleFileSelect = (file: File) => {
    startEvaluation(file);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Agent Evaluation
        </h1>
        <p className="text-gray-600">
          Upload a CSV dataset to evaluate your agent's performance on tool selection,
          argument matching, and response faithfulness.
        </p>
      </div>

      {/* File Uploader */}
      {!isRunning && !summary && (
        <div className="mb-8">
          <FileUploader onFileSelect={handleFileSelect} disabled={isRunning} />
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-sm font-medium text-red-800 mb-1">Error</h3>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Progress Indicator */}
      {isRunning && (
        <div className="mb-8">
          <EvaluationProgress
            current={progress.current}
            total={progress.total}
            currentQuery={currentQuery || undefined}
          />
        </div>
      )}

      {/* Results List */}
      {results.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              Test Results
              <span className="ml-2 text-sm font-normal text-gray-500">
                ({results.length} test{results.length !== 1 ? 's' : ''})
              </span>
            </h2>
            {summary && (
              <button
                onClick={reset}
                className="flex items-center space-x-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <RefreshCcw className="h-4 w-4" />
                <span>New Evaluation</span>
              </button>
            )}
          </div>

          <div className="space-y-4">
            {results.map((result) => (
              <TestCaseResult key={result.test_id} result={result} />
            ))}
          </div>
        </div>
      )}

      {/* Summary */}
      {summary && (
        <div className="mb-8">
          <EvaluationSummary summary={summary} results={results} />
        </div>
      )}

      {/* Empty State */}
      {!isRunning && !summary && results.length === 0 && !error && (
        <div className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
            <svg
              className="w-8 h-8 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No evaluation running
          </h3>
          <p className="text-gray-500 max-w-md mx-auto">
            Upload a CSV file with test cases to begin evaluating your agent's performance.
          </p>
        </div>
      )}

      {/* CSV Format Help */}
      <div className="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-sm font-semibold text-blue-900 mb-3">
          CSV Format Requirements
        </h3>
        <div className="text-sm text-blue-800 space-y-2">
          <p>
            Your CSV file should contain the following columns:
          </p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li><code className="bg-blue-100 px-1 rounded">test_id</code> - Unique identifier for each test</li>
            <li><code className="bg-blue-100 px-1 rounded">query</code> - User query to test</li>
            <li><code className="bg-blue-100 px-1 rounded">expected_tool</code> - Expected tool name (e.g., "get_stock_price")</li>
            <li><code className="bg-blue-100 px-1 rounded">expected_args</code> - JSON string of expected arguments</li>
            <li><code className="bg-blue-100 px-1 rounded">expected_response_contains</code> - Keywords that should appear in response</li>
          </ul>
          <p className="mt-3 text-xs">
            Example: <code className="bg-blue-100 px-1 rounded">1,"What is Apple's stock price?","get_stock_price","{""ticker"":""AAPL""}","current price"</code>
          </p>
        </div>
      </div>
    </div>
  );
}
