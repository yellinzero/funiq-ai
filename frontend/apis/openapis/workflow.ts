import type { ICreateWorkflowVersionPayload, ISaveWorkflowRequest } from '@/apis/types'
import { fetchApi } from '@/apis/core'
import {
  getOperatorsUrl,
  getWorkflowDebugSnapshotsUrl,
  getWorkflowEdgesUrl,
  getWorkflowNodesUrl,
  getWorkflowUrl,
  getWorkflowVersionsUrl,
  publishWorkflowUrl,
  updateWorkflowUrl,
} from '@/apis/paths/workflow'

export async function getWorkflowApi(workflowId: string) {
  return await fetchApi.GET(getWorkflowUrl, { params: { path: { workflow_id: workflowId } } })
}

export async function updateWorkflowApi(workflowId: string, body: ISaveWorkflowRequest) {
  return await fetchApi.PUT(updateWorkflowUrl, { params: { path: { workflow_id: workflowId } }, body })
}

export async function publishWorkflowApi(workflowId: string, body: ICreateWorkflowVersionPayload) {
  return await fetchApi.POST(publishWorkflowUrl, { params: { path: { workflow_id: workflowId } }, body })
}

export async function getWorkflowVersionsApi(workflowId: string) {
  return await fetchApi.GET(getWorkflowVersionsUrl, { params: { path: { workflow_id: workflowId } } })
}

export async function getWorkflowDebugSnapshotsApi(workflowId: string) {
  return await fetchApi.GET(getWorkflowDebugSnapshotsUrl, { params: { path: { workflow_id: workflowId } } })
}

export async function getWorkflowNodesApi(workflowId: string) {
  return await fetchApi.GET(getWorkflowNodesUrl, { params: { path: { workflow_id: workflowId } } })
}

export async function getWorkflowEdgesApi(workflowId: string) {
  return await fetchApi.GET(getWorkflowEdgesUrl, { params: { path: { workflow_id: workflowId } } })
}

export async function getOperatorsApi() {
  return await fetchApi.GET(getOperatorsUrl)
}
