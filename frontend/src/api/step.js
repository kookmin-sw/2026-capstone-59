import axios from 'axios'

function getCsrfToken() {
  return document.cookie
    .split('; ')
    .find(row => row.startsWith('csrf_token='))
    ?.split('=')[1]
}

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
})

const aiApi = axios.create({
  baseURL: '/ai',
  withCredentials: true,
})

const addCsrfInterceptor = (instance) => {
  instance.interceptors.request.use((config) => {
    const mutatingMethods = ['post', 'put', 'patch', 'delete']
    if (mutatingMethods.includes(config.method)) {
      const csrfToken = getCsrfToken()
      if (csrfToken) config.headers['X-CSRF-Token'] = csrfToken
    }
    return config
  })
  instance.interceptors.response.use(
    (res) => res.data.data,
    (err) => Promise.reject(err.response?.data?.error ?? err)
  )
}

addCsrfInterceptor(api)
addCsrfInterceptor(aiApi)

export const getStepTree = (projectId, stageId) =>
  api.get('/steps/tree', { params: { project_id: projectId, stage_id: stageId } })

export const generateSteps = (stepId) =>
  aiApi.post(`/steps/${stepId}/generate`)

export const acceptStep = (stepId) =>
  aiApi.post(`/steps/${stepId}/accept`)

export const createNotionTemplate = (stepId) =>
  aiApi.post(`/steps/${stepId}/notion-template`)

export const getStepDetail = (stepId) =>
  aiApi.get(`/steps/${stepId}`)