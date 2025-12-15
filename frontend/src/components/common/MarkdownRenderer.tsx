import clsx from 'clsx';
import ReactMarkdown, { type Components } from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

const markdownComponents: Components = {
  code({ inline, className, children, ...props }) {
    const match = /language-(\w+)/.exec(className || '');

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

    // Use syntax highlighting for code blocks with language specified
    if (match) {
      return (
        <SyntaxHighlighter
          style={oneDark}
          language={match[1]}
          PreTag="div"
          className="rounded-lg my-2 text-sm"
          customStyle={{
            margin: 0,
            borderRadius: '0.5rem',
          }}
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      );
    }

    // Fallback for code blocks without language
    return (
      <pre
        className={clsx(
          'bg-gray-900 text-gray-100 rounded-lg p-3 overflow-x-auto text-sm my-2',
          className
        )}
        {...props}
      >
        <code className="font-mono">{children}</code>
      </pre>
    );
  },
  h1({ children, ...props }) {
    return (
      <h1 className="text-2xl font-bold mt-6 mb-3" {...props}>
        {children}
      </h1>
    );
  },
  h2({ children, ...props }) {
    return (
      <h2 className="text-xl font-bold mt-5 mb-3 pb-2 border-b border-gray-200" {...props}>
        {children}
      </h2>
    );
  },
  h3({ children, ...props }) {
    return (
      <h3 className="text-lg font-semibold mt-4 mb-2" {...props}>
        {children}
      </h3>
    );
  },
  h4({ children, ...props }) {
    return (
      <h4 className="text-base font-semibold mt-3 mb-2" {...props}>
        {children}
      </h4>
    );
  },
  p({ children, ...props }) {
    return (
      <p className="my-2 leading-relaxed" {...props}>
        {children}
      </p>
    );
  },
  strong({ children, ...props }) {
    return (
      <strong className="font-bold text-gray-900" {...props}>
        {children}
      </strong>
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
        className="border-l-4 border-blue-500 pl-4 py-2 my-3 bg-blue-50 italic text-gray-700"
        {...props}
      >
        {children}
      </blockquote>
    );
  },
  table({ children, ...props }) {
    return (
      <div className="overflow-x-auto my-4">
        <table className="min-w-full text-left border-collapse border border-gray-300" {...props}>
          {children}
        </table>
      </div>
    );
  },
  thead({ children, ...props }) {
    return (
      <thead className="bg-gray-50" {...props}>
        {children}
      </thead>
    );
  },
  tbody({ children, ...props }) {
    return (
      <tbody className="bg-white divide-y divide-gray-200" {...props}>
        {children}
      </tbody>
    );
  },
  tr({ children, ...props }) {
    return (
      <tr className="hover:bg-gray-50" {...props}>
        {children}
      </tr>
    );
  },
  th({ children, ...props }) {
    return (
      <th className="border border-gray-300 bg-gray-100 px-4 py-2 font-semibold text-left text-sm" {...props}>
        {children}
      </th>
    );
  },
  td({ children, ...props }) {
    return (
      <td className="border border-gray-300 px-4 py-2 text-sm align-top" {...props}>
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
      remarkPlugins={[remarkGfm]}
      components={markdownComponents}
    >
      {content}
    </ReactMarkdown>
  );
}
