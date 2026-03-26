import { Toaster } from '@/components/ui/sonner'
import { TooltipProvider } from '@/components/ui/tooltip'
import { AppShell } from '@/components/layout/AppShell'

function App() {
  return (
    <TooltipProvider>
      <AppShell />
      <Toaster />
    </TooltipProvider>
  )
}

export default App
