import { AgentStatus } from '@/types';
import { Loader2, Brain, Wrench, CheckCircle2, AlertCircle } from 'lucide-react';

interface StatusIndicatorProps {
  status: AgentStatus;
  message: string;
  tool_name?: string;
  progress?: number;
}

const statusConfig: Record<AgentStatus, { icon: React.ReactNode; color: string; bgColor: string }> = {
  idle: {
    icon: <CheckCircle2 className="w-4 h-4" />,
    color: 'text-gray-600',
    bgColor: 'bg-gray-100',
  },
  thinking: {
    icon: <Brain className="w-4 h-4 animate-pulse" />,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
  },
  calling_tool: {
    icon: <Wrench className="w-4 h-4" />,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
  },
  processing_results: {
    icon: <Loader2 className="w-4 h-4 animate-spin" />,
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50',
  },
  generating_response: {
    icon: <Loader2 className="w-4 h-4 animate-spin" />,
    color: 'text-primary-600',
    bgColor: 'bg-primary-50',
  },
  completed: {
    icon: <CheckCircle2 className="w-4 h-4" />,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
  },
  error: {
    icon: <AlertCircle className="w-4 h-4" />,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
  },
};

export function StatusIndicator({ status, message, tool_name, progress }: StatusIndicatorProps) {
  const config = statusConfig[status] || statusConfig.idle;

  return (
    <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${config.bgColor} border border-gray-200`}>
      <div className={config.color}>
        {config.icon}
      </div>
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-medium ${config.color} truncate`}>
          {message}
          {tool_name && <span className="ml-1 font-mono text-xs">({tool_name})</span>}
        </p>
        {progress !== undefined && (
          <div className="mt-1 w-full bg-gray-200 rounded-full h-1.5">
            <div
              className="bg-primary-600 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
