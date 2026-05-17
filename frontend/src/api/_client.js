import axios from 'axios'

// ─────────────────────────────────────────────────────────────
// 통합 axios 클라이언트
//
// - 호출부는 백엔드 path 를 그대로 쓴다 (예: '/projects', '/steps/tree').
//   ai/business 구분은 이 파일이 path 패턴으로 자동 분기한다.
// - 서버 주소는 환경변수 VITE_BUSINESS_SERVER_URL / VITE_AI_SERVER_URL
//   에서 받고, 미설정 시 localhost 기본값을 사용한다.
// - 동시 다발의 401 은 단일 refresh promise 로 합치고, refresh 자체가
//   실패하면 /login 으로 보낸다.
// ─────────────────────────────────────────────────────────────

const BUSINESS_BASE =
  import.meta.env.VITE_BUSINESS_SERVER_URL || 'http://localhost:8000'
const AI_BASE =
  import.meta.env.VITE_AI_SERVER_URL || 'http://localhost:8001'

const UUID =
  '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'

// AI 서버로 보낼 (method, path) 패턴. 그 외는 전부 business.
const AI_ROUTES = [
  { method: 'POST', pattern: new RegExp(`^/steps/${UUID}/accept$`) },
  { method: 'GET', pattern: new RegExp(`^/steps/${UUID}/sidepanel-stream$`) },
  { method: 'GET', pattern: new RegExp(`^/steps/${UUID}$`) },
  { method: 'POST', pattern: new RegExp(`^/projects/${UUID}/design-export$`) },
]

function pickBaseUrl(method, path) {
  const m = (method || 'GET').toUpperCase()
  const isAi = AI_ROUTES.some((r) => r.method === m && r.pattern.test(path))
  return isAi ? AI_BASE : BUSINESS_BASE
}

// path 를 절대 URL 로 변환. fetch (SSE 등) 직접 호출에 사용.
export function resolveApiUrl(method, path) {
  return `${pickBaseUrl(method, path)}${path}`
}

function getCsrfToken() {
  return document.cookie
    .split('; ')
    .find((row) => row.startsWith('csrf_token='))
    ?.split('=')[1]
}

// 동시 다발의 401 을 한 번의 refresh 로 합치기 위한 단일 promise.
let refreshPromise = null

function refreshTokens() {
  if (!refreshPromise) {
    refreshPromise = axios
      .post(`${BUSINESS_BASE}/auth/refresh`, null, { withCredentials: true })
      .finally(() => {
        refreshPromise = null
      })
  }
  return refreshPromise
}

function redirectToLogin() {
  if (typeof window === 'undefined') return
  const path = window.location.pathname
  if (path === '/login' || path === '/' || path.startsWith('/shared/')) return
  window.location.href = '/login'
}

function attachRouting(instance) {
  instance.interceptors.request.use((config) => {
    config.baseURL = pickBaseUrl(config.method, config.url)
    return config
  })
}

export function createApi() {
  const instance = axios.create({ withCredentials: true })

  attachRouting(instance)

  // CSRF 헤더 부착
  instance.interceptors.request.use((config) => {
    const mutating = ['post', 'put', 'patch', 'delete']
    if (mutating.includes(config.method?.toLowerCase())) {
      const csrf = getCsrfToken()
      if (csrf) {
        config.headers = config.headers ?? {}
        config.headers['X-CSRF-Token'] = csrf
      }
    }
    return config
  })

  // 응답: envelope unwrap + 401 자동 refresh & retry
  instance.interceptors.response.use(
    (res) => res.data?.data,
    async (err) => {
      const original = err.config
      const status = err.response?.status

      // refresh 자체가 실패 — 무한 루프 방지
      if (original?.url?.endsWith('/auth/refresh')) {
        redirectToLogin()
        return Promise.reject(err.response?.data?.error ?? err)
      }

      // 401 응답 — refresh 후 원래 요청 한 번 재시도
      if (status === 401 && original && !original._retry) {
        original._retry = true
        try {
          await refreshTokens()
          const newCsrf = getCsrfToken()
          if (newCsrf && original.headers) {
            original.headers['X-CSRF-Token'] = newCsrf
          }
          return instance(original)
        } catch (refreshErr) {
          redirectToLogin()
          return Promise.reject(refreshErr.response?.data?.error ?? refreshErr)
        }
      }

      return Promise.reject(err.response?.data?.error ?? err)
    }
  )

  return instance
}

// 인증 없이 동작하는 read-only 클라이언트 (share 페이지용)
export function createPublicApi() {
  const instance = axios.create({ withCredentials: true })
  attachRouting(instance)
  instance.interceptors.response.use(
    (res) => res.data?.data,
    (err) => Promise.reject(err.response?.data?.error ?? err)
  )
  return instance
}
