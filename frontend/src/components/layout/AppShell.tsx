import { useState } from 'react'
import { useHistories } from '@/hooks/useHistories'
import { ChatPanel } from '@/components/chat/ChatPanel'
import { Sidebar } from './Sidebar'
import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar'

export function AppShell() {
  const [activeHistoryId, setActiveHistoryId] = useState<string | null>(null)
  // chatPanelHistoryId is what ChatPanel loads — only changes on explicit navigation,
  // not when the server assigns an id to a newly created chat mid-stream.
  const [chatPanelHistoryId, setChatPanelHistoryId] = useState<string | null>(null)
  const [chatKey, setChatKey] = useState(0)
  const { histories, loading, refetch } = useHistories()

  function handleNewChat() {
    setActiveHistoryId(null)
    setChatPanelHistoryId(null)
    setChatKey((k) => k + 1)
  }

  function handleSelectHistory(id: string) {
    setActiveHistoryId(id)
    setChatPanelHistoryId(id)
    setChatKey((k) => k + 1)
  }

  function handleHistoryCreated(id: string) {
    // Update the sidebar highlight without touching chatPanelHistoryId —
    // ChatPanel is already mid-stream and must not reload.
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
          historyId={chatPanelHistoryId}
          onHistoryCreated={handleHistoryCreated}
        />
      </SidebarInset>
    </SidebarProvider>
  )
}
