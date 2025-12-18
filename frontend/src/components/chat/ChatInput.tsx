import { useState, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message);
      setMessage('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex-shrink-0 bg-white border-t border-gray-200 px-6 py-4">
      <div className="max-w-4xl mx-auto flex gap-3">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about stocks, financial ratios, or investment strategies..."
          disabled={disabled}
          rows={1}
          className="flex-1 resize-none border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
        <button
          onClick={handleSend}
          disabled={disabled || !message.trim()}
          className="bg-primary-500 text-white px-6 py-3 rounded-lg hover:bg-primary-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <Send className="w-5 h-5" />
          <span>Send</span>
        </button>
      </div>
      <div className="max-w-4xl mx-auto mt-2 text-xs text-gray-500">
        Press Enter to send, Shift+Enter for new line
      </div>
    </div>
  );
}
