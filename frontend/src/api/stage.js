import { createApi } from './_client'

const api = createApi()

export const getStages = (projectId) =>
  api.get('/stages', { params: { project_id: projectId } })

export const rollbackStage = (stageId) =>
  api.post(`/stages/${stageId}/rollback`)
