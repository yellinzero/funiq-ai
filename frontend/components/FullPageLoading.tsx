import { Loader2 } from 'lucide-react'

export default function FullPageLoading() {
  return (
    <div className="flex justify-center items-center h-full w-full">
      <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
    </div>
  )
}
