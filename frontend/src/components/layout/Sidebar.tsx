import { SquarePen } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import {
  Sidebar as ShadcnSidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarSeparator,
  SidebarMenuSkeleton,
} from '@/components/ui/sidebar'
import type { ChatHistory } from '@/hooks/useHistories'

interface Props {
  histories: ChatHistory[]
  loading: boolean
  activeHistoryId: string | null
  onSelectHistory: (id: string) => void
  onNewChat: () => void
}

export function Sidebar({ histories, loading, activeHistoryId, onSelectHistory, onNewChat }: Props) {
  return (
    <ShadcnSidebar>
      <SidebarHeader className="flex flex-row items-center justify-between px-4 py-3">
        <span className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          Assignment Assist
        </span>
        <Tooltip>
          <TooltipTrigger
            onClick={onNewChat}
            className="inline-flex items-center justify-center rounded-md text-muted-foreground hover:text-primary hover:bg-accent h-7 w-7 transition-colors"
          >
            <SquarePen className="w-4 h-4" />
          </TooltipTrigger>
          <TooltipContent>New conversation</TooltipContent>
        </Tooltip>
      </SidebarHeader>

      <SidebarSeparator />

      <SidebarContent className="px-2 py-2">
        {loading ? (
          <SidebarMenu>
            {[1, 2, 3].map((i) => (
              <SidebarMenuItem key={i}>
                <SidebarMenuSkeleton />
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        ) : histories.length === 0 ? (
          <p className="text-xs text-muted-foreground px-3 py-2">No conversations yet.</p>
        ) : (
          <SidebarMenu>
            {histories.map((h) => (
              <SidebarMenuItem key={h.id}>
                <SidebarMenuButton
                  onClick={() => onSelectHistory(h.id)}
                  isActive={activeHistoryId === h.id}
                  className={cn('truncate', activeHistoryId === h.id && 'text-primary')}
                >
                  {h.preview}
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        )}
      </SidebarContent>
    </ShadcnSidebar>
  )
}
