import { createApi } from './_client'

const api = createApi()

export const getProjects = (params) => api.get('/projects', { params })
export const createProject = (data) => api.post('/projects', data)
export const deleteProject = (projectId) => api.delete(`/projects/${projectId}`)
export const updateProject = (projectId, data) => api.patch(`/projects/${projectId}`, data)
export const getShareStatus = (projectId) => api.get(`/projects/${projectId}/share`)
export const createShare = (projectId) => api.post(`/projects/${projectId}/share`)
export const deleteShare = (projectId) => api.delete(`/projects/${projectId}/share`)
export const restoreProject = (projectId) => updateProject(projectId, { is_deleted: false })
