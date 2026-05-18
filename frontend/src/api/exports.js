import { createApi } from './_client'

const api = createApi()

// 1) 사전 조회 — accept된 RS 목록
export const getAcceptedRequiredSteps = (projectId) =>
  api.get(`/projects/${projectId}/accepted-required-steps`)

// ─────────────────────────────────────────────────────────────
// Design Export — 비동기 폴링
//
// 1. job_id 를 클라이언트가 생성 (crypto.randomUUID).
// 2. POST /projects/{id}/design-export-start  (fire-and-forget)
// 3. GET /projects/{id}/design-export-jobs/{job_id} 적응형 폴링.
// 4. is_complete 면 onComplete({markdown, filename}) 또는 onError({code}).
//
// abort() 는 클라이언트 폴링만 멈춤 — 백엔드 작업은 계속되지만 결과는
// 클라이언트 입장에서 버려진다.
// ─────────────────────────────────────────────────────────────
const MIN_POLL_MS = 1000
const MAX_POLL_MS = 4000
const BACKOFF_AFTER_QUIET = 2

function generateJobId() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  // 폴백 — 매우 단순한 UUID v4 비슷 (보안용 아님; 식별자 용도)
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

export function createDesignExportStream(projectId, selectedStepIds) {
  let timeoutId = null
  let aborted = false

  return {
    start({ onComplete, onError } = {}) {
      aborted = false
      const jobId = generateJobId()

      // 생성 트리거 — 응답 안 기다림
      api
        .post(`/projects/${projectId}/design-export-start`, {
          job_id: jobId,
          selected_step_ids: selectedStepIds,
        })
        .catch(() => {
          // 사전검증 실패(rate limit / 빈 selection 등) 가능 — 폴링이 곧 알아냄.
        })

      let interval = MIN_POLL_MS
      let quietCount = 0
      let lastStatus = null

      const poll = async () => {
        if (aborted) return
        try {
          const res = await api.get(
            `/projects/${projectId}/design-export-jobs/${jobId}`
          )
          const { status, markdown, filename, error_code, is_complete } = res

          if (is_complete) {
            timeoutId = null
            if (status === 'done') {
              onComplete?.({ markdown, filename })
            } else {
              onError?.({ code: error_code || 'DESIGN_EXPORT_FAILED' })
            }
            return
          }

          // 진행 중 — 상태 변화 없으면 점진적으로 주기 늘림
          if (status === lastStatus) {
            quietCount += 1
            if (quietCount >= BACKOFF_AFTER_QUIET) {
              interval = Math.min(Math.round(interval * 1.5), MAX_POLL_MS)
            }
          } else {
            interval = MIN_POLL_MS
            quietCount = 0
            lastStatus = status
          }
        } catch {
          // 일시적 네트워크 오류 — 다음 사이클 재시도
        }

        if (!aborted) {
          timeoutId = setTimeout(poll, interval)
        }
      }

      poll() // 첫 호출은 즉시
    },

    abort() {
      aborted = true
      if (timeoutId) clearTimeout(timeoutId)
      timeoutId = null
    },
  }
}
