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
// 2. 500ms 마다 GET /steps/{id}/sidepanel-content 로 누적 raw text 폴링
// 3. content 가 늘어난 만큼만 delta 로 onChunk 호출 (UI 는 누적 표시)
// 4. is_complete 면 onDone 또는 onError 후 폴링 중단
//
// abort() 는 클라이언트 폴링만 멈춤 — 백엔드는 끝까지 실행되어 DB 에 저장됨.
// ─────────────────────────────────────────────────────────────
const POLL_INTERVAL_MS = 500

export function createSidePanelStream(stepId) {
  let intervalId = null
  let aborted = false

  return {
    start({ onChunk, onDone, onError }) {
      aborted = false
      // 생성 시작 트리거 — 응답을 기다리지 않는다.
      api.post(`/steps/${stepId}/sidepanel-start`).catch(() => {
        // 시작 자체가 실패해도 폴링은 시도 — 이미 진행 중이면 폴링으로 잡힘.
      })

      let lastLen = 0

      const poll = async () => {
        if (aborted) return
        try {
          const { status, content, is_complete } = await api.get(
            `/steps/${stepId}/sidepanel-content`
          )

          // 새로 누적된 부분만 delta 로 전달 → UI 는 기존처럼 점진 표시
          if (typeof content === 'string' && content.length > lastLen) {
            const delta = content.slice(lastLen)
            lastLen = content.length
            onChunk?.(delta)
          }

          if (is_complete) {
            if (intervalId) clearInterval(intervalId)
            intervalId = null
            status === 'error' ? onError?.() : onDone?.()
          }
        } catch {
          // 일시적 네트워크 오류는 무시하고 다음 사이클에 재시도
        }
      }

      intervalId = setInterval(poll, POLL_INTERVAL_MS)
      poll() // 첫 호출은 즉시
    },

    abort() {
      aborted = true
      if (intervalId) clearInterval(intervalId)
      intervalId = null
    },
  }
}
