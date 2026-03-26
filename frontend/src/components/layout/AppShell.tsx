import { useState } from 'react'
import { useHistories } from '@/hooks/useHistories'
import { ChatPanel } from '@/components/chat/ChatPanel'
import { Sidebar } from './Sidebar'
import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar'

export function AppShell() {
  const [activeHistoryId, setActiveHistoryId] = useState<string | null>(null)
  const [chatKey, setChatKey] = useState(0)
  const { histories, loading, refetch } = useHistories()

  function handleNewChat() {
    setActiveHistoryId(null)
    setChatKey((k) => k + 1)
  }

  function handleSelectHistory(id: string) {
    setActiveHistoryId(id)
    setChatKey((k) => k + 1)
  }

  function handleHistoryCreated(id: string) {
    setActiveHistoryId(id)
    void refetch()
  }

  return (
    <SidebarProvider className="h-svh overflow-hidden">
      <Sidebar
        histories={histories}
        loading={loading}
        activeHistoryId={activeHistoryId}
        onSelectHistory={handleSelectHistory}
        onNewChat={handleNewChat}
      />
      <SidebarInset className="flex flex-col h-full overflow-hidden">
        <ChatPanel
          key={chatKey}
          historyId={activeHistoryId}
          onHistoryCreated={handleHistoryCreated}
        />
      </SidebarInset>
    </SidebarProvider>
  )
}
