import { useEffect, useLayoutEffect, useRef, useState, useCallback } from 'react'
import styles from './OnboardingTour.module.css'

const PADDING = 8
const RADIUS = 12
const VIEWPORT_MARGIN = 16 /* 말풍선이 viewport 가장자리에 닿지 않게 두는 여백 */

/**
 * 온보딩 가이드 투어 컴포넌트.
 *
 * @param {Object[]} steps - 가이드 단계 목록
 * @param {string}   steps[].selector - 강조할 요소의 CSS selector (ID 또는 클래스)
 * @param {string}   steps[].title    - 말풍선 제목
 * @param {string}   steps[].body     - 말풍선 본문
 * @param {string=}  steps[].placement - 'top' | 'bottom' | 'left' | 'right' | 'auto' (기본 'auto')
 * @param {boolean}  open  - 투어 표시 여부
 * @param {Function} onClose - 종료/스킵 핸들러
 * @param {Function=} onComplete - 마지막 Next 클릭 시
 */
export default function OnboardingTour({ steps, open, onClose, onComplete }) {
  const [index, setIndex] = useState(0)
  const [rect, setRect] = useState(null)
  const [mounted, setMounted] = useState(false)
  const [tooltipSize, setTooltipSize] = useState({ width: 360, height: 180 })
  const tooltipRef = useRef(null)

  const current = steps?.[index]

  // 타겟 요소의 BoundingClientRect를 측정
  const measure = useCallback(() => {
    if (!current) return
    const el = document.querySelector(current.selector)
    if (!el) {
      // 타겟이 아직 마운트되지 않았으면 잠시 후 재시도
      setRect(null)
      return
    }
    const r = el.getBoundingClientRect()
    setRect({
      top: r.top - PADDING,
      left: r.left - PADDING,
      width: r.width + PADDING * 2,
      height: r.height + PADDING * 2,
    })
  }, [current])

  // open이 true가 된 직후 mount 애니메이션
  useEffect(() => {
    if (open) {
      setIndex(0)
      const t = setTimeout(() => setMounted(true), 16)
      return () => clearTimeout(t)
    }
    setMounted(false)
  }, [open])

  // 현재 step이 바뀔 때마다 위치 측정 + 리사이즈/스크롤 시 재측정
  useLayoutEffect(() => {
    if (!open) return
    measure()
    // 타겟이 늦게 마운트되는 경우를 대비해 짧은 폴링
    let tries = 0
    const polling = setInterval(() => {
      const el = document.querySelector(current?.selector ?? '')
      if (el) {
        measure()
        clearInterval(polling)
      } else if (++tries > 20) {
        clearInterval(polling)
      }
    }, 50)
    window.addEventListener('resize', measure)
    window.addEventListener('scroll', measure, true)
    return () => {
      clearInterval(polling)
      window.removeEventListener('resize', measure)
      window.removeEventListener('scroll', measure, true)
    }
  }, [open, index, current, measure])

  // 말풍선 실제 크기 측정 (viewport clamping 정확도 향상)
  useLayoutEffect(() => {
    if (!open || !tooltipRef.current) return
    const el = tooltipRef.current
    const update = () => {
      const r = el.getBoundingClientRect()
      setTooltipSize((prev) =>
        prev.width === r.width && prev.height === r.height
          ? prev
          : { width: r.width, height: r.height }
      )
    }
    update()
    const ro = new ResizeObserver(update)
    ro.observe(el)
    return () => ro.disconnect()
  }, [open, index])

  // ESC로 종료
  useEffect(() => {
    if (!open) return
    const onKey = (e) => {
      if (e.key === 'Escape') onClose?.()
      else if (e.key === 'ArrowRight') handleNext()
      else if (e.key === 'ArrowLeft') handlePrev()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, index, steps])

  function handleNext() {
    if (index < steps.length - 1) {
      setIndex((i) => i + 1)
    } else {
      onComplete?.()
      onClose?.()
    }
  }
  function handlePrev() {
    if (index > 0) setIndex((i) => i - 1)
  }

  if (!open || !current) return null

  // 말풍선 위치 계산 (placement 기반 + viewport clamping)
  const tooltip = computeTooltipPlacement(rect, current.placement, tooltipSize)

  return (
    <div className={`${styles.root} ${mounted ? styles.mounted : ''}`}>
      {/* SVG 마스크: 화면 전체 어둡게 + 타겟 영역만 잘라낸 구멍 */}
      <svg className={styles.overlay} width="100%" height="100%" onClick={onClose}>
        <defs>
          <mask id="poco-tour-mask">
            <rect width="100%" height="100%" fill="white" />
            {rect && (
              <rect
                className={styles.spotlight}
                x={rect.left}
                y={rect.top}
                width={rect.width}
                height={rect.height}
                rx={RADIUS}
                ry={RADIUS}
                fill="black"
              />
            )}
          </mask>
        </defs>
        <rect
          width="100%"
          height="100%"
          fill="rgba(15, 15, 30, 0.65)"
          mask="url(#poco-tour-mask)"
        />
      </svg>

      {/* 타겟 가장자리 강조 ring */}
      {rect && (
        <div
          className={styles.ring}
          style={{
            top: rect.top,
            left: rect.left,
            width: rect.width,
            height: rect.height,
          }}
        />
      )}

      {/* 말풍선 */}
      {rect && (
        <div
          ref={tooltipRef}
          key={index} /* 단계 변경 시 fade-in 재트리거 */
          className={styles.tooltip}
          style={{
            top: tooltip.top,
            left: tooltip.left,
            transform: tooltip.transform,
          }}
        >
          <div
            className={`${styles.arrow} ${styles[`arrow_${tooltip.arrow}`]}`}
            style={tooltip.arrowOffset ?? undefined}
          />
          <div className={styles.tooltipHeader}>
            <span className={styles.tooltipStep}>
              {index + 1} / {steps.length}
            </span>
            <button className={styles.skipBtn} onClick={onClose}>건너뛰기</button>
          </div>
          <h3 className={styles.tooltipTitle}>{current.title}</h3>
          <p className={styles.tooltipBody}>{current.body}</p>
          <div className={styles.tooltipActions}>
            <button
              className={styles.prevBtn}
              onClick={handlePrev}
              disabled={index === 0}
            >
              이전
            </button>
            <button className={styles.nextBtn} onClick={handleNext}>
              {index === steps.length - 1 ? '시작하기' : '다음'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// 타겟 영역과 placement에 따라 말풍선 위치 계산.
// 계산된 위치가 viewport 밖으로 벗어나면 안쪽으로 clamping하고,
// 화살표 위치도 그에 맞춰 보정한다.
function computeTooltipPlacement(rect, placement = 'auto', tooltipSize) {
  if (!rect) {
    return { top: 0, left: 0, transform: 'translate(0,0)', arrow: 'top' }
  }

  const TOOLTIP_GAP = 16
  const vw = window.innerWidth
  const vh = window.innerHeight
  const tw = tooltipSize?.width ?? 360
  const th = tooltipSize?.height ?? 180

  // auto일 때: 말풍선이 들어갈 공간이 가장 넉넉한 쪽 선택
  let placed = placement
  if (placed === 'auto') {
    const spaceTop = rect.top - VIEWPORT_MARGIN
    const spaceBottom = vh - (rect.top + rect.height) - VIEWPORT_MARGIN
    const spaceLeft = rect.left - VIEWPORT_MARGIN
    const spaceRight = vw - (rect.left + rect.width) - VIEWPORT_MARGIN
    // 수직 우선: 위/아래에 충분한 공간이 있으면 그쪽으로
    if (spaceBottom >= th + TOOLTIP_GAP) placed = 'bottom'
    else if (spaceTop >= th + TOOLTIP_GAP) placed = 'top'
    else if (spaceRight >= tw + TOOLTIP_GAP) placed = 'right'
    else if (spaceLeft >= tw + TOOLTIP_GAP) placed = 'left'
    else placed = 'bottom' /* fallback — clamping이 처리 */
  }

  // 1) 기준 위치 계산 (placement 기준 anchor 좌표)
  let top, left, transform, arrow
  switch (placed) {
    case 'top':
      top = rect.top - TOOLTIP_GAP
      left = rect.left + rect.width / 2
      transform = 'translate(-50%, -100%)'
      arrow = 'bottom'
      break
    case 'left':
      top = rect.top + rect.height / 2
      left = rect.left - TOOLTIP_GAP
      transform = 'translate(-100%, -50%)'
      arrow = 'right'
      break
    case 'right':
      top = rect.top + rect.height / 2
      left = rect.left + rect.width + TOOLTIP_GAP
      transform = 'translate(0, -50%)'
      arrow = 'left'
      break
    case 'bottom':
    default:
      top = rect.top + rect.height + TOOLTIP_GAP
      left = rect.left + rect.width / 2
      transform = 'translate(-50%, 0)'
      arrow = 'top'
      break
  }

  // 2) transform 결과 left/top → 실제 박스 left/top으로 변환
  // top/bottom: translateX(-50%) → 실제 left = left - tw/2
  // left:       translate(-100%, -50%) → 실제 left = left - tw, top = top - th/2
  // right:      translate(0, -50%)     → 실제 left = left,        top = top - th/2
  // top:        translate(-50%, -100%) → 실제 top = top - th
  let boxLeft, boxTop
  if (placed === 'top') {
    boxLeft = left - tw / 2
    boxTop = top - th
  } else if (placed === 'bottom') {
    boxLeft = left - tw / 2
    boxTop = top
  } else if (placed === 'left') {
    boxLeft = left - tw
    boxTop = top - th / 2
  } else {
    boxLeft = left
    boxTop = top - th / 2
  }

  // 3) viewport 안으로 clamp
  const minLeft = VIEWPORT_MARGIN
  const maxLeft = vw - tw - VIEWPORT_MARGIN
  const minTop = VIEWPORT_MARGIN
  const maxTop = vh - th - VIEWPORT_MARGIN
  const clampedLeft = Math.max(minLeft, Math.min(maxLeft, boxLeft))
  const clampedTop = Math.max(minTop, Math.min(maxTop, boxTop))

  // 4) 화살표가 타겟 중심을 가리키도록 offset 보정
  // 위/아래 화살표: 박스 내 left = (target center x) - clampedLeft
  // 좌/우 화살표:   박스 내 top  = (target center y) - clampedTop
  let arrowOffset = null
  if (arrow === 'top' || arrow === 'bottom') {
    const targetCenterX = rect.left + rect.width / 2
    const offsetX = Math.max(16, Math.min(tw - 16, targetCenterX - clampedLeft))
    arrowOffset = { left: `${offsetX}px`, transform: 'translateX(-50%)' }
  } else {
    const targetCenterY = rect.top + rect.height / 2
    const offsetY = Math.max(16, Math.min(th - 16, targetCenterY - clampedTop))
    arrowOffset = { top: `${offsetY}px`, transform: 'translateY(-50%)' }
  }

  return {
    top: clampedTop,
    left: clampedLeft,
    transform: 'none',
    arrow,
    arrowOffset,
  }
}
