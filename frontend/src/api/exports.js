import { createApi } from './_client'

const api = createApi()                                          // Business (/api)
const AI_BASE = import.meta.env.VITE_AI_URL || '/ai'

function getCsrfToken() {
  return document.cookie
    .split('; ')
    .find(row => row.startsWith('csrf_token='))
    ?.split('=')[1]
}

// 1) 사전 조회 — accept된 RS 목록
export const getAcceptedRequiredSteps = (projectId) =>
  api.get(`/projects/${projectId}/accepted-required-steps`)
  // 응답 envelope unwrap 후: { required_steps: [{ step_id, name, stage_sequence }, ...] }

// 2) design-export SSE
export function createDesignExportStream(projectId, selectedStepIds) {
  let abortController = null

  return {
    start({ onComplete, onError } = {}) {
      abortController = new AbortController()

      ;(async () => {
        try {
          const csrf = getCsrfToken()
          const res = await fetch(`${AI_BASE}/projects/${projectId}/design-export`, {
            method: 'POST',
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'text/event-stream',
              ...(csrf ? { 'X-CSRF-Token': csrf } : {}),
            },
            body: JSON.stringify({ selected_step_ids: selectedStepIds }),
            signal: abortController.signal,
          })

          if (!res.ok || !res.body) {
            let code = 'DESIGN_EXPORT_FAILED'
            try {
              const body = await res.json()
              code = body?.error?.code ?? body?.code ?? code
            } catch { /* */ }
            onError?.({ code, status: res.status })
            return
          }

          const reader = res.body.getReader()
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
                const dataStr = line.slice(6)

                if (currentEvent === 'keepalive') {
                  currentEvent = null
                  continue
                }

                let data
                try { data = JSON.parse(dataStr) } catch { data = null }

                if (currentEvent === 'complete') {
                  onComplete?.(data)
                  return
                }
                if (currentEvent === 'error') {
                  onError?.(data ?? { code: 'DESIGN_EXPORT_FAILED' })
                  return
                }

                currentEvent = null
              } else if (line === '') {
                currentEvent = null
              }
            }
          }
        } catch (err) {
          if (err.name === 'AbortError') return
          onError?.({ code: 'DESIGN_EXPORT_NETWORK_ERROR', message: err?.message })
        }
      })()
    },

    abort() {
      abortController?.abort()
    },
  }
}