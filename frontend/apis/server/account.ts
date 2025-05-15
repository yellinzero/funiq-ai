'use server'
import type { IUserInfo } from '../types'
import { cookies } from 'next/headers'
import { getUserInfoApi } from '../openapis/account'

export async function getCurrentUser(): Promise<IUserInfo | null> {
  const session = (await cookies()).get('session')?.value
  if (!session)
    return null

  try {
    const { data } = await getUserInfoApi()
    return data ?? null
  }
  catch (error) {
    console.error('Failed to fetch user info:', error)
    return null
  }
}
