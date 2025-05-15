import type { ICreateAppRequest, IGetAppsQuery, IUpdateAppRequest } from '@/apis/types'
import { fetchApi } from '@/apis/core'
import {
  createAppUrl,
  deleteAppUrl,
  getAppsUrl,
  getAppUrl,
  updateAppUrl,
} from '@/apis/paths/app'

export async function getAppsApi(query: IGetAppsQuery) {
  return await fetchApi.GET(getAppsUrl, { params: { query } })
}

export async function createAppApi(body: ICreateAppRequest) {
  return await fetchApi.POST(createAppUrl, { body })
}

export async function getAppApi(appId: string) {
  return await fetchApi.GET(getAppUrl, { params: { path: { app_id: appId } } })
}

export async function updateAppApi(appId: string, body: IUpdateAppRequest) {
  return await fetchApi.PUT(updateAppUrl, { params: { path: { app_id: appId } }, body })
}

export async function deleteAppApi(appId: string) {
  return await fetchApi.DELETE(deleteAppUrl, { params: { path: { app_id: appId } } })
}
