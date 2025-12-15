// Types for FinAgent frontend

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  user_id: string | null;
  model_name: string;
  total_messages: number;
  total_tokens: number;
}

export interface ToolExecution {
  id: number;
  tool_name: string;
  tool_input: Record<string, any>;
  tool_output: string | null;
  execution_time_ms: number | null;
  success: boolean;
  error_message: string | null;
  created_at: string;
}

export interface Message {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  tokens_used: number | null;
  response_time_ms: number | null;
  model_name: string | null;
  tool_executions: ToolExecution[];
}

export type AgentStatus =
  | 'idle'
  | 'thinking'
  | 'calling_tool'
  | 'processing_results'
  | 'generating_response'
  | 'completed'
  | 'error';

export interface StatusUpdate {
  status: AgentStatus;
  message: string;
  tool_name?: string;
  progress?: number; // 0-100
}

export interface ChatResponse {
  conversation_id: number;
  user_message: Message;
  assistant_message: Message;
  status?: AgentStatus;
  status_updates?: StatusUpdate[];
}

// SSE Event types
export type SSEEvent =
  | { type: 'user_message'; message_id: number; content: string }
  | { type: 'content_chunk'; content: string }
  | { type: 'tool_call'; tool_name: string; tool_input: Record<string, any> }
  | { type: 'tool_result'; tool_name: string; tool_output: string; execution_time_ms: number }
  | { type: 'status'; status: string; message: string; tool_name?: string; progress?: number }
  | { type: 'final_response'; content: string; iterations: number }
  | { type: 'complete'; message_id: number; response_time_ms: number }
  | { type: 'error'; error?: string; content?: string };
