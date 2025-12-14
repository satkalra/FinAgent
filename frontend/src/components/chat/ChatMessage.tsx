import { Message } from '@/types';
import { User, Bot, Wrench } from 'lucide-react';
import { MarkdownRenderer } from '@/components/common/MarkdownRenderer';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center flex-shrink-0">
          <Bot className="w-5 h-5 text-white" />
        </div>
      )}

      <div className={`flex flex-col gap-2 max-w-2xl ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`px-4 py-3 rounded-lg ${
            isUser
              ? 'bg-primary-500 text-white'
              : 'bg-white border border-gray-200'
          }`}
        >
          <MarkdownRenderer
            content={message.content}
            className={isUser ? 'text-white prose-invert' : ''}
          />
        </div>

        {/* Tool Executions */}
        {!isUser && message.tool_executions && Array.isArray(message.tool_executions) && message.tool_executions.length > 0 && (
          <div className="w-full space-y-2">
            {message.tool_executions.map((tool, index) => (
              <div
                key={tool.id || `tool-${index}`}
                className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm"
              >
                <div className="flex items-center gap-2 text-gray-700 font-medium mb-2">
                  <Wrench className="w-4 h-4" />
                  <span>{tool.tool_name || 'Unknown Tool'}</span>
                  {tool.execution_time_ms && (
                    <span className="text-gray-500 text-xs">
                      ({tool.execution_time_ms}ms)
                    </span>
                  )}
                </div>

                {tool.success ? (
                  tool.tool_output ? (
                    <MarkdownRenderer
                      content={tool.tool_output}
                      className="prose prose-xs text-gray-600 max-w-none"
                    />
                  ) : (
                    <div className="text-xs text-gray-500">No output</div>
                  )
                ) : (
                  <div className="text-xs text-red-600">
                    Error: {tool.error_message || 'Unknown error'}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Metadata */}
        {!isUser && message.response_time_ms && (
          <div className="text-xs text-gray-500">
            Response time: {message.response_time_ms}ms
            {message.tokens_used && ` • Tokens: ${message.tokens_used}`}
          </div>
        )}
      </div>

      {isUser && (
        <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
          <User className="w-5 h-5 text-gray-600" />
        </div>
      )}
    </div>
  );
}
