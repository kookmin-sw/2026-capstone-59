import { createApi } from './_client'

const api = createApi()

export const getMe = () => api.get('/auth/me')
export const logout = () => api.post('/auth/logout')
