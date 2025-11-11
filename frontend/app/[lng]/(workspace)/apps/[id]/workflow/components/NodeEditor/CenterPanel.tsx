'use client'

import type { WorkflowNode } from '@/app/[lng]/(workspace)/apps/[id]/workflow/types'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/base/form'
import { Input } from '@/components/base/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/base/tabs'
import { Textarea } from '@/components/base/textarea'
import { useTranslation } from '@/plugins/i18n/client'
import { cn } from '@/utils/ui'
import { zodResolver } from '@hookform/resolvers/zod'
import { isEqual } from 'lodash-es'
import dynamic from 'next/dynamic'
import { useEffect, useMemo } from 'react'
import { useForm } from 'react-hook-form'
import * as z from 'zod'

const JsonSchemaForm = dynamic(() => import('@/components/JsonSchemaForm'), {
  ssr: false,
})

// Schema for node settings form validation
const nodeSettingsSchema = z.object({
  id: z.string(),
  operator: z.string(),
  name: z.string().min(1, { message: 'app.node_name_is_required' }),
  description: z.string().optional(),
})

type NodeSettingsForm = z.infer<typeof nodeSettingsSchema>

interface CenterPanelProps {
  node: WorkflowNode
  operatorInfo: any
  onNodeBasicSettingChange?: (data: { name?: string, description?: string }) => void
  onConfigChange: (data: Record<string, any>) => void
  leftButton?: React.ReactNode
  rightButton?: React.ReactNode
  className?: string
}

export function CenterPanel({
  node,
  operatorInfo,
  onNodeBasicSettingChange,
  onConfigChange,
  leftButton,
  rightButton,
  className,
}: CenterPanelProps) {
  const { t } = useTranslation(['app'])

  // Default form values based on node data
  const defaultValues = useMemo(() => ({
    id: node.id || '',
    operator: node.data.operator || '',
    name: node.data.name || `${node.data.operator}-${node.id}`,
    description: node.data.description || '',
  }), [node])

  // Form instance with validation schema
  const form = useForm<NodeSettingsForm>({
    resolver: zodResolver(nodeSettingsSchema),
    defaultValues,
    mode: 'onChange',
  })

  // Watch form changes and propagate via callback
  useEffect(() => {
    const subscription = form.watch((value) => {
      if (!value.name) {
        return
      }
      onNodeBasicSettingChange?.({
        name: value.name?.trim(),
        description: value.description?.trim() || '',
      })
    })
    return () => subscription.unsubscribe()
  }, [form, onNodeBasicSettingChange])

  // Update form when node data changes externally
  useEffect(() => {
    const currentFormData = form.getValues()
    if (node && !isEqual(currentFormData, defaultValues)) {
      form.reset(defaultValues)
    }
  }, [node, form, defaultValues])

  // Custom styling for tab triggers
  const tabsTriggerClassName = 'data-[state=active]:border-t-0 data-[state=active]:border-x-0 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none !shadow-none'

  return (
    <Tabs defaultValue="parameters" className={cn('flex flex-col h-full', className)}>
      <div className="flex items-center justify-between border-b flex-shrink-0">
        {leftButton}
        <TabsList className="flex-1 h-12 bg-transparent p-0">
          <TabsTrigger
            value="parameters"
            className={tabsTriggerClassName}
          >
            {t('app.parameters')}
          </TabsTrigger>
          <TabsTrigger
            value="settings"
            className={tabsTriggerClassName}
          >
            {t('app.basic_settings')}
          </TabsTrigger>
        </TabsList>
        {rightButton}
      </div>

      <TabsContent value="parameters" className="py-3 px-6 flex-1 overflow-y-auto">
        {operatorInfo.config_schema?.json_schema && (
          <JsonSchemaForm
            schema={operatorInfo.config_schema.json_schema}
            formData={node.data.config || {}}
            onChange={({ formData }) => onConfigChange(formData)}
            hideSubmitButton
          />
        )}
      </TabsContent>

      <TabsContent value="settings" className="py-3 px-6 flex-1 overflow-y-auto">
        <div className="space-y-4">
          <h3 className="text-sm font-medium text-foreground">{t('app.basic_settings')}</h3>

          <Form {...form}>
            <form className="space-y-4">
              {/* Node ID field */}
              <FormField
                control={form.control}
                name="id"
                disabled
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium text-muted-foreground">
                      { t('app.node_id')}
                    </FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Node type field */}
              <FormField
                control={form.control}
                name="operator"
                disabled
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium text-muted-foreground">
                      {t('app.node_type')}
                    </FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      {operatorInfo.description}
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Node name field */}
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium text-muted-foreground">{t('app.node_name')}</FormLabel>
                    <FormControl>
                      <Input
                        placeholder={t('app.text.name_placeholder')}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Node description field */}
              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium text-muted-foreground">{t('app.node_description')}</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder={t('app.text.description_placeholder')}
                        className="resize-none"
                        rows={3}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </form>
          </Form>
        </div>
      </TabsContent>
    </Tabs>
  )
}
