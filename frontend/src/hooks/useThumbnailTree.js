import { useEffect, useRef, useState } from 'react'
import { getStepTreeBySequence } from '../api/step'

// 모듈 캐시: 같은 (projectId, sequence) 조합은 한 번만 호출.
// 카드 목록 ↔ 캔버스 진입을 오가도 1분간은 재사용한다.
const cache = new Map() // key -> { data, expires }
const TTL = 60_000

const makeKey = (projectId, sequence) => `${projectId}::${sequence}`

export function useThumbnailTree(projectId, stageSequence) {
  const ref = useRef(null)
  const [isVisible, setIsVisible] = useState(false)
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  // 카드가 뷰포트(또는 50px 미만)에 들어오면 활성화
  useEffect(() => {
    if (!ref.current || isVisible) return
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.disconnect()
        }
      },
      { rootMargin: '50px' }
    )
    observer.observe(ref.current)
    return () => observer.disconnect()
  }, [isVisible])

  // 페치
  useEffect(() => {
    if (!isVisible || !projectId || !stageSequence) return

    const key = makeKey(projectId, stageSequence)
    const cached = cache.get(key)
    if (cached && cached.expires > Date.now()) {
      setData(cached.data)
      return
    }

    let cancelled = false
    setIsLoading(true)
    getStepTreeBySequence(projectId, stageSequence)
      .then((res) => {
        if (cancelled) return
        cache.set(key, { data: res, expires: Date.now() + TTL })
        setData(res)
      })
      .catch(() => {
        if (!cancelled) setData(null)
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [isVisible, projectId, stageSequence])

  return { ref, data, isLoading }
}

// 외부에서 캐시 무효화가 필요할 때 사용 (예: 캔버스에서 변경 후 목록으로 복귀)
export function invalidateThumbnailCache(projectId) {
  if (!projectId) {
    cache.clear()
    return
  }
  for (const key of cache.keys()) {
    if (key.startsWith(`${projectId}::`)) cache.delete(key)
  }
}
