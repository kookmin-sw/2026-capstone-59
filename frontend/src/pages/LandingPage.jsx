import { useEffect, useState, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { getMe, logout } from '../api/auth'
import styles from './LandingPage.module.css'

// ===== Design tokens =====
const tokens = {
  primary: '#7C5CFF',
  primaryHover: '#6A47FF',
  primarySoft: '#F4F1FF',
  primarySoftBorder: '#E2DBFF',
  bg: '#FAF8FF',
  bgGradient: 'radial-gradient(60% 60% at 50% 0%, #EEEAFF 0%, #FAF8FF 60%, #FFFFFF 100%)',
  ink: '#11121A',
  body: '#3C3C48',
  sub: '#7A7A88',
  border: '#ECECF2',
  hairline: '#F0EEF7',
  green: '#22A06B',
  greenSoft: '#E8F6EE',
  amber: '#F59E0B',
  amberSoft: '#FEF3C7',
}

const fontStack = "'Pretendard', 'Pretendard Variable', -apple-system, BlinkMacSystemFont, system-ui, sans-serif"
const monoStack = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace"

// ===== Hooks =====
function useInView(options = {}) {
  const ref = useRef(null)
  const [inView, setInView] = useState(false)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true)
          io.disconnect()
        }
      },
      { threshold: 0.15, rootMargin: '0px 0px -8% 0px', ...options }
    )
    io.observe(el)
    return () => io.disconnect()
  }, [])
  return [ref, inView]
}

// ===== Atoms =====
function Reveal({ children, delay = 0, y = 28, style = {} }) {
  const [ref, inView] = useInView()
  return (
    <div
      ref={ref}
      className={`${styles.reveal} ${inView ? styles.revealVisible : ''}`}
      style={{ transitionDelay: `${delay}s`, '--poco-reveal-y': `${y}px`, ...style }}
    >
      {children}
    </div>
  )
}

function Pill({ children, color = 'lavender' }) {
  const palettes = {
    lavender: { bg: tokens.primarySoft, fg: tokens.primary, dot: tokens.primary },
    green: { bg: tokens.greenSoft, fg: '#1E8A5A', dot: tokens.green },
    amber: { bg: tokens.amberSoft, fg: '#92400E', dot: tokens.amber },
  }
  const p = palettes[color] ?? palettes.lavender
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 7,
      padding: '5px 12px', background: p.bg, color: p.fg,
      fontSize: 12, fontWeight: 600, borderRadius: 99,
      letterSpacing: '-0.01em', whiteSpace: 'nowrap', fontFamily: fontStack,
    }}>
      <span style={{ width: 6, height: 6, borderRadius: 99, background: p.dot }} />
      {children}
    </span>
  )
}

function PrimaryCTA({ children, size = 'md', onClick, glow = false }) {
  const sizes = {
    sm: { h: 40, px: 18, fs: 13.5 },
    md: { h: 48, px: 22, fs: 14.5 },
    lg: { h: 56, px: 28, fs: 16 },
  }
  const s = sizes[size]
  return (
    <button
      onClick={onClick}
      className={glow ? styles.ctaGlow : ''}
      style={{
        height: s.h, padding: `0 ${s.px}px`,
        background: tokens.primary, color: '#fff',
        border: 'none', borderRadius: 99,
        fontSize: s.fs, fontWeight: 600, letterSpacing: '-0.01em',
        cursor: 'pointer', fontFamily: fontStack, whiteSpace: 'nowrap',
        boxShadow: '0 1px 2px rgba(124,92,255,0.3), 0 8px 24px -8px rgba(124,92,255,0.45), inset 0 -1px 0 rgba(0,0,0,0.06)',
      }}
    >
      {children}
    </button>
  )
}

function GhostCTA({ children, size = 'md', onClick }) {
  const sizes = {
    sm: { h: 40, px: 16, fs: 13.5 },
    md: { h: 48, px: 20, fs: 14.5 },
    lg: { h: 56, px: 24, fs: 16 },
  }
  const s = sizes[size]
  return (
    <button
      onClick={onClick}
      style={{
        height: s.h, padding: `0 ${s.px}px`,
        background: 'transparent', color: tokens.ink,
        border: `1px solid ${tokens.border}`, borderRadius: 99,
        fontSize: s.fs, fontWeight: 500, cursor: 'pointer',
        fontFamily: fontStack, whiteSpace: 'nowrap',
        display: 'inline-flex', alignItems: 'center', gap: 8,
      }}
    >
      {children}
    </button>
  )
}

function Eyebrow({ children, align = 'left' }) {
  return (
    <div style={{
      fontSize: 12.5, color: tokens.primary, fontWeight: 600,
      letterSpacing: '0.12em', textTransform: 'uppercase',
      fontFamily: monoStack, textAlign: align,
    }}>
      {children}
    </div>
  )
}

// 고양이 발바닥 (사용자 제공 아트워크)
function CatPawIcon({ size = 64 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 324 335" fill="none" xmlns="http://www.w3.org/2000/svg">
      <g opacity="0.7">
        <path d="M64.7098 179.37C82.0026 194.181 84.9275 219.141 71.2427 235.118C57.5579 251.095 32.4456 252.041 15.1528 237.229C-2.14002 222.418 -5.06493 197.458 8.61984 181.481C22.3046 165.504 47.4169 164.558 64.7098 179.37Z" fill="#4A35D0" fillOpacity="0.18"/>
        <path d="M247.402 95.4747C247.366 118.243 264.392 136.728 285.428 136.76C306.465 136.793 323.548 118.362 323.583 95.593C323.618 72.8242 306.593 54.3399 285.556 54.3072C264.52 54.2746 247.437 72.7059 247.402 95.4747Z" fill="#4A35D0" fillOpacity="0.18"/>
        <path d="M132.871 63.9595C139.997 92.0618 166.485 109.592 192.034 103.114C217.583 96.6355 232.518 68.6025 225.393 40.5002C218.267 12.3979 191.779 -5.132 166.23 1.3461C140.681 7.8242 125.746 35.8572 132.871 63.9595Z" fill="#4A35D0" fillOpacity="0.18"/>
        <path d="M114.89 71.9734C131.562 95.692 127.596 127.207 106.032 142.364C84.4687 157.52 53.473 150.58 36.8014 126.861C20.1299 103.143 24.0958 71.6278 45.6595 56.4709C67.2231 41.3141 98.2189 48.2548 114.89 71.9734Z" fill="#4A35D0" fillOpacity="0.18"/>
        <path d="M313.351 254.801C291.948 299.012 250.039 278.463 225.851 289.57C201.663 300.678 191.877 345.921 140.176 331.779C66.1967 302.399 95.4947 171.393 158.222 142.587C220.95 113.782 340.998 178.434 313.351 254.801Z" fill="#4A35D0" fillOpacity="0.18"/>
      </g>
    </svg>
  )
}

