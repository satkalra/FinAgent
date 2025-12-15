import { ThoughtStep } from '@/types';
import { Brain, Lightbulb } from 'lucide-react';

interface ThinkingStepProps {
  thought: ThoughtStep;
  isLatest?: boolean;
}

export function ThinkingStepComponent({ thought, isLatest = false }: ThinkingStepProps) {
  const getActionColor = (action: string) => {
    const lower = action.toLowerCase();
    if (lower === 'final_answer') return 'text-green-600 bg-green-50 border-green-200';
    if (lower.includes('calculate') || lower.includes('ratio') || lower.includes('investment')) {
      return 'text-purple-600 bg-purple-50 border-purple-200';
    }
    if (lower.includes('stock') || lower.includes('price')) {
      return 'text-blue-600 bg-blue-50 border-blue-200';
    }
    if (lower.includes('company')) {
      return 'text-indigo-600 bg-indigo-50 border-indigo-200';
    }
    return 'text-primary-600 bg-primary-50 border-primary-200';
  };

  const getActionLabel = (action: string) => {
    if (action === 'final_answer') return 'Finalizing Answer';
    return `Tool: ${action}`;
  };

  return (
    <div className={`flex gap-3 items-start ${isLatest ? 'animate-fade-in' : ''}`}>
      <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
        {thought.action === 'final_answer' ? (
          <Lightbulb className="w-4 h-4 text-indigo-600" />
        ) : (
          <Brain className="w-4 h-4 text-indigo-600" />
        )}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-semibold text-gray-500">
            Step {thought.iteration}
          </span>
          <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${getActionColor(thought.action)}`}>
            {getActionLabel(thought.action)}
          </span>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
          <p className="text-sm text-gray-700 leading-relaxed italic">
            💭 {thought.thought}
          </p>
        </div>
      </div>
    </div>
  );
}
