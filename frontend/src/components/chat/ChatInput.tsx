import { type KeyboardEvent, useRef, useState } from 'react'
import { SendHorizontal, Square } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

interface Props {
  onSend: (text: string) => void
  isStreaming: boolean
  onStop: () => void
}

export function ChatInput({ onSend, isStreaming, onStop }: Props) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  function handleSend() {
    const text = value.trim()
    if (!text || isStreaming) return
    onSend(text)
    setValue('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  function handleInput() {
    const el = textareaRef.current
    if (el) {
      el.style.height = 'auto'
      el.style.height = `${Math.min(el.scrollHeight, 200)}px`
    }
  }

  return (
    <div className="border-t border-gray-100 p-4">
      <div className="max-w-3xl mx-auto flex gap-2 items-end">
        <Textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          placeholder="Ask about your students, classes, or assignments… (Enter to send)"
          className="resize-none min-h-[44px] max-h-[200px] focus-visible:ring-primary"
          rows={1}
        />
        {isStreaming ? (
          <Button variant="outline" size="icon" onClick={onStop} className="shrink-0 h-11 w-11">
            <Square className="w-4 h-4 fill-current" />
          </Button>
        ) : (
          <Button
            onClick={handleSend}
            disabled={!value.trim()}
            size="icon"
          className="shrink-0 h-11 w-11 bg-primary hover:bg-primary/90 text-primary-foreground"
          >
            <SendHorizontal className="w-4 h-4" />
          </Button>
        )}
      </div>
      <p className="max-w-3xl mx-auto text-center text-xs text-muted-foreground mt-2">
        AI can make mistakes — review responses for accuracy and relevance.
      </p>
    </div>
  )
}
