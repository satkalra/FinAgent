/**
 * TypeScript types for evaluation system (mirrors backend schemas)
 */

export interface TestCase {
  test_id: string;
  query: string;
  expected_tool: string | string[];
  expected_args: Record<string, any> | Record<string, any>[];
  expected_response_contains: string;
}

export interface MetricScore {
  metric_name: 'tool_selection' | 'argument_match' | 'faithfulness';
  score: number;
  details?: string;
}

export interface EvaluationResult {
  test_id: string;
  query: string;
  expected_tool: string | string[];
  actual_tools: string[];
  actual_response: string;
  metrics: MetricScore[];
  overall_score: number;
  passed: boolean;
}

export interface EvaluationSummary {
  total_tests: number;
  passed: number;
  failed: number;
  average_tool_selection: number;
  average_argument_match: number;
  average_faithfulness: number;
  overall_average: number;
}

// SSE Event Types
export type EvaluationSSEEventType =
  | 'status'
  | 'test_case_start'
  | 'test_case_result'
  | 'summary'
  | 'error';

export interface StatusEvent {
  type: 'status';
  message: string;
  progress?: number;
}

export interface TestCaseStartEvent {
  type: 'test_case_start';
  test_id: string;
  query: string;
  current: number;
  total: number;
}

export interface TestCaseResultEvent {
  type: 'test_case_result';
  data: EvaluationResult;
}

export interface SummaryEvent {
  type: 'summary';
  data: EvaluationSummary;
}

export interface ErrorEvent {
  type: 'error';
  test_id?: string;
  message: string;
  continue?: boolean;
}

export type EvaluationSSEEvent =
  | StatusEvent
  | TestCaseStartEvent
  | TestCaseResultEvent
  | SummaryEvent
  | ErrorEvent;
