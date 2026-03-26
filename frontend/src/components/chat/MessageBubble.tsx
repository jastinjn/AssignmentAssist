import type { UIMessage } from 'ai'
import ReactMarkdown from 'react-markdown'
import { cn } from '@/lib/utils'

export function MessageBubble({ message }: { message: UIMessage }) {
  const isUser = message.role === 'user'

  const text = message.parts
    .filter((p): p is Extract<typeof p, { type: 'text' }> => p.type === 'text')
    .map((p) => p.text)
    .join('')

  return (
    <div className={cn('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={cn(
          'max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed',
          isUser
            ? 'bg-primary text-primary-foreground'
            : 'bg-gray-50 text-gray-800 border border-gray-100',
        )}
      >
        {isUser ? (
          <span className="whitespace-pre-wrap">{text}</span>
        ) : (
          <ReactMarkdown
            components={{
              p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
              ul: ({ children }) => <ul className="list-disc pl-4 mb-2 space-y-1">{children}</ul>,
              ol: ({ children }) => <ol className="list-decimal pl-4 mb-2 space-y-1">{children}</ol>,
              li: ({ children }) => <li>{children}</li>,
              strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
              h1: ({ children }) => <h1 className="text-base font-bold mb-1">{children}</h1>,
              h2: ({ children }) => <h2 className="text-sm font-bold mb-1">{children}</h2>,
              h3: ({ children }) => <h3 className="text-sm font-semibold mb-1">{children}</h3>,
              code: ({ children }) => (
                <code className="bg-gray-200 text-gray-800 rounded px-1 py-0.5 text-xs font-mono">
                  {children}
                </code>
              ),
              pre: ({ children }) => (
                <pre className="bg-gray-200 rounded p-2 text-xs font-mono overflow-x-auto mb-2">
                  {children}
                </pre>
              ),
            }}
          >
            {text}
          </ReactMarkdown>
        )}
      </div>
    </div>
  )
}
