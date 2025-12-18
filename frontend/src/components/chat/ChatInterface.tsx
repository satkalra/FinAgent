import { AgentStatus, Message, SSEEvent, StatusUpdate, ThoughtStep } from '@/types';
import { Send } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import { ChatInput } from './ChatInput';
import { ChatMessage } from './ChatMessage';
import { StatusIndicator } from './StatusIndicator';
import { ThinkingStepComponent } from './ThinkingStep';

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentStatus, setCurrentStatus] = useState<StatusUpdate | null>(null);
  const [latestThoughts, setLatestThoughts] = useState<ThoughtStep[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentStatus, latestThoughts]);

  const streamSSEMessage = async (content: string, historyMessages: Pick<Message, 'role' | 'content'>[]) => {
    const SSE_BASE_URL = import.meta.env.VITE_SSE_BASE_URL || 'http://localhost:8000/sse';
    const url = `${SSE_BASE_URL}/chat`;

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    let assistantContent = '';
    const newThoughts: ThoughtStep[] = [];
    let messageCreated = false; // Flag to prevent duplicate messages

    return new Promise<void>((resolve, reject) => {
      fetchEventSource(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          history: historyMessages,
        }),
        signal: abortController.signal,

        onopen: async (response) => {
          if (response.ok) {
            return; // Everything is OK
          } else if (response.status >= 400 && response.status < 500 && response.status !== 429) {
            // Client error - don't retry
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          } else {
            // Server error or rate limit - will retry
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }
        },

        onmessage: (event) => {
          try {
            const data = JSON.parse(event.data) as SSEEvent;

            // Handle status events
            if (event.event === 'status' || data.type === 'status') {
              if ('message' in data) {
                const toolName = data.tool_name || data.tool_internal_name;
                const status: StatusUpdate = {
                  status: (data.status || 'thinking') as AgentStatus,
                  message: data.message,
                  tool_name: toolName,
                  tool_internal_name: data.tool_internal_name,
                  progress: data.progress,
                };
                setCurrentStatus(status);

                if (status.status === 'completed' || status.status === 'complete') {
                  setLatestThoughts([]);

                  // Create assistant message from streamed content (only once)
                  if (assistantContent && !messageCreated) {
                    messageCreated = true;
                    const assistantMessage: Message = {
                      id: Date.now(),
                      role: 'assistant',
                      content: assistantContent,
                      created_at: new Date().toISOString(),
                      tokens_used: null,
                      response_time_ms: null,
                      model_name: null,
                      tool_executions: [],
                    };
                    setMessages((prev) => [...prev, assistantMessage]);
                  }

                  setIsLoading(false);
                  setCurrentStatus(null);
                  abortControllerRef.current = null;
                  resolve();
                }
              }
            }

            // Handle thought events
            if (event.event === 'thought' || data.type === 'thought') {
              if ('thought' in data) {
                const thought: ThoughtStep = {
                  iteration: data.iteration,
                  thought: data.thought,
                  action: data.action,
                };
                newThoughts.push(thought);
                setLatestThoughts([...newThoughts]);
              }
            }

            // Handle answer events
            if (event.event === 'answer' || data.type === 'answer') {
              if (data.chunk) {
                assistantContent += data.chunk;
              } else if (data.content) {
                assistantContent = data.content;
              }
            }
          } catch (error) {
            console.error('Error parsing SSE event:', error);
          }
        },

        onerror: (error) => {
          console.error('SSE Error:', error);
          abortControllerRef.current = null;

          setCurrentStatus({
            status: 'error',
            message: 'Connection lost',
          });

          setIsLoading(false);
          setTimeout(() => setCurrentStatus(null), 3000);

          reject(error);
          throw error; // Stop retrying
        },

        onclose: () => {
          console.log('SSE connection closed');
          abortControllerRef.current = null;
        },
      });
    });
  };

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const historyBeforeMessage = messages.map((msg) => ({
      role: msg.role,
      content: msg.content,
    }));

    // Optimistically add user message immediately
    const optimisticUserMessage: Message = {
      id: Date.now(), // Temporary ID
      role: 'user',
      content,
      created_at: new Date().toISOString(),
      tokens_used: null,
      response_time_ms: null,
      model_name: null,
      tool_executions: [],
    };

    setMessages((prev) => [...prev, optimisticUserMessage]);
    setIsLoading(true);
    setLatestThoughts([]); // Clear previous thoughts
    setCurrentStatus({
      status: 'thinking',
      message: 'Analyzing your request...',
    });

    try {
      await streamSSEMessage(content, historyBeforeMessage);
    } catch (error) {
      console.error('Error sending message:', error);

      setCurrentStatus({
        status: 'error',
        message: 'Failed to get response',
      });

      // Add error message to chat
      const errorMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `❌ **Error**: Failed to get response from FinAgent. ${error instanceof Error ? error.message : 'Please try again.'
          }`,
        created_at: new Date().toISOString(),
        tokens_used: null,
        response_time_ms: null,
        model_name: null,
        tool_executions: [],
      };

      setMessages((prev) => [...prev, errorMessage]);

      // Clear error status after 3 seconds
      setTimeout(() => setCurrentStatus(null), 3000);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-500 rounded-lg flex items-center justify-center">
            <Send className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">FinAgent</h1>
            <p className="text-sm text-gray-500">Financial Agent powered by AI</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center max-w-md">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Send className="w-8 h-8 text-primary-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Welcome to FinAgent
              </h2>
              <p className="text-gray-600 mb-6">
                Your AI-powered financial analyst. Ask me about stocks, calculate
                financial ratios, or get investment insights.
              </p>
              <div className="grid gap-2 text-left">
                <button
                  onClick={() => handleSendMessage("What's the current price of Apple stock?")}
                  className="p-3 bg-white rounded-lg border border-gray-200 hover:border-primary-400 hover:bg-primary-50 transition-all cursor-pointer text-left group"
                  disabled={isLoading}
                >
                  <p className="text-sm text-gray-600 group-hover:text-primary-700">
                    💡 "What's the current price of Apple stock?"
                  </p>
                </button>
                <button
                  onClick={() => handleSendMessage("Calculate the P/E ratio for TSLA")}
                  className="p-3 bg-white rounded-lg border border-gray-200 hover:border-primary-400 hover:bg-primary-50 transition-all cursor-pointer text-left group"
                  disabled={isLoading}
                >
                  <p className="text-sm text-gray-600 group-hover:text-primary-700">
                    💡 "Calculate the P/E ratio for TSLA"
                  </p>
                </button>
                <button
                  onClick={() => handleSendMessage("Compare AAPL and MSFT financial ratios")}
                  className="p-3 bg-white rounded-lg border border-gray-200 hover:border-primary-400 hover:bg-primary-50 transition-all cursor-pointer text-left group"
                  disabled={isLoading}
                >
                  <p className="text-sm text-gray-600 group-hover:text-primary-700">
                    💡 "Compare AAPL and MSFT financial ratios"
                  </p>
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}

            {/* Show status indicator */}
            {currentStatus && !latestThoughts.length && (
              <div className="flex justify-start">
                <div className="max-w-2xl">
                  <StatusIndicator
                    status={currentStatus.status}
                    message={currentStatus.message}
                    tool_name={currentStatus.tool_name}
                    progress={currentStatus.progress}
                  />
                </div>
              </div>
            )}

            {/* Show intermediate thinking steps - prominently displayed */}
            {latestThoughts.length > 0 && (
              <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border-2 border-indigo-200 rounded-xl p-4 my-4 shadow-sm">
                <div className="flex items-center gap-2 mb-3">
                  <div className="flex items-center gap-1.5">
                    <div className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse"></div>
                    <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse delay-75"></div>
                    <div className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse delay-150"></div>
                  </div>
                  <span className="text-sm font-bold text-indigo-900">
                    🧠 Agent Reasoning Process
                  </span>
                </div>
                <div className="space-y-3">
                  {latestThoughts.map((thought, idx) => (
                    <ThinkingStepComponent
                      key={`thought-${thought.iteration}`}
                      thought={thought}
                      isLatest={idx === latestThoughts.length - 1}
                    />
                  ))}
                </div>
                {currentStatus && (
                  <div className="mt-3 pt-3 border-t border-indigo-200">
                    <StatusIndicator
                      status={currentStatus.status}
                      message={currentStatus.message}
                      tool_name={currentStatus.tool_name}
                      progress={currentStatus.progress}
                    />
                  </div>
                )}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <ChatInput onSend={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
