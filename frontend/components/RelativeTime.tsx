import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/base/tooltip'
import { getRelativeTime } from '@/utils/time'

export default function RelativeTime({
  date,
  className,
}: {
  date: string
  className?: string
}) {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <span className={className}>{getRelativeTime(date)}</span>
        </TooltipTrigger>
        <TooltipContent>
          <span>{date}</span>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}
