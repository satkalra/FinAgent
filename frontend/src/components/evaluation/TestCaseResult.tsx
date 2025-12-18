import { useState } from 'react';
import { ChevronDown, ChevronUp, Check, X, AlertCircle } from 'lucide-react';
import { EvaluationResult } from '../../types/evaluation';

interface TestCaseResultProps {
  result: EvaluationResult;
}

export default function TestCaseResult({ result }: TestCaseResultProps) {
  const [expanded, setExpanded] = useState(false);

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600 bg-green-50';
    if (score >= 0.4) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getPassIcon = (passed: boolean) => {
    return passed ? (
      <Check className="h-5 w-5 text-green-600" />
    ) : (
      <X className="h-5 w-5 text-red-600" />
    );
  };

  return (
    <div className={`bg-white border rounded-lg shadow-sm overflow-hidden ${
      result.passed ? 'border-green-200' : 'border-red-200'
    }`}>
      <div className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-start space-x-3 flex-1">
            <div className="mt-1">{getPassIcon(result.passed)}</div>
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-1">
                <span className="text-xs font-medium text-gray-500">
                  Test #{result.test_id}
                </span>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  result.passed
                    ? 'bg-green-100 text-green-700'
                    : 'bg-red-100 text-red-700'
                }`}>
                  {result.passed ? 'PASSED' : 'FAILED'}
                </span>
              </div>
              <p className="text-sm font-medium text-gray-900 mb-2">
                {result.query}
              </p>
            </div>
          </div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1 hover:bg-gray-100 rounded transition-colors ml-2"
          >
            {expanded ? (
              <ChevronUp className="h-5 w-5 text-gray-500" />
            ) : (
              <ChevronDown className="h-5 w-5 text-gray-500" />
            )}
          </button>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-3 gap-3 mb-3">
          {result.metrics.map((metric) => (
            <div
              key={metric.metric_name}
              className={`px-3 py-2 rounded-lg ${getScoreColor(metric.score)}`}
            >
              <div className="text-xs font-medium mb-1 capitalize">
                {metric.metric_name.replace('_', ' ')}
              </div>
              <div className="text-lg font-bold">
                {(metric.score * 100).toFixed(0)}%
              </div>
            </div>
          ))}
        </div>

        {/* Overall Score */}
        <div className="flex items-center justify-between pt-3 border-t border-gray-200">
          <span className="text-sm font-medium text-gray-700">Overall Score</span>
          <span className={`text-lg font-bold ${
            result.overall_score >= 0.7
              ? 'text-green-600'
              : result.overall_score >= 0.4
              ? 'text-yellow-600'
              : 'text-red-600'
          }`}>
            {(result.overall_score * 100).toFixed(0)}%
          </span>
        </div>

        {/* Expanded Details */}
        {expanded && (
          <div className="mt-4 pt-4 border-t border-gray-200 space-y-4">
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">
                Expected Tool{Array.isArray(result.expected_tool) && result.expected_tool.length > 1 ? 's' : ''}
              </h4>
              <div className="flex flex-wrap gap-2">
                {Array.isArray(result.expected_tool) ? (
                  result.expected_tool.map((tool, idx) => (
                    <code key={idx} className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                      {tool}
                    </code>
                  ))
                ) : (
                  <code className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                    {result.expected_tool}
                  </code>
                )}
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">
                Actual Tools Called
              </h4>
              <div className="flex flex-wrap gap-2">
                {result.actual_tools.length > 0 ? (
                  result.actual_tools.map((tool, idx) => {
                    const expectedTools = Array.isArray(result.expected_tool)
                      ? result.expected_tool
                      : [result.expected_tool];
                    const isExpected = expectedTools.includes(tool);

                    return (
                      <code
                        key={idx}
                        className={`text-xs px-2 py-1 rounded ${
                          isExpected
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {tool}
                      </code>
                    );
                  })
                ) : (
                  <span className="text-sm text-gray-500 italic">No tools called</span>
                )}
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">
                Agent Response
              </h4>
              <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded max-h-40 overflow-y-auto">
                {result.actual_response}
              </div>
            </div>

            {/* LLM Judge Explanation */}
            {result.metrics.find(m => m.metric_name === 'faithfulness')?.details && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-2" />
                  Faithfulness Evaluation
                </h4>
                <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded border border-blue-200">
                  {result.metrics.find(m => m.metric_name === 'faithfulness')?.details}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
