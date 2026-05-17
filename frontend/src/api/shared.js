import { createPublicApi } from './_client'

const api = createPublicApi()

export const getSharedProject = (shareToken) =>
  api.get(`/shared/${shareToken}`)

export const getSharedStages = (shareToken) =>
  api.get(`/shared/${shareToken}/stages`)

export const getSharedStepTree = (shareToken, stageId) =>
  api.get(`/shared/${shareToken}/steps/tree`, { params: { stage_id: stageId } })

export const getSharedStepDetail = (shareToken, stepId) =>
  api.get(`/shared/${shareToken}/steps/${stepId}`)
