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
        <h3 className="text-lg font-bold text-blue-900 mb-4">
          📄 CSV Format Guide
        </h3>

        {/* Column Descriptions */}
        <div className="mb-6">
          <h4 className="text-sm font-semibold text-blue-900 mb-2">Required Columns</h4>
          <div className="bg-white rounded-lg p-4 space-y-3">
            <div>
              <code className="bg-blue-100 px-2 py-1 rounded font-mono text-xs">test_id</code>
              <p className="text-sm text-gray-700 mt-1">Unique identifier for each test case (e.g., "1", "test_001")</p>
            </div>

            <div>
              <code className="bg-blue-100 px-2 py-1 rounded font-mono text-xs">query</code>
              <p className="text-sm text-gray-700 mt-1">The user question to test against the agent</p>
              <div className="mt-1 text-xs text-gray-600 space-y-1">
                <div>• Example: <code className="bg-gray-100 px-1">"What is Apple's stock price?"</code></div>
              </div>
            </div>

            <div>
              <code className="bg-blue-100 px-2 py-1 rounded font-mono text-xs">expected_tool</code>
              <p className="text-sm text-gray-700 mt-1">Tool(s) that should be called - single tool name or JSON array of tool names</p>
              <div className="mt-1 text-xs text-gray-600 space-y-1">
                <div>• Single tool: <code className="bg-gray-100 px-1">"get_stock_price"</code></div>
                <div>• Multiple tools: <code className="bg-gray-100 px-1">{`["get_stock_price","get_company_info"]`}</code></div>
                <div className="text-amber-700 flex items-start mt-2">
                  <span className="mr-1">⚠️</span>
                  <span>Tool names must be internal names (snake_case), not display names</span>
                </div>
              </div>
            </div>

            <div>
              <code className="bg-blue-100 px-2 py-1 rounded font-mono text-xs">expected_args</code>
              <p className="text-sm text-gray-700 mt-1">Expected arguments - single JSON object or array of objects (matching tools order)</p>
              <div className="mt-1 text-xs text-gray-600 space-y-1">
                <div>• Single tool: <code className="bg-gray-100 px-1">{`{""ticker"":""AAPL""}`}</code></div>
                <div>• Multiple tools: <code className="bg-gray-100 px-1">{`[{""ticker"":""AAPL""},{""ticker"":""AAPL""}]`}</code></div>
                <div className="text-amber-700 flex items-start mt-2">
                  <span className="mr-1">⚠️</span>
                  <span>Use escaped double quotes: <code className="bg-amber-50 px-1">{`""`}</code> for quotes inside JSON</span>
                </div>
              </div>
            </div>

            <div>
              <code className="bg-blue-100 px-2 py-1 rounded font-mono text-xs">expected_response_contains</code>
              <p className="text-sm text-gray-700 mt-1">Comma-separated keywords that should appear in the agent's final response</p>
              <div className="mt-1 text-xs text-gray-600 space-y-1">
                <div>• Example: <code className="bg-gray-100 px-1">"current price,AAPL"</code></div>
                <div>• Used by LLM judge to evaluate response faithfulness</div>
              </div>
            </div>
          </div>
        </div>

        {/* Multi-Tool Support Note */}
        <div className="mb-6 bg-green-50 border border-green-300 rounded-lg p-4">
          <div className="flex items-start space-x-2">
            <span className="text-green-600 text-lg">✨</span>
            <div className="text-sm text-green-800">
              <span className="font-semibold">Multi-Tool Support:</span> You can now test queries that require multiple tools!
              Use JSON arrays for both <code className="bg-green-100 px-1">expected_tool</code> and <code className="bg-green-100 px-1">expected_args</code>.
              The system will validate that ALL expected tools are called with correct arguments.
            </div>
          </div>
        </div>

        {/* Available Tools */}
        <div className="mb-6">
          <h4 className="text-sm font-semibold text-blue-900 mb-2">Available Tools</h4>
          <div className="bg-white rounded-lg p-4 space-y-4">

            <div className="border-l-4 border-green-500 pl-3">
              <div className="font-mono text-xs text-green-700 font-bold">get_stock_price</div>
              <p className="text-xs text-gray-600 mt-1">Get current stock price, historical prices, and basic stock information</p>
              <div className="mt-2 text-xs">
                <span className="font-semibold">Arguments:</span>
                <ul className="list-disc list-inside ml-2 mt-1 space-y-1">
                  <li><code className="bg-gray-100 px-1">ticker</code> (required) - Stock symbol (e.g., "AAPL", "MSFT")</li>
                  <li><code className="bg-gray-100 px-1">period</code> (optional) - Time period: "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y"</li>
                  <li><code className="bg-gray-100 px-1">info</code> (optional) - Include detailed info (true/false)</li>
                </ul>
                <div className="mt-2 bg-gray-50 p-2 rounded">
                  <span className="text-gray-500">Example:</span> <code className="text-xs">{`{""ticker"":""AAPL"",""period"":""1mo""}`}</code>
                </div>
              </div>
            </div>

            <div className="border-l-4 border-blue-500 pl-3">
              <div className="font-mono text-xs text-blue-700 font-bold">get_company_info</div>
              <p className="text-xs text-gray-600 mt-1">Get company details including sector, industry, employees, and executives</p>
              <div className="mt-2 text-xs">
                <span className="font-semibold">Arguments:</span>
                <ul className="list-disc list-inside ml-2 mt-1">
                  <li><code className="bg-gray-100 px-1">ticker</code> (required) - Stock symbol (e.g., "AAPL", "MSFT")</li>
                </ul>
                <div className="mt-2 bg-gray-50 p-2 rounded">
                  <span className="text-gray-500">Example:</span> <code className="text-xs">{`{""ticker"":""MSFT""}`}</code>
                </div>
              </div>
            </div>

            <div className="border-l-4 border-purple-500 pl-3">
              <div className="font-mono text-xs text-purple-700 font-bold">calculate_financial_ratios</div>
              <p className="text-xs text-gray-600 mt-1">Calculate P/E, PEG, P/B, ROE, ROA, profit margins, and debt ratios</p>
              <div className="mt-2 text-xs">
                <span className="font-semibold">Arguments:</span>
                <ul className="list-disc list-inside ml-2 mt-1">
                  <li><code className="bg-gray-100 px-1">ticker</code> (required) - Stock symbol (e.g., "AAPL", "MSFT")</li>
                </ul>
                <div className="mt-2 bg-gray-50 p-2 rounded">
                  <span className="text-gray-500">Example:</span> <code className="text-xs">{`{""ticker"":""GOOGL""}`}</code>
                </div>
              </div>
            </div>

            <div className="border-l-4 border-orange-500 pl-3">
              <div className="font-mono text-xs text-orange-700 font-bold">calculate_investment_returns</div>
              <p className="text-xs text-gray-600 mt-1">Calculate investment returns, compound interest, and future value</p>
              <div className="mt-2 text-xs">
                <span className="font-semibold">Arguments:</span>
                <ul className="list-disc list-inside ml-2 mt-1 space-y-1">
                  <li><code className="bg-gray-100 px-1">principal</code> (required) - Initial investment amount</li>
                  <li><code className="bg-gray-100 px-1">annual_rate</code> (required) - Annual rate as percentage (e.g., 7 for 7%)</li>
                  <li><code className="bg-gray-100 px-1">years</code> (required) - Investment time period in years</li>
                  <li><code className="bg-gray-100 px-1">monthly_contribution</code> (optional) - Monthly contribution amount</li>
                </ul>
                <div className="mt-2 bg-gray-50 p-2 rounded">
                  <span className="text-gray-500">Example:</span> <code className="text-xs">{`{""principal"":1000,""annual_rate"":7,""years"":10}`}</code>
                </div>
              </div>
            </div>

          </div>
        </div>

        {/* Full Example */}
        <div>
          <h4 className="text-sm font-semibold text-blue-900 mb-2">Complete CSV Example</h4>
          <div className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
            <pre className="text-xs font-mono whitespace-pre">
{`test_id,query,expected_tool,expected_args,expected_response_contains
1,"What is Apple's stock price?","get_stock_price","{""ticker"":""AAPL""}","current price"
2,"Tell me about Microsoft","get_company_info","{""ticker"":""MSFT""}","sector,industry"
3,"Calculate ratios for Google","calculate_financial_ratios","{""ticker"":""GOOGL""}","P/E ratio"
4,"$1000 at 7% for 10 years?","calculate_investment_returns","{""principal"":1000,""annual_rate"":7,""years"":10}","future value"
5,"Get Apple price and company info","[""get_stock_price"",""get_company_info""]","[{""ticker"":""AAPL""},{""ticker"":""AAPL""}]","Apple,stock,sector"`}
            </pre>
          </div>
          <p className="text-xs text-gray-600 mt-2">
            <span className="font-semibold">Note:</span> Row 5 shows multi-tool validation - expecting both <code className="bg-gray-100 px-1">get_stock_price</code> and <code className="bg-gray-100 px-1">get_company_info</code> to be called with corresponding arguments.
          </p>
        </div>
      </div>
    </div>
  );
}
