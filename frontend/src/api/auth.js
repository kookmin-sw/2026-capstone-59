import { clearSession, createApi } from './_client'

const api = createApi()

export const getMe = () => api.get('/auth/me')

export const logout = async () => {
  try {
    return await api.post('/auth/logout')
  } finally {
    clearSession()
  }
}
