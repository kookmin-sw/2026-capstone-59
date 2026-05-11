import axios from 'axios'

function getCsrfToken() {
  return document.cookie
    .split('; ')
    .find(row => row.startsWith('csrf_token='))
    ?.split('=')[1]
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  withCredentials: true,
})

api.interceptors.request.use((config) => {
  const mutatingMethods = ['post', 'put', 'patch', 'delete']
  if (mutatingMethods.includes(config.method)) {
    const csrfToken = getCsrfToken()
    if (csrfToken) config.headers['X-CSRF-Token'] = csrfToken
  }
  return config
})

api.interceptors.response.use(
  (res) => res.data.data,
  (err) => Promise.reject(err.response?.data?.error ?? err)
)

export const getStages = (projectId) =>
  api.get('/stages', { params: { project_id: projectId } })

export const rollbackStage = (stageId) =>
  api.post(`/stages/${stageId}/rollback`)