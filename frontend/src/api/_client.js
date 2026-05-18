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

function isAiRoute(method, path) {
  const m = (method || 'GET').toUpperCase()
  return AI_ROUTES.some((r) => r.method === m && r.pattern.test(path))
}

function pickBaseUrl(method, path) {
  return isAiRoute(method, path) ? AI_BASE : BUSINESS_BASE
}

// path 를 절대 URL 로 변환. fetch (SSE 등) 직접 호출에 사용.
export function resolveApiUrl(method, path) {
  return `${pickBaseUrl(method, path)}${path}`
}

// cross-site 셋업에서 JS 가 쿠키를 직접 읽을 수 없으므로,
// 백엔드가 /auth/me, /auth/refresh 응답 body 로 내려준 토큰들을
// sessionStorage 에 보관해 헤더로 부착한다.
//
// - csrf_token : 모든 mutating 요청의 X-CSRF-Token 헤더
// - access_token: AI Lambda Function URL 호출 시 Authorization 헤더
//                 (Function URL 은 별도 도메인이라 쿠키가 안 감)
const CSRF_STORAGE_KEY = 'csrf_token'
const ACCESS_TOKEN_STORAGE_KEY = 'access_token'

export function getCsrfToken() {
  try {
    return sessionStorage.getItem(CSRF_STORAGE_KEY) ?? undefined
  } catch {
    return undefined
  }
}

export function setCsrfToken(token) {
  if (!token) return
  try {
    sessionStorage.setItem(CSRF_STORAGE_KEY, token)
  } catch {
    /* sessionStorage 불가 환경 — 무시 */
  }
}

export function getAccessToken() {
  try {
    return sessionStorage.getItem(ACCESS_TOKEN_STORAGE_KEY) ?? undefined
  } catch {
    return undefined
  }
}

export function setAccessToken(token) {
  if (!token) return
  try {
    sessionStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, token)
  } catch {
    /* */
  }
}

export function clearAuthTokens() {
  try {
    sessionStorage.removeItem(CSRF_STORAGE_KEY)
    sessionStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY)
  } catch {
    /* */
  }
}

// 후위 호환을 위해 유지 (auth.js 의 logout 에서 사용)
export const clearCsrfToken = clearAuthTokens

// 동시 다발의 401 을 한 번의 refresh 로 합치기 위한 단일 promise.
let refreshPromise = null

function refreshTokens() {
  if (!refreshPromise) {
    refreshPromise = axios
      .post(`${BUSINESS_BASE}/auth/refresh`, null, { withCredentials: true })
      .then((res) => {
        // 새 csrf_token / access_token 을 응답 body 에서 받아 sessionStorage 갱신
        const data = res?.data?.data
        if (data?.csrf_token) setCsrfToken(data.csrf_token)
        if (data?.access_token) setAccessToken(data.access_token)
        return res
      })
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

  // CSRF + Authorization Bearer 헤더 부착
  instance.interceptors.request.use((config) => {
    config.headers = config.headers ?? {}

    const mutating = ['post', 'put', 'patch', 'delete']
    if (mutating.includes(config.method?.toLowerCase())) {
      const csrf = getCsrfToken()
      if (csrf) config.headers['X-CSRF-Token'] = csrf
    }

    // AI 라우트는 별도 도메인이라 쿠키가 안 가므로 Bearer 헤더로 폴백
    if (isAiRoute(config.method, config.url)) {
      const accessToken = getAccessToken()
      if (accessToken) config.headers['Authorization'] = `Bearer ${accessToken}`
    }

    return config
  })

  // 응답: envelope unwrap + 401 자동 refresh & retry
  instance.interceptors.response.use(
    (res) => {
      const data = res.data?.data
      // /auth/me, /auth/refresh 등의 응답에 토큰이 포함되면 sessionStorage 갱신
      if (data && typeof data === 'object') {
        if (data.csrf_token) setCsrfToken(data.csrf_token)
        if (data.access_token) setAccessToken(data.access_token)
      }
      return data
    },
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
          // refresh 로 갱신된 새 토큰들로 헤더 교체
          original.headers = original.headers ?? {}
          const newCsrf = getCsrfToken()
          if (newCsrf) original.headers['X-CSRF-Token'] = newCsrf
          if (isAiRoute(original.method, original.url)) {
            const newAccess = getAccessToken()
            if (newAccess) original.headers['Authorization'] = `Bearer ${newAccess}`
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
