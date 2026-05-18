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

// Side panel 현재 진행 상태 1회 조회 (폴링 시작 전 probe 용).
export const getSidePanelContent = (stepId) =>
  api.get(`/steps/${stepId}/sidepanel-content`)

// ─────────────────────────────────────────────────────────────
// Side Panel — 비동기 폴링
//
// 1. POST /steps/{id}/sidepanel-start  (fire-and-forget; 응답 안 기다림)
// 2. GET /steps/{id}/sidepanel-content 폴링 — 적응형 주기
//    - 새 chunk 도착 시: MIN_INTERVAL 로 빠르게 (활발한 스트리밍)
//    - 변경 없음 누적 시: 주기를 1.5x 씩 늘려 최대 MAX_INTERVAL 까지
//    - 변경 발생 시: 다시 MIN_INTERVAL 로 reset
// 3. is_complete 면 onDone/onError 후 폴링 중단
// 4. 4xx: 종료 신호로 간주 — 폴링 중단 / 5xx·네트워크 오류: MAX 재시도 후 포기
//
// onChunk(content) 는 **누적된 full content** 를 전달한다 (delta 가 아님).
// — 새로고침 후 복구 시 등에 buf 가 미리 채워져 있어도 중복 누적되지 않도록.
// 소비자는 `b.text = content` 식으로 단순 대입하면 된다.
//
// abort() 는 클라이언트 폴링만 멈춤 — 백엔드는 끝까지 실행되어 DB 에 저장됨.
// ─────────────────────────────────────────────────────────────
const MIN_POLL_MS = 1000
const MAX_POLL_MS = 4000
const BACKOFF_AFTER_QUIET = 2 // 변경 없는 폴링이 N회 연속이면 주기 확대
const MAX_TRANSIENT_FAILURES = 5 // 5xx / 네트워크 오류 누적 한도

function getStatusCode(err) {
  // axios err 와 _client.js 응답 interceptor 가 던지는 envelope 에러 모두 대응
  return err?.response?.status ?? err?.status ?? null
}

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
      let transientFailures = 0

      const stop = (kind) => {
        timeoutId = null
        aborted = true
        if (kind === 'error') onError?.()
        else onDone?.()
      }

      const poll = async () => {
        if (aborted) return
        try {
          const { status, content, is_complete } = await api.get(
            `/steps/${stepId}/sidepanel-content`
          )

          transientFailures = 0 // 성공 시 카운터 리셋

          const text = typeof content === 'string' ? content : ''
          const grew = text.length > lastLen
          if (grew) {
            // 누적 content 전체를 전달 (delta 가 아님)
            onChunk?.(text)
            lastLen = text.length
            interval = MIN_POLL_MS // 활발 — 빠른 폴링
            quietCount = 0
          } else {
            quietCount += 1
            if (quietCount >= BACKOFF_AFTER_QUIET) {
              interval = Math.min(Math.round(interval * 1.5), MAX_POLL_MS)
            }
          }

          if (is_complete) {
            return stop(status === 'error' ? 'error' : 'done')
          }
        } catch (err) {
          const code = getStatusCode(err)
          // 4xx — 종료 신호. 더 폴링해도 의미 없음.
          if (code !== null && code >= 400 && code < 500) {
            return stop('error')
          }
          // 5xx / 네트워크 오류 — 한도까지 재시도, 초과 시 포기
          transientFailures += 1
          if (transientFailures >= MAX_TRANSIENT_FAILURES) {
            return stop('error')
          }
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
