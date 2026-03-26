import { useEffect, useRef } from 'react'
import type { UIMessage } from 'ai'
import { MessageBubble } from './MessageBubble'

interface Props {
  messages: UIMessage[]
  isThinking: boolean
}

export function MessageList({ messages, isThinking }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="px-6 py-4">
      <div className="max-w-3xl mx-auto space-y-4">
        {messages.filter((m) => m.parts.some((p) => p.type === 'text' && p.text)).map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
        {isThinking && (
          <div className="flex justify-start">
            <div className="bg-gray-50 border border-gray-100 rounded-2xl px-4 py-2.5">
              <span className="text-sm text-gray-400 italic">Thinking…</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
