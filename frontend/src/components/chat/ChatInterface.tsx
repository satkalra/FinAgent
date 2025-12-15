import { chatService } from '@/services/chatService';
import { AgentStatus, Message, SSEEvent, StatusUpdate, ThoughtStep } from '@/types';
import { Send } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { ChatInput } from './ChatInput';
import { ChatMessage } from './ChatMessage';
import { StatusIndicator } from './StatusIndicator';
import { ThinkingStepComponent } from './ThinkingStep';

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [currentStatus, setCurrentStatus] = useState<StatusUpdate | null>(null);
  const [latestThoughts, setLatestThoughts] = useState<ThoughtStep[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentStatus, latestThoughts]);

  const streamSSEMessage = async (content: string, convId: number) => {
    const SSE_BASE_URL = import.meta.env.VITE_SSE_BASE_URL || 'http://localhost:8000/sse';
    const url = `${SSE_BASE_URL}/chat/${convId}?message=${encodeURIComponent(content)}`;

    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    let assistantContent = '';
    const newThoughts: ThoughtStep[] = [];

    return new Promise<void>((resolve, reject) => {
      // Handle different event types
      eventSource.addEventListener('status', (e) => {
        try {
          const data = JSON.parse(e.data) as SSEEvent;
          if (data.type === 'status' && 'message' in data) {
            const status: StatusUpdate = {
              status: (data.status || 'thinking') as AgentStatus,
              message: data.message,
              tool_name: data.tool_name,
              progress: data.progress,
            };
            setCurrentStatus(status);
          }
        } catch (error) {
          console.error('Error parsing status event:', error);
        }
      });

      eventSource.addEventListener('thought', (e) => {
        try {
          const data = JSON.parse(e.data) as SSEEvent;
          if (data.type === 'thought' && 'thought' in data) {
            const thought: ThoughtStep = {
              iteration: data.iteration,
              thought: data.thought,
              action: data.action,
            };
            newThoughts.push(thought);
            // Update thoughts in real-time as they arrive
            setLatestThoughts([...newThoughts]);
          }
        } catch (error) {
          console.error('Error parsing thought event:', error);
        }
      });

      eventSource.addEventListener('answer', (e) => {
        try {
          const data = JSON.parse(e.data) as any;
          if (data.type === 'answer') {
            if (data.chunk) {
              assistantContent += data.chunk;
            } else if (data.content) {
              assistantContent = data.content;
            }
          }
        } catch (error) {
          console.error('Error parsing answer event:', error);
        }
      });

      eventSource.onerror = (error) => {
        console.error('SSE Error:', error);
        eventSource.close();
        eventSourceRef.current = null;

        setCurrentStatus({
          status: 'error',
          message: 'Connection lost',
        });

        setIsLoading(false);
        setTimeout(() => setCurrentStatus(null), 3000);

        reject(new Error('SSE connection failed'));
      };

      // Separate listener for completion to avoid conflicts
      const handleStatusCompletion = (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data) as SSEEvent;
          if (data.type === 'status' && data.status === 'complete') {
            eventSource.close();
            eventSourceRef.current = null;

            // Create assistant message from streamed content
            if (assistantContent) {
              const assistantMessage: Message = {
                id: Date.now(),
                conversation_id: convId,
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

            // Clear thoughts and status after delay
            setTimeout(() => {
              setCurrentStatus(null);
              setLatestThoughts([]);
            }, 5000);

            resolve();
          }
        } catch (error) {
          console.error('Error parsing completion event:', error);
        }
      };

      // Add completion handler
      eventSource.addEventListener('status', handleStatusCompletion);
    });
  };

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    // Optimistically add user message immediately
    const optimisticUserMessage: Message = {
      id: Date.now(), // Temporary ID
      conversation_id: conversationId || 0,
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
      // First, create conversation if needed
      let currentConvId = conversationId;
      if (!currentConvId) {
        const response = await chatService.sendMessage(content, undefined);
        currentConvId = response.conversation_id;
        setConversationId(currentConvId);

        // Replace optimistic message with real user message
        setMessages((prev) => {
          const withoutOptimistic = prev.filter((msg) => msg.id !== optimisticUserMessage.id);
          return [...withoutOptimistic, response.user_message];
        });
      } else {
        // Add message to existing conversation via REST first to ensure it's saved
        await chatService.sendMessage(content, currentConvId);
      }

      // Then stream the response via SSE
      await streamSSEMessage(content, currentConvId);
    } catch (error) {
      console.error('Error sending message:', error);

      setCurrentStatus({
        status: 'error',
        message: 'Failed to get response',
      });

      // Add error message to chat
      const errorMessage: Message = {
        id: Date.now() + 1,
        conversation_id: conversationId || 0,
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
    <div className="flex flex-col h-screen bg-gray-50">
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