// 발자국이 왼쪽 → 오른쪽으로 순차적으로 탁탁탁 찍히는 trail 애니메이션
function FloatingDots() {
  // 두 줄(상단·하단)로 발자국 trail 배치. 같은 줄 안에서 좌우발이 살짝 엇갈리며 진행.
  // x: 가로 위치(%), y: 세로 위치(%), tilt: 발 회전(좌발은 음수, 우발은 양수), s: 크기(px), d: 시작 지연(s)
  const TOTAL = 6 /* 한 사이클 전체 시간(s). 한 줄에 8개 발자국이 있을 때 마지막 발자국은 약 5.6s 지연 */
  const STAGGER = 0.7 /* 발자국 사이 간격(s) */
  const STEPS_PER_ROW = 8

  function buildRow(yPercent, baseTilt, hueShift = 0) {
    return Array.from({ length: STEPS_PER_ROW }).map((_, i) => {
      const isLeftFoot = i % 2 === 0
      const x = 4 + i * (92 / (STEPS_PER_ROW - 1)) /* 좌측 4% → 우측 96% 까지 */
      const yOffset = isLeftFoot ? -3 : 3 /* 좌우발 살짝 엇갈리게 */
      // 진행 방향(우측)을 기준으로 좌발은 약간 왼쪽으로, 우발은 오른쪽으로 기울임
      const tilt = baseTilt + (isLeftFoot ? -10 : 10)
      return {
        x,
        y: yPercent + yOffset,
        s: 56 + (i % 3) * 6, /* 56 / 62 / 68 px 약간 변주 */
        tilt,
        delay: i * STAGGER,
        hueShift,
      }
    })
  }

  const rowTop = buildRow(28, -2)
  const rowBottom = buildRow(76, 4)
  const all = [...rowTop, ...rowBottom]

  return (
    <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', overflow: 'hidden' }}>
      {all.map((p, i) => (
        <span
          key={i}
          style={{
            position: 'absolute',
            left: `${p.x}%`,
            top: `${p.y}%`,
            transform: 'translate(-50%, -50%)',
            pointerEvents: 'none',
            opacity: 0,
            animation: `pocoPawStamp ${TOTAL}s ease-out ${p.delay}s infinite`,
          }}
        >
          <span style={{ display: 'inline-block', transform: `rotate(${p.tilt}deg)` }}>
            <CatPawIcon size={p.s} />
          </span>
        </span>
      ))}
    </div>
  )
}

function InlineTree({ width = 240, height = 90 }) {
  const nodes = [
    { x: 30, y: 100 }, { x: 110, y: 60 }, { x: 110, y: 140 },
    { x: 200, y: 30, required: true }, { x: 200, y: 90 }, { x: 200, y: 170 },
    { x: 290, y: 60 }, { x: 290, y: 130 },
  ]
  const edges = [[0,1],[0,2],[1,3],[1,4],[2,5],[4,6],[5,7]]
  const accentNode = 2
  return (
    <svg width={width} height={height} viewBox="0 0 320 200" fill="none">
      {edges.map(([a, b], i) => (
        <path key={i}
          d={`M${nodes[a].x} ${nodes[a].y} C${(nodes[a].x + nodes[b].x) / 2} ${nodes[a].y}, ${(nodes[a].x + nodes[b].x) / 2} ${nodes[b].y}, ${nodes[b].x} ${nodes[b].y}`}
          stroke="#D7CCFF" strokeWidth="1.5" strokeLinecap="round" />
      ))}
      {nodes.map((n, i) =>
        n.required ? (
          <g key={i} transform={`translate(${n.x} ${n.y}) rotate(45)`}>
            <rect x={-10} y={-10} width={20} height={20} rx={3} fill="#7C5CFF" stroke="#fff" strokeWidth="3" />
          </g>
        ) : (
          <g key={i}>
            {i === accentNode && (
              <circle cx={n.x} cy={n.y} r={13} fill="#7C5CFF"
                style={{ transformOrigin: `${n.x}px ${n.y}px`, animation: 'pocoPulse 2.4s ease-out infinite' }} />
            )}
            <circle cx={n.x} cy={n.y} r={i === accentNode ? 13 : 10}
              fill={i === accentNode ? '#7C5CFF' : '#fff'}
              stroke={i === accentNode ? '#fff' : '#C7BBFF'}
              strokeWidth={i === accentNode ? 3 : 2} />
          </g>
        )
      )}
    </svg>
  )
}

