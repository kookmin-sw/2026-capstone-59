import { createApi, resolveApiUrl } from './_client'

const api = createApi()

export const getStepTree = (projectId, stageId) =>
  api.get('/steps/tree', { params: { project_id: projectId, stage_id: stageId } })

export const getStepTreeBySequence = (projectId, stageSequence) =>
  api.get('/steps/tree', { params: { project_id: projectId, stage_sequence: stageSequence } })

export const acceptStep = (stepId) =>
  api.post(`/steps/${stepId}/accept`)

export const getStepDetail = (stepId) =>
  api.get(`/steps/${stepId}`)

export const rollbackStep = (stepId) =>
  api.post(`/steps/${stepId}/rollback`)

export const keepStep = (stepId, isKeep) =>
  api.post(`/steps/${stepId}/keep`, { is_keep: isKeep })

export function createSidePanelStream(stepId) {
  let abortController = null

  return {
    start({ onChunk, onDone, onError }) {
      abortController = new AbortController()

      ;(async () => {
        try {
          const url = resolveApiUrl('GET', `/steps/${stepId}/sidepanel-stream`)
          const response = await fetch(url, {
            method: 'GET',
            headers: {
              Accept: 'text/event-stream',
            },
            credentials: 'include',
            signal: abortController.signal,
          })

          if (!response.ok || !response.body) {
            onError?.()
            return
          }

          const reader = response.body.getReader()
          const decoder = new TextDecoder()
          let buffer = ''
          let currentEvent = null

          while (true) {
            const { done, value } = await reader.read()
            if (done) break

            buffer += decoder.decode(value, { stream: true })
            const lines = buffer.split('\n')
            buffer = lines.pop() ?? ''

            for (const line of lines) {
              if (line.startsWith('event: ')) {
                currentEvent = line.slice(7).trim()
              } else if (line.startsWith('data: ')) {
                if (currentEvent === 'done') {
                  onDone?.()
                  return
                }
                if (currentEvent === 'error') {
                  onError?.()
                  return
                }

                try {
                  const json = JSON.parse(line.slice(6))
                  if (json.delta) onChunk?.(json.delta)
                } catch {
                  //
                }

                currentEvent = null
              } else if (line === '') {
                currentEvent = null
              }
            }
          }

          onDone?.()
        } catch (err) {
          if (err.name === 'AbortError') return
          onError?.()
        }
      })()
    },

    abort() {
      abortController?.abort()
    },
  }
}
