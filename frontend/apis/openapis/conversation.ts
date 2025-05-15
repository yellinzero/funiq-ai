import type { ICompletionRequest, ICreateConversationRequest, IGetConversationsQuery, IUpdateConversationRequest } from '@/apis/types'
import { fetchApi } from '@/apis/core'
import {
  completionUrl,
  createConversationUrl,
  deleteConversationUrl,
  getConversationsUrl,
  getConversationUrl,
  getMessagesUrl,
  updateConversationUrl,
} from '@/apis/paths/conversation'

export async function getConversationsApi(appId: string, query?: IGetConversationsQuery) {
  return await fetchApi.GET(getConversationsUrl, { params: { path: { app_id: appId }, query } })
}

export async function createConversationApi(appId: string, body: ICreateConversationRequest) {
  return await fetchApi.POST(createConversationUrl, { params: { path: { app_id: appId } }, body })
}

export async function getConversationApi(conversationId: string) {
  return await fetchApi.GET(getConversationUrl, { params: { path: { conversation_id: conversationId } } })
}

export async function updateConversationApi(
  conversationId: string,
  body: IUpdateConversationRequest,
) {
  return await fetchApi.PUT(updateConversationUrl, { params: { path: { conversation_id: conversationId } }, body })
}

export async function deleteConversationApi(conversationId: string) {
  return await fetchApi.DELETE(deleteConversationUrl, { params: { path: { conversation_id: conversationId } } })
}

export async function getMessagesApi(conversationId: string) {
  return await fetchApi.GET(getMessagesUrl, { params: { path: { conversation_id: conversationId } } })
}

export async function completionApi(conversationId: string, body: ICompletionRequest) {
  return await fetchApi.POST(completionUrl, { params: { path: { conversation_id: conversationId } }, body })
}