function StageStrip() {
  const stages = [
    { n: '01', ko: '아이디어 구체화', en: 'Ideation' },
    { n: '02', ko: '프로젝트 계획', en: 'Planning' },
    { n: '03', ko: '요구사항 정의', en: 'Requirement' },
    { n: '04', ko: '설계', en: 'Design' },
    { n: '05', ko: '개발', en: 'Development' },
    { n: '06', ko: '테스트 및 검증', en: 'Test' },
  ]
  const [ref, inView] = useInView({ threshold: 0.25 })
  return (
    <div ref={ref} style={{ position: 'relative', padding: '0 20px' }}>
      <svg style={{ position: 'absolute', left: 50, right: 50, top: 30, width: 'calc(100% - 100px)', height: 2, pointerEvents: 'none' }}
        viewBox="0 0 1000 2" preserveAspectRatio="none">
        <line x1="0" y1="1" x2="1000" y2="1"
          stroke={tokens.primarySoftBorder} strokeWidth="2" strokeDasharray="6 6"
          style={{ strokeDasharray: '1000 1000', strokeDashoffset: inView ? 0 : 1000, transition: 'stroke-dashoffset 1.8s ease-out 0.3s' }} />
      </svg>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 16, position: 'relative' }}>
        {stages.map((s, i) => (
          <div key={s.n} style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center',
            opacity: inView ? 1 : 0,
            transform: inView ? 'translateY(0)' : 'translateY(16px)',
            transition: `opacity 0.6s ease ${0.5 + i * 0.12}s, transform 0.6s ease ${0.5 + i * 0.12}s`,
          }}>
            <div className={styles.stageNumber} style={{
              width: 60, height: 60, borderRadius: 99,
              background: '#fff', border: `2px solid ${tokens.primarySoftBorder}`,
              color: tokens.primary, display: 'grid', placeItems: 'center',
              fontFamily: monoStack, fontSize: 14, fontWeight: 700,
              boxShadow: '0 2px 4px rgba(20,18,40,0.04)',
            }}>{s.n}</div>
            <div style={{ fontSize: 14, fontWeight: 600, marginTop: 14, color: tokens.ink, letterSpacing: '-0.01em', whiteSpace: 'nowrap' }}>{s.ko}</div>
            <div style={{ fontSize: 11, color: tokens.sub, marginTop: 4, fontFamily: monoStack, letterSpacing: '0.04em' }}>{s.en}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ===== Section icon helpers =====
function SourceCard({ title, badge, year, subtitle, publisher, description, tag, href }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className={styles.sourceCard}
      style={{
        position: 'relative',
        display: 'flex', flexDirection: 'column',
        padding: 28,
        background: 'linear-gradient(180deg, rgba(38, 33, 70, 0.7) 0%, rgba(28, 24, 55, 0.7) 100%)',
        border: '1px solid rgba(124, 92, 255, 0.18)',
        borderRadius: 18,
        textDecoration: 'none',
        color: '#fff',
        height: '100%',
        boxSizing: 'border-box',
        overflow: 'hidden',
        transition: 'transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease',
      }}
    >
      {/* 우측 상단 연도 */}
      <span style={{
        position: 'absolute', top: 22, right: 24,
        fontSize: 12, color: '#5C5680',
        fontFamily: monoStack, letterSpacing: '0.06em',
      }}>
        {year}
      </span>

      {/* 타이틀 + 배지 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
        <span style={{
          fontSize: 24, fontWeight: 800, letterSpacing: '-0.02em', color: '#fff',
        }}>
          {title}
        </span>
        <span style={{
          padding: '3px 9px',
          background: 'rgba(124, 92, 255, 0.22)',
          color: '#C5B4FF',
          fontSize: 12, fontWeight: 600, letterSpacing: '0.02em',
          borderRadius: 6,
          fontFamily: monoStack,
        }}>
          {badge}
        </span>
      </div>

      {/* 영문 부제 */}
      <div style={{
        fontSize: 13.5, color: '#9890BC', marginTop: 8,
        fontStyle: 'italic', letterSpacing: '-0.005em',
      }}>
        {subtitle}
      </div>

      {/* 발행기관 칩 */}
      <span style={{
        display: 'inline-flex', alignItems: 'center', gap: 8,
        marginTop: 18, padding: '6px 12px',
        background: 'rgba(255, 255, 255, 0.04)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        borderRadius: 8,
        fontSize: 12.5, color: '#C8C4DC', fontWeight: 500,
        alignSelf: 'flex-start',
      }}>
        <span style={{
          width: 6, height: 6, borderRadius: 99,
          background: '#22A06B', display: 'inline-block',
        }} />
        {publisher}
      </span>

      {/* 본문 */}
      <p style={{
        fontSize: 14, color: '#C8C4DC', marginTop: 20,
        lineHeight: 1.75, letterSpacing: '-0.005em', flex: 1,
      }}>
        {description}
      </p>

      {/* 하단: 키워드 + 원문 확인 */}
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        marginTop: 24, paddingTop: 20,
        borderTop: '1px solid rgba(255, 255, 255, 0.06)',
      }}>
        <span style={{
          fontSize: 13, color: '#9D87FF', fontWeight: 700, letterSpacing: '-0.005em',
        }}>
          {tag}
        </span>
        <span style={{
          fontSize: 12.5, color: '#9890BC', fontWeight: 500, letterSpacing: '-0.005em',
          display: 'inline-flex', alignItems: 'center', gap: 4,
        }}>
          원문 확인 <span style={{ fontSize: 11 }}>↗</span>
        </span>
      </div>
    </a>
  )
}

