import axios from 'axios'

// csrf_token 쿠키에서 읽기
function getCsrfToken() {
  return document.cookie
    .split('; ')
    .find(row => row.startsWith('csrf_token='))
    ?.split('=')[1]
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  withCredentials: true, // 쿠키 자동 전송 (fetch의 credentials: 'include'와 동일)
})

api.interceptors.request.use((config) => {
  // POST/PUT/PATCH/DELETE 요청에만 CSRF 토큰 헤더 추가
  const mutatingMethods = ['post', 'put', 'patch', 'delete']
  if (mutatingMethods.includes(config.method)) {
    const csrfToken = getCsrfToken()
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken
    }
  }
  return config
})

api.interceptors.response.use(
  (res) => res.data.data,
  (err) => Promise.reject(err.response?.data?.error ?? err)
)

export const getProjects = (params) => api.get('/projects', { params })
export const createProject = (data) => api.post('/projects', data)
export const deleteProject = (projectId) => api.delete(`/projects/${projectId}`)
export const updateProject = (projectId, data) => api.patch(`/projects/${projectId}`, data)
export const createShare = (projectId) => api.post(`/projects/${projectId}/share`)
export const deleteShare = (projectId) => api.delete(`/projects/${projectId}/share`)
export const restoreProject = (projectId) => updateProject(projectId, { is_deleted: false })