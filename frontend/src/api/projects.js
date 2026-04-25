import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

api.interceptors.response.use(
  (res) => res.data.data,
  (err) => Promise.reject(err.response?.data?.error ?? err)
)

export const getProjects = (params) => api.get('/projects', { params })
export const createProject = (data) => api.post('/projects', data)