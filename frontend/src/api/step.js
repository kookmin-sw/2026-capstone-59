import { createApi } from './_client'

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

// ─────────────────────────────────────────────────────────────
// Side Panel — 비동기 폴링
//
// 1. POST /steps/{id}/sidepanel-start  (fire-and-forget; 응답 안 기다림)
// 2. GET /steps/{id}/sidepanel-content 폴링 — 적응형 주기
//    - 새 chunk 도착 시: MIN_INTERVAL 로 빠르게 (활발한 스트리밍)
//    - 변경 없음 누적 시: 주기를 1.5x 씩 늘려 최대 MAX_INTERVAL 까지
//    - 변경 발생 시: 다시 MIN_INTERVAL 로 reset
// 3. is_complete 면 onDone/onError 후 폴링 중단
//
// abort() 는 클라이언트 폴링만 멈춤 — 백엔드는 끝까지 실행되어 DB 에 저장됨.
// ─────────────────────────────────────────────────────────────
const MIN_POLL_MS = 1000
const MAX_POLL_MS = 4000
const BACKOFF_AFTER_QUIET = 2 // 변경 없는 폴링이 N회 연속이면 주기 확대

export function createSidePanelStream(stepId) {
  let timeoutId = null
  let aborted = false

  return {
    start({ onChunk, onDone, onError }) {
      aborted = false
      api.post(`/steps/${stepId}/sidepanel-start`).catch(() => {
        // 시작 자체가 실패해도 폴링은 시도 — 이미 진행 중이면 폴링으로 잡힘.
      })

      let lastLen = 0
      let interval = MIN_POLL_MS
      let quietCount = 0

      const poll = async () => {
        if (aborted) return
        try {
          const { status, content, is_complete } = await api.get(
            `/steps/${stepId}/sidepanel-content`
          )

          const grew =
            typeof content === 'string' && content.length > lastLen
          if (grew) {
            onChunk?.(content.slice(lastLen))
            lastLen = content.length
            interval = MIN_POLL_MS // 활발 — 빠른 폴링
            quietCount = 0
          } else {
            quietCount += 1
            if (quietCount >= BACKOFF_AFTER_QUIET) {
              interval = Math.min(Math.round(interval * 1.5), MAX_POLL_MS)
            }
          }

          if (is_complete) {
            timeoutId = null
            status === 'error' ? onError?.() : onDone?.()
            return
          }
        } catch {
          // 일시적 네트워크 오류는 무시 — 다음 사이클에 재시도
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
