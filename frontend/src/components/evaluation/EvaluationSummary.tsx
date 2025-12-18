import { CheckCircle2, XCircle, Download } from 'lucide-react';
import { EvaluationSummary as SummaryType, EvaluationResult } from '../../types/evaluation';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface EvaluationSummaryProps {
  summary: SummaryType;
  results: EvaluationResult[];
}

export default function EvaluationSummary({ summary, results }: EvaluationSummaryProps) {
  const passRate = summary.total_tests > 0
    ? Math.round((summary.passed / summary.total_tests) * 100)
    : 0;

  const chartData = [
    {
      name: 'Tool Selection',
      score: Math.round(summary.average_tool_selection * 100),
    },
    {
      name: 'Argument Match',
      score: Math.round(summary.average_argument_match * 100),
    },
    {
      name: 'Faithfulness',
      score: Math.round(summary.average_faithfulness * 100),
    },
  ];

  const downloadResults = () => {
    const dataStr = JSON.stringify({ summary, results }, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `evaluation-results-${new Date().toISOString()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header with Pass Rate */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg shadow-lg p-8">
        <h2 className="text-2xl font-bold mb-2">Evaluation Complete!</h2>
        <div className="flex items-center space-x-8 mt-4">
          <div>
            <div className="text-5xl font-bold">{passRate}%</div>
            <div className="text-blue-100 text-sm mt-1">Pass Rate</div>
          </div>
          <div className="flex-1 grid grid-cols-2 gap-4">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="h-6 w-6" />
              <div>
                <div className="text-2xl font-bold">{summary.passed}</div>
                <div className="text-blue-100 text-xs">Passed</div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <XCircle className="h-6 w-6" />
              <div>
                <div className="text-2xl font-bold">{summary.failed}</div>
                <div className="text-blue-100 text-xs">Failed</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Metric Breakdown */}
      <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Average Scores by Metric
          </h3>
          <button
            onClick={downloadResults}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Download className="h-4 w-4" />
            <span>Download Results</span>
          </button>
        </div>

        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis domain={[0, 100]} />
            <Tooltip
              formatter={(value) => `${value}%`}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '0.5rem'
              }}
            />
            <Legend />
            <Bar dataKey="score" fill="#3b82f6" name="Score (%)" />
          </BarChart>
        </ResponsiveContainer>

        <div className="grid grid-cols-3 gap-4 mt-6">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {Math.round(summary.average_tool_selection * 100)}%
            </div>
            <div className="text-sm text-gray-600 mt-1">Tool Selection</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {Math.round(summary.average_argument_match * 100)}%
            </div>
            <div className="text-sm text-gray-600 mt-1">Argument Match</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">
              {Math.round(summary.average_faithfulness * 100)}%
            </div>
            <div className="text-sm text-gray-600 mt-1">Faithfulness</div>
          </div>
        </div>
      </div>
    </div>
  );
}
