'use client'

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/base/alert-dialog'
import { useTranslation } from '@/plugins/i18n/client'
import { cn } from '@/utils/ui'
import { AlertCircle, AlertTriangle, CheckCircle2, Info } from 'lucide-react'
import { createContext, type ReactNode, useCallback, useContext, useMemo, useState } from 'react'

type MessageType = 'info' | 'success' | 'warning' | 'error'

interface ConfirmOptions {
  title: string
  description: string
  confirmText?: string
  cancelText?: string
  type?: MessageType
  showCancelButton?: boolean
  confirmButtonClass?: string
  cancelButtonClass?: string
  showClose?: boolean
}

interface MessageBoxContextValue {
  alert: (message: string, title: string, options?: Partial<ConfirmOptions>) => Promise<boolean>
  confirm: (message: string, title?: string, options?: Partial<ConfirmOptions>) => Promise<boolean>
}

const MessageBoxContext = createContext<MessageBoxContextValue | null>(null)

const TypeIcon = {
  info: Info,
  success: CheckCircle2,
  warning: AlertTriangle,
  error: AlertCircle,
}

const TypeStyles = {
  info: {
    icon: 'text-blue-500',
    button: 'bg-blue-500 hover:bg-blue-600',
  },
  success: {
    icon: 'text-green-500',
    button: 'bg-green-500 hover:bg-green-600',
  },
  warning: {
    icon: 'text-yellow-500',
    button: 'bg-yellow-500 hover:bg-yellow-600',
  },
  error: {
    icon: 'text-red-500',
    button: 'bg-destructive hover:bg-destructive/90',
  },
}

export function MessageBoxProvider({ children }: { children: ReactNode }) {
  const { t } = useTranslation(['global'])
  const [open, setOpen] = useState(false)
  const [options, setOptions] = useState<ConfirmOptions | null>(null)
  const [resolve, setResolve] = useState<((value: boolean) => void) | null>(null)

  const alert = useCallback((
    message: string,
    title: string,
    options?: Partial<ConfirmOptions>,
  ): Promise<boolean> => {
    const alertOptions: ConfirmOptions = {
      title,
      description: message,
      showCancelButton: false,
      type: 'info',
      ...options,
    }
    setOptions(alertOptions)
    setOpen(true)
    return new Promise((res) => {
      setResolve(() => res)
    })
  }, [])

  const confirm = useCallback((
    message: string,
    title?: string,
    options?: Partial<ConfirmOptions>,
  ): Promise<boolean> => {
    const confirmOptions: ConfirmOptions = {
      title: title || t('global.confirm'),
      description: message,
      showCancelButton: true,
      type: 'warning',
      ...options,
    }
    setOptions(confirmOptions)
    setOpen(true)
    return new Promise((res) => {
      setResolve(() => res)
    })
  }, [t])

  const handleConfirm = useCallback(() => {
    resolve?.(true)
    setOpen(false)
  }, [resolve])

  const handleCancel = useCallback(() => {
    resolve?.(false)
    setOpen(false)
  }, [resolve])

  const Icon = options?.type ? TypeIcon[options.type] : TypeIcon.info

  const contextValue = useMemo(() => ({ alert, confirm }), [alert, confirm])

  return (
    <MessageBoxContext.Provider value={contextValue}>
      {children}
      {options && (
        <AlertDialog open={open} onOpenChange={open => !open && handleCancel()}>
          <AlertDialogContent>
            <AlertDialogHeader className="flex flex-row gap-4">
              {options.type && (
                <div className={cn('mt-1', TypeStyles[options.type].icon)}>
                  <Icon className="h-5 w-5" />
                </div>
              )}
              <div className="flex-1">
                <AlertDialogTitle>{options.title}</AlertDialogTitle>
                <AlertDialogDescription>{options.description}</AlertDialogDescription>
              </div>
            </AlertDialogHeader>
            <AlertDialogFooter>
              {options.showCancelButton && (
                <AlertDialogCancel
                  onClick={handleCancel}
                  className={options.cancelButtonClass}
                >
                  {options.cancelText || t('global.cancel')}
                </AlertDialogCancel>
              )}
              <AlertDialogAction
                onClick={handleConfirm}
                className={cn(
                  options.type && TypeStyles[options.type].button,
                  options.confirmButtonClass,
                )}
              >
                {options.confirmText || t('global.confirm')}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      )}
    </MessageBoxContext.Provider>
  )
}

export function useMessageBox() {
  const context = useContext(MessageBoxContext)
  if (!context) {
    throw new Error('useMessageBox must be used within a MessageBoxProvider')
  }
  return context
}
