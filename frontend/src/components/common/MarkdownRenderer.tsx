import clsx from 'clsx';
import ReactMarkdown, { type Components } from 'react-markdown';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

const markdownComponents: Components = {
  code({ inline, className, children, ...props }) {
    if (inline) {
      return (
        <code
          className={clsx(
            'bg-gray-100 rounded px-1 py-0.5 text-primary-700 font-mono text-[0.85em]',
            className
          )}
          {...props}
        >
          {children}
        </code>
      );
    }

    return (
      <pre
        className={clsx(
          'bg-gray-900 text-gray-100 rounded-lg p-3 overflow-x-auto text-sm',
          className
        )}
        {...props}
      >
        <code className="font-mono">{children}</code>
      </pre>
    );
  },
  a({ children, ...props }) {
    return (
      <a
        className="text-primary-600 underline underline-offset-2 break-words"
        target="_blank"
        rel="noreferrer"
        {...props}
      >
        {children}
      </a>
    );
  },
  ul({ children, ...props }) {
    return (
      <ul className="list-disc pl-5 space-y-1" {...props}>
        {children}
      </ul>
    );
  },
  ol({ children, ...props }) {
    return (
      <ol className="list-decimal pl-5 space-y-1" {...props}>
        {children}
      </ol>
    );
  },
  blockquote({ children, ...props }) {
    return (
      <blockquote
        className="border-l-4 border-primary-200 pl-4 italic text-gray-600"
        {...props}
      >
        {children}
      </blockquote>
    );
  },
  table({ children, ...props }) {
    return (
      <div className="overflow-x-auto">
        <table className="min-w-full text-left border-collapse" {...props}>
          {children}
        </table>
      </div>
    );
  },
  th({ children, ...props }) {
    return (
      <th className="border border-gray-200 bg-gray-50 px-3 py-2 font-semibold" {...props}>
        {children}
      </th>
    );
  },
  td({ children, ...props }) {
    return (
      <td className="border border-gray-200 px-3 py-2 align-top" {...props}>
        {children}
      </td>
    );
  },
};

export function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  if (!content) return null;

  return (
    <ReactMarkdown
      className={clsx('prose prose-sm max-w-none break-words', className)}
      components={markdownComponents}
    >
      {content}
    </ReactMarkdown>
  );
}
