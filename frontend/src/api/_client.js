import axios from 'axios'

// ─────────────────────────────────────────────────────────────
// 공통 axios 클라이언트 팩토리
// - withCredentials (HttpOnly 쿠키 자동 전송)
// - 변경 요청에 X-CSRF-Token 헤더 부착
// - 응답 envelope 자동 unwrap (res.data.data)
// - 401 응답 시 자동으로 /auth/refresh 후 원래 요청 재시도
// - refresh 가 동시 다발로 호출되지 않도록 단일 promise 큐
// - refresh 자체가 실패하면 /login 으로 리다이렉트
// ─────────────────────────────────────────────────────────────

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

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
    // 별도 axios 인스턴스로 호출 — 글로벌 instance 의 인터셉터를 거치지 않음(무한 루프 방지)
    refreshPromise = axios
      .post(`${BASE_URL}/auth/refresh`, null, { withCredentials: true })
      .finally(() => {
        // 다음 만료 시 새 promise 생성될 수 있도록 비움
        refreshPromise = null
      })
  }
  return refreshPromise
}

function redirectToLogin() {
  if (typeof window === 'undefined') return
  // 이미 로그인 페이지에 있으면 무한 루프 방지
  const path = window.location.pathname
  if (path === '/login' || path === '/' || path.startsWith('/shared/')) return
  window.location.href = '/login'
}

export function createApi(baseURL = BASE_URL) {
  const instance = axios.create({ baseURL, withCredentials: true })

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

      // 1) refresh 자체가 실패한 경우 — 무한 루프 방지
      if (original?.url?.endsWith('/auth/refresh')) {
        redirectToLogin()
        return Promise.reject(err.response?.data?.error ?? err)
      }

      // 2) 401 응답 — refresh 후 원래 요청 재시도 (한 번만)
      if (status === 401 && original && !original._retry) {
        original._retry = true
        try {
          await refreshTokens()
          // refresh 성공 시 새 csrf 토큰이 쿠키로 내려왔으므로 헤더 갱신
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
export function createPublicApi(baseURL = BASE_URL) {
  const instance = axios.create({ baseURL, withCredentials: true })
  instance.interceptors.response.use(
    (res) => res.data?.data,
    (err) => Promise.reject(err.response?.data?.error ?? err)
  )
  return instance
}
