import { useCallback, useEffect, useState } from 'react'

export interface ChatHistory {
  id: string
  createdAt: string
  updatedAt: string
  preview: string
}

export function useHistories() {
  const [histories, setHistories] = useState<ChatHistory[]>([])
  const [loading, setLoading] = useState(true)

  const fetchHistories = useCallback(async () => {
    try {
      const res = await fetch('/api/chat/histories')
      const data = await res.json()
      setHistories(data)
    } catch {
      // silently fail
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void fetchHistories()
  }, [fetchHistories])

  return { histories, loading, refetch: fetchHistories }
}
