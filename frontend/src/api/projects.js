import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {  // 토큰 있을 때만 헤더 추가
    config.headers.Authorization = `Bearer ${token}`
  }
  return config  // 토큰 없으면 그냥 그대로 요청
})

api.interceptors.response.use(
  (res) => res.data.data,
  (err) => Promise.reject(err.response?.data?.error ?? err)
)

export const getProjects = (params) => api.get('/projects', { params })
export const createProject = (data) => api.post('/projects', data)