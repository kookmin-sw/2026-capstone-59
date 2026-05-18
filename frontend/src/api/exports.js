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
const MAX_TRANSIENT_FAILURES = 5

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

// ─── 진행 중인 job_id 를 localStorage 에 보관 (새로고침 후 복구용) ───
const STORAGE_KEY = (projectId) => `design_export_job:${projectId}`

export function getDesignExportJobId(projectId) {
  try {
    return localStorage.getItem(STORAGE_KEY(projectId)) || null
  } catch {
    return null
  }
}

function saveDesignExportJobId(projectId, jobId) {
  try {
    localStorage.setItem(STORAGE_KEY(projectId), jobId)
  } catch {
    /* */
  }
}

export function clearDesignExportJobId(projectId) {
  try {
    localStorage.removeItem(STORAGE_KEY(projectId))
  } catch {
    /* */
  }
}

function getStatusCode(err) {
  return err?.response?.status ?? err?.status ?? null
}

/**
 * Design Export 스트림 생성/재개.
 *
 * @param {string} projectId
 * @param {string[]} selectedStepIds  selected step ids — resumeJobId 가 있으면 무시됨
 * @param {object} [opts]
 * @param {string} [opts.resumeJobId]  기존 job_id 로 재개 (POST 생략, 폴링만 시작)
 */
export function createDesignExportStream(projectId, selectedStepIds, opts = {}) {
  let timeoutId = null
  let aborted = false

  return {
    start({ onComplete, onError } = {}) {
      aborted = false
      const jobId = opts.resumeJobId || generateJobId()

      if (!opts.resumeJobId) {
        // 새 job — localStorage 에 기록 + 트리거 POST
        saveDesignExportJobId(projectId, jobId)
        api
          .post(`/projects/${projectId}/design-export-start`, {
            job_id: jobId,
            selected_step_ids: selectedStepIds,
          })
          .catch(() => {
            // 사전검증 실패(rate limit / 빈 selection 등) 가능 — 폴링이 곧 알아냄.
          })
      }

      let interval = MIN_POLL_MS
      let quietCount = 0
      let lastStatus = null
      let transientFailures = 0

      const stop = (kind, payload) => {
        timeoutId = null
        aborted = true
        clearDesignExportJobId(projectId)
        if (kind === 'done') onComplete?.(payload)
        else onError?.(payload)
      }

      const poll = async () => {
        if (aborted) return
        try {
          const res = await api.get(
            `/projects/${projectId}/design-export-jobs/${jobId}`
          )
          transientFailures = 0

          const { status, markdown, filename, error_code, is_complete } = res

          if (is_complete) {
            return status === 'done'
              ? stop('done', { markdown, filename })
              : stop('error', { code: error_code || 'DESIGN_EXPORT_FAILED' })
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
        } catch (err) {
          const code = getStatusCode(err)
          // 4xx — 종료 신호. 더 폴링해도 의미 없음.
          if (code !== null && code >= 400 && code < 500) {
            return stop('error', { code: 'DESIGN_EXPORT_FAILED' })
          }
          // 5xx / 네트워크 오류 — 한도까지 재시도
          transientFailures += 1
          if (transientFailures >= MAX_TRANSIENT_FAILURES) {
            return stop('error', { code: 'DESIGN_EXPORT_NETWORK_ERROR' })
          }
        }

        if (!aborted) {
          timeoutId = setTimeout(poll, interval)
        }
      }

      poll() // 첫 호출은 즉시
    },

    abort() {
      // 사용자가 명시적으로 취소 — 백엔드 작업은 계속되지만 클라이언트 입장에선 버려짐.
      // localStorage 도 정리해서 새로고침 시 재개되지 않게.
      aborted = true
      if (timeoutId) clearTimeout(timeoutId)
      timeoutId = null
      clearDesignExportJobId(projectId)
    },
  }
}
