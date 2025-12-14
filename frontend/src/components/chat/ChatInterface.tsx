import { useState, useEffect, useRef } from 'react';
import { chatService } from '@/services/chatService';
import { Message } from '@/types';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { Send } from 'lucide-react';

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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

    try {
      const response = await chatService.sendMessage(content, conversationId || undefined);

      // Update conversation ID if new
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Replace optimistic message with real messages from server
      setMessages((prev) => {
        // Remove optimistic message
        const withoutOptimistic = prev.filter((msg) => msg.id !== optimisticUserMessage.id);
        // Add real messages
        return [...withoutOptimistic, response.user_message, response.assistant_message];
      });
    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message to chat
      const errorMessage: Message = {
        id: Date.now() + 1,
        conversation_id: conversationId || 0,
        role: 'assistant',
        content: `❌ **Error**: Failed to get response from FinAgent. ${
          error instanceof Error ? error.message : 'Please try again.'
        }`,
        created_at: new Date().toISOString(),
        tokens_used: null,
        response_time_ms: null,
        model_name: null,
        tool_executions: [],
      };

      setMessages((prev) => [...prev, errorMessage]);
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
                <div className="p-3 bg-white rounded-lg border border-gray-200">
                  <p className="text-sm text-gray-600">
                    Try: "What's the current price of Apple stock?"
                  </p>
                </div>
                <div className="p-3 bg-white rounded-lg border border-gray-200">
                  <p className="text-sm text-gray-600">
                    Try: "Calculate the P/E ratio for TSLA"
                  </p>
                </div>
                <div className="p-3 bg-white rounded-lg border border-gray-200">
                  <p className="text-sm text-gray-600">
                    Try: "Compare AAPL and MSFT financial ratios"
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex items-center gap-2 text-gray-500">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                <span className="ml-2">FinAgent is thinking...</span>
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
