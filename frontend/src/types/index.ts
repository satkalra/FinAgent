// Types for FinAgent frontend

export type AgentStatus =
  | 'idle'
  | 'thinking'
  | 'calling_tool'
  | 'processing_results'
  | 'generating_response'
  | 'completed'
  | 'error';

export interface ToolExecution {
  id?: number | string;
  tool_name: string;
  tool_input?: Record<string, any>;
  tool_output?: string | null;
  execution_time_ms?: number | null;
  success?: boolean;
  error_message?: string | null;
}

export interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  conversation_id?: number;
  created_at?: string;
  tokens_used?: number | null;
  response_time_ms?: number | null;
  model_name?: string | null;
  tool_executions?: ToolExecution[];
}

export interface StatusUpdate {
  status: AgentStatus;
  message: string;
  tool_name?: string;
  tool_internal_name?: string;
  progress?: number; // 0-100
}

export interface ThoughtStep {
  iteration: number;
  thought: string;
  action: string;
}

// SSE Event types
export type SSEEvent =
  | { type: 'user_message'; message_id: number; content: string }
  | { type: 'content_chunk'; content: string }
  | { type: 'thought'; iteration: number; thought: string; action: string }
  | { type: 'tool_call'; tool_name: string; tool_internal_name?: string; tool_input: Record<string, any> }
  | { type: 'tool_result'; tool_name: string; tool_internal_name?: string; tool_output: string; execution_time_ms: number }
  | { type: 'status'; status: string; message: string; tool_name?: string; tool_internal_name?: string; progress?: number }
  | { type: 'answer'; chunk?: string; content?: string; is_final?: boolean; iterations?: number }
  | { type: 'final_response'; content: string; iterations: number }
  | { type: 'complete'; message_id: number; response_time_ms: number }
  | { type: 'error'; error?: string; content?: string };
