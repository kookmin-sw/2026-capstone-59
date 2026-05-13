import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  withCredentials: true,
})

api.interceptors.response.use(
  (res) => res.data.data,
  (err) => Promise.reject(err.response?.data?.error ?? err)
)

export const getSharedProject = (shareToken) =>
  api.get(`/shared/${shareToken}`)

export const getSharedStages = (shareToken) =>
  api.get(`/shared/${shareToken}/stages`)

export const getSharedStepTree = (shareToken, stageId) =>
  api.get(`/shared/${shareToken}/steps/tree`, { params: { stage_id: stageId } })

export const getSharedStepDetail = (shareToken, stepId) =>
  api.get(`/shared/${shareToken}/steps/${stepId}`)