import { Loader2 } from 'lucide-react';

interface EvaluationProgressProps {
  current: number;
  total: number;
  currentQuery?: string;
}

export default function EvaluationProgress({ current, total, currentQuery }: EvaluationProgressProps) {
  const percentage = total > 0 ? Math.round((current / total) * 100) : 0;

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
      <div className="flex items-center mb-4">
        <Loader2 className="h-5 w-5 text-blue-600 animate-spin mr-3" />
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm font-medium text-gray-700">
              Evaluating test cases...
            </span>
            <span className="text-sm font-medium text-gray-900">
              {current} / {total}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${percentage}%` }}
            />
          </div>
        </div>
      </div>

      {currentQuery && (
        <div className="mt-3 p-3 bg-gray-50 rounded">
          <p className="text-xs text-gray-500 mb-1">Current test:</p>
          <p className="text-sm text-gray-700">{currentQuery}</p>
        </div>
      )}
    </div>
  );
}
