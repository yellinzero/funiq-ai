import type { getConversationsUrl } from '@/apis/paths/conversation'
import type { ExtractParamsType } from '@/apis/types/helpers'
import type { components } from '@/types/openapi'

type IComponentsSchemas = components['schemas']

// Conversation related types
export type IGetConversationsQuery = NonNullable<ExtractParamsType<'get', typeof getConversationsUrl>>['query']
export type IConversationInfo = IComponentsSchemas['ConversationInfo']
export type IConversationStatus = IComponentsSchemas['ConversationStatus']
export type IConversationListResponse = IComponentsSchemas['ConversationListResponse']
export type ICreateConversationRequest = IComponentsSchemas['CreateConversationRequest']
export type IUpdateConversationRequest = IComponentsSchemas['UpdateConversationRequest']
export type IMessageInfo = IComponentsSchemas['MessageInfo']
export type IMessageFrom = IComponentsSchemas['MessageFrom']
export type ICompletionRequest = IComponentsSchemas['CompletionRequest']