// ===== Section icon helpers =====
function FeatureIcon({ kind }) {
  if (kind === 'tree') return <InlineTree width={240} height={90} />
  if (kind === 'compass') return (
    <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
      <circle cx="32" cy="32" r="22" stroke="#7C5CFF" strokeWidth="2" />
      <circle cx="32" cy="32" r="4" fill="#7C5CFF" />
      <path d="M32 14 L32 22 M32 42 L32 50 M14 32 L22 32 M42 32 L50 32" stroke="#C7BBFF" strokeWidth="2" strokeLinecap="round" />
      <path d="M28 28 L36 36 M36 28 L28 36" stroke="#7C5CFF" strokeWidth="1.5" strokeLinecap="round" opacity="0.4" />
    </svg>
  )
  if (kind === 'book') return (
    <svg width="80" height="64" viewBox="0 0 80 64" fill="none">
      <rect x="10" y="14" width="28" height="36" rx="3" fill="#fff" stroke="#7C5CFF" strokeWidth="2" />
      <rect x="42" y="14" width="28" height="36" rx="3" fill="#F4F1FF" stroke="#7C5CFF" strokeWidth="2" />
      <path d="M16 22 L32 22 M16 28 L32 28 M16 34 L26 34" stroke="#C7BBFF" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M48 22 L64 22 M48 28 L64 28 M48 34 L58 34" stroke="#7C5CFF" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  )
  return null
}

// 비교 표 셀의 상태 마크 — yes(체크) / mid(부분) / no(엑스)
function CompareMark({ kind }) {
  const map = {
    yes: { color: tokens.primary, bg: tokens.primarySoft,
      icon: <path d="M4 8.5L7 11.5L12 5.5" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" /> },
    mid: { color: '#D97706', bg: tokens.amberSoft,
      icon: <path d="M3 8H13" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" /> },
    no:  { color: '#9CA3AF', bg: '#F3F4F6',
      icon: <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" /> },
  }
  const m = map[kind] ?? map.no
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
      width: 26, height: 26, borderRadius: 999,
      background: m.bg, color: m.color,
    }}>
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">{m.icon}</svg>
    </span>
  )
}

function PersonaIcon({ kind }) {
  const stroke = tokens.primary
  if (kind === 'student') return (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
      <path d="M22 10v6M2 10l10-5 10 5-10 5z" stroke={stroke} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M6 12v5c3 3 9 3 12 0v-5" stroke={stroke} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
  if (kind === 'dev') return (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
      <polyline points="16 18 22 12 16 6" stroke={stroke} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
      <polyline points="8 6 2 12 8 18" stroke={stroke} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
  if (kind === 'pm') return (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
      <path d="M9 11l3 3L22 4" stroke={stroke} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" stroke={stroke} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
  if (kind === 'team') return (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke={stroke} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
      <circle cx="9" cy="7" r="4" stroke={stroke} strokeWidth="1.6"/>
      <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" stroke={stroke} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
  return null
}

// ===== Data =====
const FEATURES = [
  { n: '01', title: 'AI 기반 Step Flow 생성', en: 'Step Flow',
    body: '아이디어만 입력하면, AI가 다음 단계를 3가지 방향으로 제안합니다. 검증된 6단계 프로세스 위에서 캔버스가 자랍니다.',
    quote: '막연함을 "다음 한 걸음"으로', icon: 'compass' },
  { n: '02', title: '분기점 롤백 & 재탐색', en: 'Branching',
    body: '잘못된 방향이라면 되돌아가서 다른 가지를 탐색하세요. 기록은 남고, 모든 결정은 자산으로 보존됩니다.',
    quote: '되돌아갈 수 있는 선택', icon: 'tree', highlight: true },
  { n: '03', title: 'Step별 클릭 어시스턴트', en: 'Side Panel Guide',
    body: '노드를 클릭하면 멘토링·용어사전·노션 템플릿이 펼쳐집니다. 딱딱한 방법론 문서 대신 맥락에 맞는 가이드.',
    quote: '곁에 있는 시니어 멘토', icon: 'book' },
]

const PERSONAS = [
  { kind: 'student', title: '캡스톤을 준비 중인 대학생',
    body: '첫 팀 프로젝트, 어디서부터 시작해야 할지 몰라 막막한 당신' },
  { kind: 'dev', title: '사이드 프로젝트를 구상 중인 개발자',
    body: '아이디어는 넘치는데, 체계적으로 정리하고 싶은 당신' },
  { kind: 'pm', title: '신규 서비스를 기획 중인 PM',
    body: '검증된 프레임워크 위에서 빠르게 구조를 잡고 싶은 당신' },
  { kind: 'team', title: '팀과 의사결정을 공유하고 싶은 리더',
    body: '"왜 이 결정을 했는지" 팀원에게 명확히 보여주고 싶은 당신' },
]

const GALLERY_ROW_1 = [
  '배달 라이더 경로 앱', '캠퍼스 중고거래 플랫폼', '반려동물 건강 관리 앱',
  '음악 추천 큐레이션 앱', 'AI 면접 코칭 서비스', '도시농부 커뮤니티',
  '취준 스터디 매칭', '여행 일정 자동 정리',
]
const GALLERY_ROW_2 = [
  '소셜 독서 커뮤니티', '스마트팜 모니터링 대시보드', '실시간 협업 화이트보드',
  '러닝 크루 기록 SNS', '집안일 분담 가족 앱', '동아리 운영 자동화',
  '학생 동선 안전 알림', '취미 클래스 큐레이션',
]

// 마퀴 한 줄 — 같은 콘텐츠를 두 번 이어붙여 seamless loop 구현
function MarqueeRow({ items, direction = 'left', duration = 38 }) {
  // 2배만 이어붙이면 칩 폭이 좁아 -50% 이동 거리가 짧고 결과적으로 시각적 속도가 느려 정적으로 보일 수 있다.
  // 칩 갯수가 적을수록 4배로 늘려 한 cycle 이동 거리를 늘린다.
  const repeat = items.length < 10 ? 4 : 2
  const doubled = Array.from({ length: repeat }, () => items).flat()
  const animName = direction === 'left' ? 'pocoMarqueeLeft' : 'pocoMarqueeRight'
  // repeat=4면 -25%만 이동해도 한 사이클이 완성되도록 keyframes도 분기
  const animSuffix = repeat === 4 ? '4x' : ''
  return (
    <div className={styles.marqueeRow}>
      <div
        className={styles.marqueeTrack}
        style={{ animation: `${animName}${animSuffix} ${duration}s linear infinite` }}
      >
        {doubled.map((name, i) => (
          <span key={`${name}-${i}`} className={styles.galleryChip} style={{
            padding: '12px 22px', background: '#FBFAFF',
            border: `1px solid ${tokens.primarySoftBorder}`, borderRadius: 99,
            fontSize: 14, fontWeight: 500, color: tokens.ink, letterSpacing: '-0.01em',
            display: 'inline-flex', alignItems: 'center', gap: 8,
            whiteSpace: 'nowrap', flexShrink: 0,
          }}>
            <span style={{ width: 6, height: 6, borderRadius: 99, background: tokens.primary, flexShrink: 0 }} />
            {name}
          </span>
        ))}
      </div>
    </div>
  )
}

// ===== Main page =====
export default function LandingPage() {
  const navigate = useNavigate()
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  useEffect(() => {
    getMe().then(() => setIsLoggedIn(true)).catch(() => setIsLoggedIn(false))
  }, [])

  const handleStart = useCallback(() => {
    navigate(isLoggedIn ? '/projects' : '/login')
  }, [isLoggedIn, navigate])

  const handleLogout = useCallback(async () => {
    try { await logout() } catch { /* ignore */ }
    setIsLoggedIn(false)
  }, [])

  const handleGitHub = useCallback(() => {
    window.open('https://github.com/kookmin-sw/2026-capstone-59', '_blank', 'noopener')
  }, [])

  // Smooth section-by-section scrolling
  useEffect(() => {
    const sections = [...document.querySelectorAll(`.${styles.snapSection}`)]
    if (!sections.length) return

    let currentIdx = 0
    let isAnimating = false
    let lastWheelAt = 0
    const DURATION = 665

    const easeInOutCubic = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2)

    function animateTo(targetY) {
      const startY = window.scrollY
      const distance = targetY - startY
      if (Math.abs(distance) < 1) { isAnimating = false; return }
      isAnimating = true
      const startTime = performance.now()
      function step(now) {
        const t = Math.min((now - startTime) / DURATION, 1)
        window.scrollTo(0, startY + distance * easeInOutCubic(t))
        if (t < 1) requestAnimationFrame(step)
        else isAnimating = false
      }
      requestAnimationFrame(step)
    }

    function goTo(idx) {
      idx = Math.max(0, Math.min(sections.length - 1, idx))
      if (isAnimating || idx === currentIdx) return
      currentIdx = idx
      const rect = sections[idx].getBoundingClientRect()
      animateTo(window.scrollY + rect.top)
    }

    function syncIdx() {
      let best = 0, bestDist = Infinity
      sections.forEach((s, i) => {
        const r = s.getBoundingClientRect()
        const dist = Math.abs(r.top)
        if (dist < bestDist) { bestDist = dist; best = i }
      })
      currentIdx = best
    }
    syncIdx()

    function onWheel(e) {
      if (isAnimating) { e.preventDefault(); return }
      if (Math.abs(e.deltaY) < 4) return
      const now = performance.now()
      if (now - lastWheelAt < 80) { e.preventDefault(); return }
      lastWheelAt = now
      e.preventDefault()
      goTo(currentIdx + (e.deltaY > 0 ? 1 : -1))
    }
    function onKey(e) {
      const navKeys = ['ArrowDown', 'ArrowUp', 'PageDown', 'PageUp', ' ', 'Home', 'End']
      if (!navKeys.includes(e.key)) return
      const tag = document.activeElement?.tagName ?? ''
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(tag)) return
      e.preventDefault()
      if (isAnimating) return
      if (e.key === 'Home') goTo(0)
      else if (e.key === 'End') goTo(sections.length - 1)
      else if (e.key === 'ArrowUp' || e.key === 'PageUp') goTo(currentIdx - 1)
      else goTo(currentIdx + 1)
    }
    let touchStartY = 0, touchDelta = 0
    function onTouchStart(e) { touchStartY = e.touches[0].clientY; touchDelta = 0 }
    function onTouchMove(e) {
      if (isAnimating) { e.preventDefault(); return }
      touchDelta = touchStartY - e.touches[0].clientY
    }
    function onTouchEnd() {
      if (isAnimating) return
      if (Math.abs(touchDelta) > 40) goTo(currentIdx + (touchDelta > 0 ? 1 : -1))
    }
    function onAnchorClick(e) {
      const a = e.target.closest('a[href^="#"]')
      if (!a) return
      const id = a.getAttribute('href').slice(1)
      if (!id) return
      const target = sections.find((s) => s.id === id)
      if (target) { e.preventDefault(); goTo(sections.indexOf(target)) }
    }

    window.addEventListener('wheel', onWheel, { passive: false })
    window.addEventListener('keydown', onKey)
    window.addEventListener('touchstart', onTouchStart, { passive: true })
    window.addEventListener('touchmove', onTouchMove, { passive: false })
    window.addEventListener('touchend', onTouchEnd)
    document.addEventListener('click', onAnchorClick)
    return () => {
      window.removeEventListener('wheel', onWheel)
      window.removeEventListener('keydown', onKey)
      window.removeEventListener('touchstart', onTouchStart)
      window.removeEventListener('touchmove', onTouchMove)
      window.removeEventListener('touchend', onTouchEnd)
      document.removeEventListener('click', onAnchorClick)
    }
  }, [])

  return (
    <div style={{ width: '100%', background: tokens.bg, fontFamily: fontStack, color: tokens.ink }}>
      {/* ===== Sticky Nav ===== */}
      <div className={styles.navSticky}>
        <header style={{
          width: '100%', padding: '20px 56px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          background: 'transparent', boxSizing: 'border-box',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <img src="/poco-logo-text.svg" alt="poco" height={28} />
          </div>
          <nav style={{ display: 'flex', alignItems: 'center', gap: 32 }}>
            <a href="#features" style={navLinkStyle}>기능</a>
            <a href="#personas" style={navLinkStyle}>누구를 위한가</a>
            <a href="https://github.com/kookmin-sw/2026-capstone-59" target="_blank" rel="noopener noreferrer" style={navLinkStyle}>GitHub</a>
            {isLoggedIn ? <GhostCTA size="sm" onClick={handleLogout}>로그아웃</GhostCTA> : null}
            <PrimaryCTA size="sm" onClick={handleStart}>Get started!</PrimaryCTA>
          </nav>
        </header>
      </div>

      {/* ===== 1. HERO ===== */}
      {/* justify-content: center 대신 flex-start + padding-top 으로 nav 와의 클립 방지 */}
      <section className={`${styles.snapSection} ${styles.heroSection}`} style={{ textAlign: 'center', background: tokens.bgGradient, overflow: 'hidden' }}>
        <FloatingDots />
        <div style={{ position: 'relative', maxWidth: 880, margin: '0 auto' }}>
          <div className={styles.fadeUp} style={{ animationDelay: '0.05s' }}>
            <Eyebrow align="center">Your AI Development Partner</Eyebrow>
          </div>

          <div className={styles.fadeScale} style={{ display: 'flex', justifyContent: 'center', margin: '24px 0 8px', animationDelay: '0.18s' }}>
            <img src="/poco-logo-text.svg" alt="poco" style={{ height: 220, width: 'auto' }} />
          </div>

          <h1 className={styles.fadeUp} style={{
            fontSize: 52, lineHeight: 1.18, letterSpacing: '-0.035em', fontWeight: 700,
            margin: '16px 0 18px', color: tokens.ink, animationDelay: '0.35s',
          }}>
            당신의 생각이 <span style={{ color: tokens.primary }}>트리</span>로 자라납니다
          </h1>

          <p className={styles.fadeUp} style={{
            fontSize: 18, lineHeight: 1.6, color: tokens.sub, maxWidth: 620,
            margin: '0 auto 36px', letterSpacing: '-0.01em', animationDelay: '0.5s',
          }}>
            AI가 다 만들어주는 시대, <b style={{ color: tokens.ink, fontWeight: 600 }}>무엇을·왜 만들지</b> 정의하고 계신가요?<br />
            Poco가 다음 한 걸음의 선택지를 제시하고, 의사결정의 궤적을 트리로 시각화해드립니다.
          </p>

          <div className={styles.fadeUp} style={{ display: 'flex', gap: 12, justifyContent: 'center', alignItems: 'center', animationDelay: '0.65s' }}>
            <PrimaryCTA size="lg" onClick={handleStart} glow>무료로 시작하기 →</PrimaryCTA>
            <GhostCTA size="lg" onClick={handleGitHub}>
              View on GitHub <span style={{ color: tokens.sub }}>↗</span>
            </GhostCTA>
          </div>

          <div className={styles.fadeIn} style={{
            marginTop: 40, display: 'inline-flex', gap: 14, alignItems: 'center',
            color: tokens.sub, fontSize: 13, fontFamily: monoStack, whiteSpace: 'nowrap',
            animationDelay: '0.85s',
          }}>
            <span style={{ display: 'inline-block', width: 28, height: 1, background: tokens.border }} />
            DOJ SDLC · SWEBOK V4.0a 기반
            <span style={{ display: 'inline-block', width: 28, height: 1, background: tokens.border }} />
          </div>
        </div>

        <div className={styles.fadeIn} style={{
          marginTop: 48, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10,
          color: tokens.sub, fontSize: 11, fontFamily: monoStack, letterSpacing: '0.16em',
          textTransform: 'uppercase', animationDelay: '1.1s',
        }}>
          한 걸음 더 내려가 보세요
          <span style={{ width: 1, height: 32,
            background: `linear-gradient(to bottom, ${tokens.primarySoftBorder}, transparent)`,
            animation: 'pocoFloat 2.4s ease-in-out infinite' }} />
        </div>
      </section>

      {/* ===== 2. 이런 경험, 있지 않나요? ===== */}
      <section className={styles.snapSection} style={{ background: '#fff', padding: '80px 56px' }}>
        <div style={{ maxWidth: 1080, margin: '0 auto', width: '100%' }}>
          <Reveal>
            <div style={{ textAlign: 'center', marginBottom: 56 }}>
              <Eyebrow align="center">Sound Familiar?</Eyebrow>
              <h2 style={{ fontSize: 38, fontWeight: 700, letterSpacing: '-0.03em', margin: '16px 0 10px' }}>
                이런 경험, 있지 않나요?
              </h2>
              <p style={{ fontSize: 15, color: tokens.sub, margin: 0, lineHeight: 1.65 }}>
                AI 챗봇은 분명 똑똑한데, 막상 프로젝트를 만들려고 하면 어딘가 답답하죠.
              </p>
            </div>
          </Reveal>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
            {[
              { tag: '챗봇과의 대화', user: '아 잠깐, 아까 말한 기술 스택은 뭐였지?', ai: '이전 대화에서 기술 스택에 대해 말씀하신 적이 없는 것 같습니다. 다시 알려주시겠어요?', label: '대화는 흘러갑니다' },
              { tag: '팀 회의 직전', user: '팀원한테 설명해야 하는데… 왜 이 결정 했더라?', ai: '대화 로그를 다시 읽어보세요. 길죠?', label: '근거는 흩어집니다' },
              { tag: '아이디어 정리', user: '아이디어는 있는데 어디부터 손대지?', ai: '좋은 아이디어네요! 먼저 요구사항을 정리해볼까요? (그래서 뭘 묻지...)', label: '시작점이 흐립니다' },
            ].map((c, i) => (
              <Reveal key={i} delay={i * 0.1} y={32}>
                <div className={styles.card} style={{
                  padding: 24, background: '#FAFAFD',
                  border: `1px solid ${tokens.border}`, borderRadius: 18,
                  display: 'flex', flexDirection: 'column', gap: 14, height: '100%',
                }}>
                  <div style={{ fontSize: 11, color: tokens.sub, fontFamily: monoStack, letterSpacing: '0.08em' }}>{c.tag}</div>

                  <div style={{
                    alignSelf: 'flex-end', maxWidth: '85%', padding: '10px 14px',
                    background: tokens.primary, color: '#fff', fontSize: 13.5, lineHeight: 1.55,
                    borderRadius: '14px 14px 4px 14px', letterSpacing: '-0.01em',
                  }}>{c.user}</div>

                  <div style={{
                    alignSelf: 'flex-start', maxWidth: '85%', padding: '10px 14px',
                    background: '#fff', color: tokens.body, fontSize: 13, lineHeight: 1.55,
                    borderRadius: '14px 14px 14px 4px', border: `1px solid ${tokens.border}`,
                    letterSpacing: '-0.01em',
                  }}>{c.ai}</div>

                  <div style={{
                    marginTop: 'auto', paddingTop: 12, fontSize: 12, color: tokens.primary,
                    fontWeight: 600, fontFamily: monoStack, letterSpacing: '-0.005em',
                  }}>↳ {c.label}</div>
                </div>
              </Reveal>
            ))}
          </div>

          <Reveal delay={0.3}>
            <p style={{
              textAlign: 'center', marginTop: 48, fontSize: 17, lineHeight: 1.65,
              color: tokens.ink, letterSpacing: '-0.01em',
            }}>
              <span style={{ color: tokens.primary, fontWeight: 700 }}>여기서 Poco가 시작됩니다.</span>
            </p>
          </Reveal>
        </div>
      </section>

      {/* ===== 3. 4-way 비교 표 (Jira/Notion · 챗봇 · 방법론 문서 · Poco) ===== */}
      <section className={styles.snapSection} style={{ background: tokens.bg, padding: '80px 56px' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto', width: '100%' }}>
          <Reveal>
            <div style={{ textAlign: 'center', marginBottom: 48 }}>
              <Eyebrow align="center">What's Different</Eyebrow>
              <h2 style={{ fontSize: 38, fontWeight: 700, letterSpacing: '-0.03em', margin: '16px 0 10px' }}>
                무엇이 다른가요?
              </h2>
              <p style={{ fontSize: 15, color: tokens.sub, margin: 0, lineHeight: 1.65 }}>
                다른 도구·자료에도 장점이 있지만, Poco만 줄 수 있는 가치가 있어요.
              </p>
            </div>
          </Reveal>

          <Reveal delay={0.1}>
            <div className={styles.comparisonTable}>
              <table>
                <thead>
                  <tr>
                    <th scope="col" className={styles.tableLabelCol}></th>
                    <th scope="col">Jira / Notion</th>
                    <th scope="col">일반 챗봇</th>
                    <th scope="col">방법론 문서<br /><span className={styles.colSub}>SWEBOK · PMBOK</span></th>
                    <th scope="col" className={styles.pocoCol}>Poco</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { label: '다음 할 일 제시',
                      cells: [
                        { mark: 'no', text: '직접 작성·관리' },
                        { mark: 'mid', text: '질문 능력 필요' },
                        { mark: 'no', text: '사용자가 해석' },
                        { mark: 'yes', text: 'AI가 자동 제시' },
                      ] },
                    { label: '의사결정 보존',
                      cells: [
                        { mark: 'mid', text: '텍스트 산재' },
                        { mark: 'no', text: '대화는 흘러감' },
                        { mark: 'no', text: '별도 기록 필요' },
                        { mark: 'yes', text: '트리로 시각화' },
                      ] },
                    { label: '방법론 근거',
                      cells: [
                        { mark: 'no', text: '없음' },
                        { mark: 'no', text: '답이 흔들림' },
                        { mark: 'yes', text: '완전한 표준' },
                        { mark: 'yes', text: 'DOJ SDLC + SWEBOK' },
                      ] },
                    { label: '분기 탐색 · 롤백',
                      cells: [
                        { mark: 'no', text: '불가' },
                        { mark: 'no', text: '대화 흐름만' },
                        { mark: 'no', text: '문서 정독뿐' },
                        { mark: 'yes', text: '자유로운 회귀' },
                      ] },
                    { label: '시작 진입 장벽',
                      cells: [
                        { mark: 'mid', text: '도구 학습' },
                        { mark: 'yes', text: '낮음' },
                        { mark: 'no', text: '매우 높음' },
                        { mark: 'yes', text: '아이디어만 입력' },
                      ] },
                  ].map((row) => (
                    <tr key={row.label}>
                      <th scope="row" className={styles.tableLabelCol}>{row.label}</th>
                      {row.cells.map((c, idx) => {
                        const isPoco = idx === 3
                        return (
                          <td key={idx} className={isPoco ? styles.pocoCol : ''}>
                            <CompareMark kind={c.mark} />
                            <div className={styles.cellText}>{c.text}</div>
                          </td>
                        )
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Reveal>

          <Reveal delay={0.3}>
            <p style={{ textAlign: 'center', marginTop: 28, fontSize: 14, color: tokens.sub, fontFamily: monoStack, letterSpacing: '-0.005em' }}>
              챗봇은 대화를 쌓습니다. Poco는 결정을 보존합니다.
            </p>
          </Reveal>
        </div>
      </section>

      {/* ===== 4. FEATURES ===== */}
      <section id="features" className={styles.snapSection} style={{ background: '#fff', padding: '80px 56px' }}>
        <div style={{ maxWidth: 1080, margin: '0 auto', width: '100%' }}>
          <Reveal>
            <div style={{ textAlign: 'center', marginBottom: 56 }}>
              <Eyebrow align="center">3 Core Features</Eyebrow>
              <h2 style={{ fontSize: 38, fontWeight: 700, letterSpacing: '-0.03em', margin: '16px 0 0' }}>
                다음 한 걸음, Poco가 함께
              </h2>
            </div>
          </Reveal>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
            {FEATURES.map((f, i) => (
              <Reveal key={f.n} delay={i * 0.12} y={36}>
                <div className={styles.card} style={{
                  padding: 28, background: '#fff',
                  border: `1px solid ${f.highlight ? tokens.primarySoftBorder : tokens.border}`,
                  borderRadius: 20,
                  boxShadow: f.highlight
                    ? '0 1px 2px rgba(124,92,255,0.08), 0 20px 40px -20px rgba(124,92,255,0.25)'
                    : '0 1px 2px rgba(20,18,40,0.03)',
                  display: 'flex', flexDirection: 'column', height: '100%',
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 22 }}>
                    <span style={{
                      fontFamily: monoStack, fontSize: 13, color: tokens.primary,
                      background: tokens.primarySoft, padding: '4px 10px', borderRadius: 7, fontWeight: 600,
                    }}>{f.n}</span>
                    <span style={{ fontSize: 11, color: tokens.sub, fontFamily: monoStack, letterSpacing: '0.08em', whiteSpace: 'nowrap' }}>{f.en}</span>
                  </div>

                  <div style={{
                    height: 96, marginBottom: 22, display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: '#FAFAFD', borderRadius: 14, border: `1px dashed ${tokens.border}`,
                  }}>
                    <FeatureIcon kind={f.icon} />
                  </div>

                  <div style={{ fontSize: 19, fontWeight: 700, letterSpacing: '-0.02em', marginBottom: 10 }}>{f.title}</div>
                  <div style={{ fontSize: 14, color: tokens.body, lineHeight: 1.65, flex: 1 }}>{f.body}</div>
                  <div style={{
                    marginTop: 20, paddingTop: 16, borderTop: `1px solid ${tokens.hairline}`,
                    fontSize: 13, color: tokens.primary, fontFamily: monoStack, letterSpacing: '-0.005em',
                  }}>— {f.quote}</div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ===== 5. 6 STAGE ===== */}
      <section className={styles.snapSection} style={{ background: tokens.bg, padding: '80px 56px' }}>
        <div style={{ maxWidth: 1180, margin: '0 auto', width: '100%' }}>
          <Reveal>
            <div style={{ textAlign: 'center', marginBottom: 72 }}>
              <Eyebrow align="center">6 Stage Process</Eyebrow>
              <h2 style={{ fontSize: 38, fontWeight: 700, letterSpacing: '-0.03em', margin: '16px 0 10px' }}>
                검증된 방법론을 자연스럽게
              </h2>
              <p style={{ fontSize: 15, color: tokens.sub, margin: 0, lineHeight: 1.65 }}>
                DOJ SDLC 10단계를 초심자·소규모 팀에 맞게 재구성한 6단계 프로세스.<br />
                각 단계마다 핵심 관문에서 멘토링과 템플릿이 제공됩니다.
              </p>
            </div>
          </Reveal>
          <StageStrip />
        </div>
      </section>

      {/* ===== 6. METHODOLOGY & TRUST ===== */}
      <section className={styles.snapSection} style={{
        background: 'linear-gradient(180deg, #1A1735 0%, #0F0E2A 100%)',
        padding: '100px 56px',
        color: '#fff',
      }}>
        <div style={{ maxWidth: 1080, margin: '0 auto', width: '100%' }}>
          <Reveal>
            <div style={{ textAlign: 'center', marginBottom: 64 }}>
              <div style={{
                fontSize: 12.5, color: '#9D87FF', fontWeight: 600,
                letterSpacing: '0.16em', textTransform: 'uppercase',
                fontFamily: monoStack, display: 'inline-flex', alignItems: 'center', gap: 8,
              }}>
                <span style={{ width: 6, height: 6, borderRadius: 99, background: '#9D87FF', display: 'inline-block' }} />
                Methodology & Trust
              </div>
              <h2 style={{
                fontSize: 44, lineHeight: 1.25, fontWeight: 800, letterSpacing: '-0.03em',
                margin: '20px 0 16px', color: '#fff',
              }}>
                AI의 즉흥성이 아닌,<br />
                <span style={{
                  background: 'linear-gradient(90deg, #B6A2FF 0%, #7C5CFF 100%)',
                  WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                }}>20년의 방법론</span> 위에서 작동합니다.
              </h2>
              <p style={{ fontSize: 15.5, color: '#A8A2C8', margin: 0, lineHeight: 1.7 }}>
                Poco의 AI 프롬프트는 국제 표준 문서에 근거합니다.<br />
                단순한 생성이 아닌, 검증된 프레임워크 기반의 구조적 안내를 제공합니다.
              </p>
            </div>
          </Reveal>

          {/* Stats */}
          <Reveal delay={0.1}>
            <div style={{
              display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16,
              maxWidth: 720, margin: '0 auto 64px', textAlign: 'center',
            }}>
              {[
                { value: '20+', label: '년간 검증된 방법론' },
                { value: '16', label: '편의 자체 가이드 문서' },
                { value: '25', label: '개 Knowledge Area 커버' },
              ].map((s, i) => (
                <div key={i}>
                  <div style={{
                    fontSize: 56, fontWeight: 800, lineHeight: 1, color: '#fff',
                    letterSpacing: '-0.04em', fontFamily: fontStack,
                  }}>
                    {s.value}
                  </div>
                  <div style={{
                    fontSize: 13, color: '#9890BC', marginTop: 12,
                    letterSpacing: '-0.005em',
                  }}>
                    {s.label}
                  </div>
                </div>
              ))}
            </div>
          </Reveal>

          {/* Source cards */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
            <Reveal delay={0.18}>
              <SourceCard
                title="SWEBOK"
                badge="V4.0"
                year="2024"
                subtitle="Software Engineering Body of Knowledge"
                publisher="IEEE Computer Society"
                description="전 세계 소프트웨어 공학의 지식체계를 정의하는 국제 표준. 15개 Knowledge Area를 기반으로 소프트웨어 개발의 전 과정을 체계화합니다."
                tag="15개 Knowledge Area"
                href="https://www.computer.org/education/bodies-of-knowledge/software-engineering"
              />
            </Reveal>
            <Reveal delay={0.28}>
              <SourceCard
                title="DOJ SDLC"
                badge="Guidance"
                year="2003"
                subtitle="System Development Life Cycle"
                publisher="U.S. Department of Justice"
                description="미국 법무부가 정의한 시스템 개발 생명주기 실무 가이드라인. 10단계 Phase를 통해 프로젝트 전 과정의 의사결정을 구조화합니다."
                tag="10단계 Phase"
                href="https://www.justice.gov/archive/jmd/irm/lifecycle/table.htm"
              />
            </Reveal>
          </div>
        </div>
      </section>

      {/* ===== 7. WHO IS IT FOR ===== */}
      <section id="personas" className={styles.snapSection} style={{ background: tokens.bg, padding: '80px 56px' }}>
        <div style={{ maxWidth: 1080, margin: '0 auto', width: '100%' }}>
          <Reveal>
            <div style={{ textAlign: 'center', marginBottom: 56 }}>
              <Eyebrow align="center">Who's It For</Eyebrow>
              <h2 style={{ fontSize: 38, fontWeight: 700, letterSpacing: '-0.03em', margin: '16px 0 0' }}>
                누구를 위한 건가요?
              </h2>
            </div>
          </Reveal>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 18 }}>
            {PERSONAS.map((p, i) => (
              <Reveal key={p.kind} delay={i * 0.08} y={32}>
                <div className={styles.card} style={{
                  padding: 28, background: '#fff',
                  border: `1px solid ${tokens.border}`, borderRadius: 18,
                  display: 'flex', gap: 18, alignItems: 'flex-start',
                }}>
                  <div style={{
                    flexShrink: 0, width: 56, height: 56, borderRadius: 14,
                    background: tokens.primarySoft, display: 'grid', placeItems: 'center',
                  }}>
                    <PersonaIcon kind={p.kind} />
                  </div>
                  <div>
                    <div style={{ fontSize: 17, fontWeight: 700, letterSpacing: '-0.02em' }}>{p.title}</div>
                    <div style={{ fontSize: 14, color: tokens.body, lineHeight: 1.65, marginTop: 8 }}>{p.body}</div>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ===== 8. PROJECT GALLERY ===== */}
      <section className={styles.snapSection} style={{ background: '#fff', padding: '80px 56px' }}>
        <div style={{ maxWidth: 1080, margin: '0 auto', width: '100%' }}>
          <Reveal>
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
              <Eyebrow align="center">In the Wild</Eyebrow>
              <h2 style={{ fontSize: 38, fontWeight: 700, letterSpacing: '-0.03em', margin: '16px 0 10px' }}>
                이런 프로젝트들이 자라고 있어요
              </h2>
              <p style={{ fontSize: 15, color: tokens.sub, margin: 0, lineHeight: 1.65 }}>
                다양한 영역의 아이디어가 Poco 위에서 구조를 잡아가고 있습니다.
              </p>
            </div>
          </Reveal>

          <Reveal delay={0.15}>
            <div className={styles.marqueeWrap} style={{ marginTop: 48 }}>
              <MarqueeRow items={GALLERY_ROW_1} direction="left" duration={38} />
              <MarqueeRow items={GALLERY_ROW_2} direction="right" duration={42} />
            </div>
          </Reveal>

          <Reveal delay={0.4}>
            <p style={{
              textAlign: 'center', marginTop: 48, fontSize: 13, color: tokens.sub,
              fontFamily: monoStack, letterSpacing: '0.04em',
            }}>
              당신의 다음 한 걸음은 무엇인가요?
            </p>
          </Reveal>
        </div>
      </section>

      {/* ===== 9. CTA + FOOTER ===== */}
      <section className={`${styles.snapSection} ${styles.hasFooter}`} style={{ background: '#fff' }}>
        <div className={styles.snapCta}>
          <div style={{ maxWidth: 720, margin: '0 auto', textAlign: 'center' }}>
            <Reveal>
              <h2 style={{ fontSize: 42, fontWeight: 700, letterSpacing: '-0.03em', margin: 0, lineHeight: 1.25 }}>
                당신의 <span style={{ color: tokens.primary }}>첫 발자국</span>을<br />
                남겨보세요
              </h2>
            </Reveal>
            <Reveal delay={0.15}>
              <p style={{ marginTop: 24, fontSize: 16, color: tokens.body, lineHeight: 1.65 }}>
                조금씩, 한 걸음씩 — 아이디어를 설계까지 함께 쌓아가요.
              </p>
            </Reveal>
            <Reveal delay={0.3}>
              <div style={{ marginTop: 36, display: 'flex', gap: 12, justifyContent: 'center' }}>
                <PrimaryCTA size="lg" onClick={handleStart} glow>무료로 시작하기 →</PrimaryCTA>
              </div>
            </Reveal>
          </div>
        </div>

        <footer style={{
          width: '100%', padding: '48px 56px 40px',
          borderTop: `1px solid ${tokens.hairline}`, background: '#fff',
          boxSizing: 'border-box', fontFamily: fontStack,
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 40 }}>
            <div style={{ flex: 1, minWidth: 0 }}>
              <img src="/poco-logo-text.svg" alt="poco" height={28} />
              <div style={{ fontSize: 13, color: tokens.sub, marginTop: 12, lineHeight: 1.6 }}>
                조금씩, 한 걸음씩 — 아이디어를 설계까지 쌓아가는 사고의 캔버스.<br />
                국민대학교 캡스톤 디자인 2026 · Team 59
              </div>
            </div>
            <div style={{ display: 'flex', gap: 56, flexShrink: 0 }}>
              <div>
                <div style={{ fontSize: 11.5, color: tokens.sub, fontWeight: 600, marginBottom: 12, letterSpacing: '0.04em', textTransform: 'uppercase' }}>Project</div>
                {[
                  { l: 'GitHub Repo', h: 'https://github.com/kookmin-sw/2026-capstone-59' },
                  { l: 'Docs', h: 'https://kookmin-sw.github.io/2026-capstone-59/' },
                ].map((it) => (
                  <a key={it.l} href={it.h} target="_blank" rel="noopener noreferrer" style={{ display: 'block', fontSize: 13.5, color: tokens.ink, marginBottom: 8, textDecoration: 'none' }}>
                    {it.l} ↗
                  </a>
                ))}
              </div>
              <div>
                <div style={{ fontSize: 11.5, color: tokens.sub, fontWeight: 600, marginBottom: 12, letterSpacing: '0.04em', textTransform: 'uppercase' }}>Team</div>
                {['정연승', '장우리', '김한림', '박수연'].map((n) => (
                  <div key={n} style={{ fontSize: 13.5, color: tokens.ink, marginBottom: 8 }}>{n}</div>
                ))}
              </div>
            </div>
          </div>
          <div style={{ marginTop: 36, paddingTop: 20, borderTop: `1px solid ${tokens.hairline}`, fontSize: 12, color: tokens.sub, display: 'flex', justifyContent: 'space-between' }}>
            <span>© 2026 Poco · Kookmin University Capstone</span>
            <span style={{ fontFamily: monoStack }}>v0.1</span>
          </div>
        </footer>
      </section>
    </div>
  )
}

const navLinkStyle = {
  fontSize: 14, color: tokens.body, textDecoration: 'none',
  fontFamily: fontStack, fontWeight: 500, whiteSpace: 'nowrap',
}
