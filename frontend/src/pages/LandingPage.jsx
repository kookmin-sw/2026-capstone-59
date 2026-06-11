import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { HiMenu, HiX} from 'react-icons/hi'
import { getMe, logout } from '../api/auth'
import PocoLogo from '../components/PocoLogo'
import styles from './LandingPage.module.css'

// ===== Static copy (Claude Design 결과 그대로 박제) =====
const PANELS = [
  {
    title: '다음 한 걸음을, AI가 제안합니다.',
    body: '검증된 소프트웨어 개발 방법론의 6단계 프로세스를 따라 노드가 동적으로 뻗어나갑니다. 각 단계의 핵심 관문은 다이아몬드 노드로 자연스럽게 나타납니다.',
    caption: '막연함을 다음 한 걸음으로.',
  },
  {
    title: '노드를 클릭하면, 사이드패널이 펼쳐집니다.',
    body: '해당 단계의 멘토링과 용어 사전이 함께 보이고, 핵심 관문에 도달하면 팀이 설계한 노션 템플릿이 연결됩니다.',
    caption: '맥락에 맞는 어시스턴트가, 곁에.',
  },
  {
    title: '아이디어가 흔들려도 괜찮습니다.',
    body: '이전 분기점으로 돌아가면 AI가 바뀐 맥락에 맞춰 새 길을 제안합니다. 모든 선택의 궤적이 캔버스에 트리로 남습니다.',
    caption: '되돌아갈 수 있는 선택, 트리로 남는 사고 과정.',
  },
  {
    title: <>사고가 정리되면,<br />한 장의 마크다운으로.</>,
    body: '의사결정 궤적이 .md 한 장으로 추출됩니다. Claude · ChatGPT · Cursor 어디든 첨부할 수 있습니다.',
    caption: '선택은 자산이 됩니다.',
  },
]

// ===== Hero Screen — 노드 콘스텔레이션이 천천히 호흡하는 추상 표현 =====
function HeroScreen() {
  return (
    <div className={styles.heroScreen}>
      <svg viewBox="0 0 800 500" preserveAspectRatio="xMidYMid slice" className={styles.heroScreenSvg}>
        <defs>
          <radialGradient id="heroBg" cx="50%" cy="40%" r="70%">
            <stop offset="0%" stopColor="#3a2f6e" />
            <stop offset="55%" stopColor="#251c4f" />
            <stop offset="100%" stopColor="#15103a" />
          </radialGradient>
          <radialGradient id="heroGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(180, 160, 240, 0.45)" />
            <stop offset="100%" stopColor="rgba(180, 160, 240, 0)" />
          </radialGradient>
        </defs>

        <rect width="800" height="500" fill="url(#heroBg)" />
        {/* Soft glow blob — drifts slowly */}
        <ellipse cx="400" cy="250" rx="280" ry="200" fill="url(#heroGlow)" className={styles.heroGlow} />

        {/* Connecting lines — 다이아 우측 정점에서 오른쪽으로 뻗는 4개 분기 */}
        <line x1="210" y1="250" x2="440" y2="130" className={styles.heroLine} />
        <line x1="210" y1="250" x2="600" y2="210" className={styles.heroLine} />
        <line x1="210" y1="250" x2="600" y2="290" className={styles.heroLine} />
        <line x1="210" y1="250" x2="440" y2="370" className={styles.heroLine} />

        {/* Central diamond — 좌측에서 분기 시작점 */}
        <g className={styles.heroDiamond}>
          <polygon points="170,210 210,250 170,290 130,250" fill="rgba(180, 160, 240, 0.18)" stroke="#c8b8ff" strokeWidth="1.5" />
        </g>

        {/* Floating step nodes — 우측으로 펼쳐진 가로 흐름 */}
        <g className={`${styles.heroNode} ${styles.heroNodeA}`}>
          <circle cx="440" cy="130" r="14" fill="rgba(180, 160, 240, 0.1)" stroke="#b8a5e6" strokeWidth="1.2" />
        </g>
        <g className={`${styles.heroNode} ${styles.heroNodeB}`}>
          <circle cx="600" cy="210" r="14" fill="rgba(180, 160, 240, 0.1)" stroke="#b8a5e6" strokeWidth="1.2" />
        </g>
        <g className={`${styles.heroNode} ${styles.heroNodeC}`}>
          <circle cx="600" cy="290" r="14" fill="rgba(180, 160, 240, 0.1)" stroke="#b8a5e6" strokeWidth="1.2" />
        </g>
        <g className={`${styles.heroNode} ${styles.heroNodeD}`}>
          <circle cx="440" cy="370" r="14" fill="rgba(180, 160, 240, 0.1)" stroke="#b8a5e6" strokeWidth="1.2" />
        </g>

        {/* Drifting particles — barely visible */}
        <circle cx="120" cy="100" r="2" className={styles.heroParticleA} fill="#d6c9ff" />
        <circle cx="680" cy="80" r="1.5" className={styles.heroParticleB} fill="#d6c9ff" />
        <circle cx="150" cy="420" r="2" className={styles.heroParticleC} fill="#d6c9ff" />
        <circle cx="650" cy="430" r="1.5" className={styles.heroParticleD} fill="#d6c9ff" />
        <circle cx="380" cy="80" r="1.2" className={styles.heroParticleE} fill="#d6c9ff" />
      </svg>
    </div>
  )
}

// ===== Demo Video — 영상이 있으면 video, 없으면 fallback 애니메이션 =====
// 영상 파일: public/assets/demo-panel-1.webm ~ demo-panel-4.webm
// 영상이 준비되면 해당 경로에 파일만 넣으면 자동 재생됨
// BASE: GitHub Pages 서브경로 배포 대응 (base '/'면 '/assets/...', '/landing/'면 그 하위로 resolve)
const BASE = import.meta.env.BASE_URL
const DEMO_VIDEOS = [
  `${BASE}assets/demo-panel-1`,
  `${BASE}assets/demo-panel-2`,
  `${BASE}assets/demo-panel-3`,
  `${BASE}assets/demo-panel-4`,
]

function DemoVideo({ index, playing, fallback }) {
  const Fallback = fallback
  const videoRef = useRef(null)
  const [videoError, setVideoError] = useState(false)

  useEffect(() => {
    if (!videoRef.current) return
    if (playing) {
      videoRef.current.currentTime = 0
      videoRef.current.play().catch(() => {})
    } else {
      videoRef.current.pause()
    }
  }, [playing])

  if (videoError) {
    return <Fallback playing={playing} />
  }

  return (
    <video
      ref={videoRef}
      muted
      loop
      playsInline
      onError={() => setVideoError(true)}
      style={{ width: '100%', height: '100%', objectFit: 'fill', display: 'block' }}
    >
      <source src={`${DEMO_VIDEOS[index]}.mp4`} type="video/mp4" />
      <source src={`${DEMO_VIDEOS[index]}.webm`} type="video/webm" />
    </video>
  )
}

// Hero iMac 영상 — public/assets/demo-hero.mp4 (또는 .webm) 이 있으면 영상, 없으면 HeroScreen fallback
function HeroDemoVideo() {
  const [videoError, setVideoError] = useState(false)

  if (videoError) {
    return <HeroScreen />
  }

  return (
    <video
      autoPlay
      muted
      loop
      playsInline
      onError={() => setVideoError(true)}
      style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
    >
      <source src={`${BASE}assets/demo-hero.mp4`} type="video/mp4" />
      <source src={`${BASE}assets/demo-hero.webm`} type="video/webm" />
    </video>
  )
}

// ===== Panel 1 Screen — 다이아 노드 클릭 → 3개 분기 애니메이션 =====
// 7s 루프: 다이아 등장 → 클릭 펄스 → 3개 분기 라인 → 3개 Step 노드 등장 → 페이드아웃
function PanelScreen1({ playing }) {
  return (
    <div className={`${styles.mock} ${playing ? styles.mockPlaying : ''}`}>
      {/* LEFT: Stage Navigator */}
      <div className={styles.mockNav}>
        <div className={styles.mockNavTitle}>Stages</div>
        {['아이디어 구체화', '프로젝트 계획', '요구사항 정의', '설계', '개발', '테스트 및 검증'].map(
          (label, i) => (
            <div
              key={label}
              className={`${styles.mockNavItem} ${i === 1 ? styles.mockNavActive : ''}`}
            >
              <span className={styles.mockNavNum}>{i + 1}</span>
              <span>{label}</span>
            </div>
          )
        )}
      </div>

      {/* RIGHT: Canvas with animated nodes */}
      <div className={styles.mockCanvas}>
        <svg viewBox="0 0 600 400" preserveAspectRatio="xMidYMid meet" className={styles.mockSvg}>
          {/* Grid background dots */}
          <defs>
            <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
              <circle cx="1" cy="1" r="1" fill="rgba(108, 99, 181, 0.08)" />
            </pattern>
          </defs>
          <rect width="600" height="400" fill="url(#grid)" />

          {/* Click ripple ring around the diamond */}
          <circle cx="130" cy="200" r="36" className={styles.mockRipple} />

          {/* Diamond (Required Step) node — 좌측 */}
          <g className={styles.mockDiamond}>
            <polygon
              points="130,160 170,200 130,240 90,200"
              fill="#fff"
              stroke="var(--p)"
              strokeWidth="2.5"
            />
            <text
              x="130"
              y="206"
              textAnchor="middle"
              fontSize="11"
              fill="var(--p)"
              fontWeight="700"
            >
              R
            </text>
          </g>

          {/* 3 branch lines — 우측으로 펼침 */}
          <line x1="170" y1="200" x2="430" y2="100" className={`${styles.mockBranch} ${styles.mockBranch1}`} />
          <line x1="170" y1="200" x2="430" y2="200" className={`${styles.mockBranch} ${styles.mockBranch2}`} />
          <line x1="170" y1="200" x2="430" y2="300" className={`${styles.mockBranch} ${styles.mockBranch3}`} />

          {/* 3 Step nodes — 우측 세로 정렬 */}
          <g className={`${styles.mockStep} ${styles.mockStep1}`}>
            <circle cx="460" cy="100" r="28" fill="#fff" stroke="var(--p)" strokeWidth="2" />
            <text x="460" y="105" textAnchor="middle" fontSize="11" fill="var(--p)">
              S1
            </text>
          </g>
          <g className={`${styles.mockStep} ${styles.mockStep2}`}>
            <circle cx="460" cy="200" r="28" fill="#fff" stroke="var(--p)" strokeWidth="2" />
            <text x="460" y="205" textAnchor="middle" fontSize="11" fill="var(--p)">
              S2
            </text>
          </g>
          <g className={`${styles.mockStep} ${styles.mockStep3}`}>
            <circle cx="460" cy="300" r="28" fill="#fff" stroke="var(--p)" strokeWidth="2" />
            <text x="460" y="305" textAnchor="middle" fontSize="11" fill="var(--p)">
              S3
            </text>
          </g>
        </svg>
      </div>
    </div>
  )
}

// ===== Panel 2 Screen — S2 노드 클릭 → 우측 사이드패널 슬라이드 인 =====
function PanelScreen2({ playing }) {
  return (
    <div className={`${styles.mock} ${playing ? styles.mockPlaying : ''}`}>
      <div className={styles.mockNav}>
        <div className={styles.mockNavTitle}>Stages</div>
        {['아이디어 구체화', '프로젝트 계획', '요구사항 정의', '설계', '개발', '테스트 및 검증'].map(
          (label, i) => (
            <div
              key={label}
              className={`${styles.mockNavItem} ${i === 1 ? styles.mockNavActive : ''}`}
            >
              <span className={styles.mockNavNum}>{i + 1}</span>
              <span>{label}</span>
            </div>
          )
        )}
      </div>

      <div className={styles.mockCanvas}>
        <svg viewBox="0 0 600 400" preserveAspectRatio="xMidYMid meet" className={styles.mockSvg}>
          <defs>
            <pattern id="grid2" width="30" height="30" patternUnits="userSpaceOnUse">
              <circle cx="1" cy="1" r="1" fill="rgba(108, 99, 181, 0.08)" />
            </pattern>
          </defs>
          <rect width="600" height="400" fill="url(#grid2)" />

          {/* Diamond + 3 Step nodes — 좌측에서 우측으로 수평 분기 */}
          <polygon points="90,160 130,200 90,240 50,200" fill="#fff" stroke="var(--p)" strokeWidth="2.5" />
          <text x="90" y="206" textAnchor="middle" fontSize="11" fill="var(--p)" fontWeight="700">R</text>
          <line x1="130" y1="200" x2="230" y2="110" stroke="var(--p)" strokeWidth="1.5" opacity="0.4" />
          <line x1="130" y1="200" x2="230" y2="200" stroke="var(--p)" strokeWidth="1.5" opacity="0.4" />
          <line x1="130" y1="200" x2="230" y2="290" stroke="var(--p)" strokeWidth="1.5" opacity="0.4" />
          <g><circle cx="250" cy="110" r="22" fill="#fff" stroke="var(--p)" strokeWidth="1.5" opacity="0.55" /><text x="250" y="114" textAnchor="middle" fontSize="10" fill="var(--p)" opacity="0.55">S1</text></g>
          <g><circle cx="250" cy="290" r="22" fill="#fff" stroke="var(--p)" strokeWidth="1.5" opacity="0.55" /><text x="250" y="294" textAnchor="middle" fontSize="10" fill="var(--p)" opacity="0.55">S3</text></g>
          {/* S2 — 강조될 노드 (중앙) */}
          <circle cx="250" cy="200" r="30" className={styles.mockSelectedRing} fill="none" stroke="var(--p)" strokeWidth="2" />
          <g><circle cx="250" cy="200" r="22" fill="#fff" stroke="var(--p)" strokeWidth="2" /><text x="250" y="204" textAnchor="middle" fontSize="10" fill="var(--p)" fontWeight="700">S2</text></g>

          {/* Side Panel — 우측에서 슬라이드 인 */}
          <g className={styles.mockSidePanel}>
            <rect x="360" y="20" width="220" height="360" rx="14" fill="#fff" stroke="var(--border)" />
            {/* Header */}
            <rect x="378" y="40" width="80" height="10" rx="3" fill="var(--p-faint)" />
            <rect x="378" y="60" width="140" height="14" rx="3" fill="var(--t-strong)" />
            {/* Tabs */}
            <rect x="378" y="92" width="50" height="6" rx="2" fill="var(--p)" />
            <rect x="438" y="92" width="44" height="6" rx="2" fill="var(--border)" />
            {/* Content lines — typing stagger */}
            <rect x="378" y="118" width="60" height="8" rx="2" fill="var(--t-strong)" className={styles.mockLine1} />
            <rect x="378" y="138" width="180" height="6" rx="2" fill="var(--border-soft)" className={styles.mockLine2} />
            <rect x="378" y="152" width="170" height="6" rx="2" fill="var(--border-soft)" className={styles.mockLine3} />
            <rect x="378" y="166" width="120" height="6" rx="2" fill="var(--border-soft)" className={styles.mockLine4} />
            <rect x="378" y="198" width="80" height="8" rx="2" fill="var(--t-strong)" className={styles.mockLine5} />
            <rect x="378" y="218" width="180" height="6" rx="2" fill="var(--border-soft)" className={styles.mockLine6} />
            <rect x="378" y="232" width="160" height="6" rx="2" fill="var(--border-soft)" className={styles.mockLine7} />
            {/* Term chips */}
            <g className={styles.mockChip1}>
              <rect x="378" y="266" width="60" height="20" rx="10" fill="var(--p-faint)" />
              <text x="408" y="280" textAnchor="middle" fontSize="9" fill="var(--p)" fontWeight="700">용어</text>
            </g>
            <g className={styles.mockChip2}>
              <rect x="446" y="266" width="72" height="20" rx="10" fill="var(--p-faint)" />
              <text x="482" y="280" textAnchor="middle" fontSize="9" fill="var(--p)" fontWeight="700">Term</text>
            </g>
          </g>
        </svg>
      </div>
    </div>
  )
}

// ===== Panel 3 Screen — 여러 분기 → 롤백 =====
function PanelScreen3({ playing }) {
  return (
    <div className={`${styles.mock} ${playing ? styles.mockPlaying : ''}`}>
      <div className={styles.mockNav}>
        <div className={styles.mockNavTitle}>Stages</div>
        {['아이디어 구체화', '프로젝트 계획', '요구사항 정의', '설계', '개발', '테스트 및 검증'].map(
          (label, i) => (
            <div
              key={label}
              className={`${styles.mockNavItem} ${i === 2 ? styles.mockNavActive : ''}`}
            >
              <span className={styles.mockNavNum}>{i + 1}</span>
              <span>{label}</span>
            </div>
          )
        )}
      </div>

      <div className={styles.mockCanvas}>
        <svg viewBox="0 0 600 400" preserveAspectRatio="xMidYMid meet" className={styles.mockSvg}>
          <defs>
            <pattern id="grid3" width="30" height="30" patternUnits="userSpaceOnUse">
              <circle cx="1" cy="1" r="1" fill="rgba(108, 99, 181, 0.08)" />
            </pattern>
          </defs>
          <rect width="600" height="400" fill="url(#grid3)" />

          {/* Root diamond — 좌측 시작점 */}
          <polygon points="70,170 100,200 70,230 40,200" fill="#fff" stroke="var(--p)" strokeWidth="2" />
          <text x="70" y="205" textAnchor="middle" fontSize="10" fill="var(--p)" fontWeight="700">R1</text>

          {/* Level 1 lines — 우측 상하 분기 */}
          <line x1="100" y1="200" x2="240" y2="130" stroke="var(--p)" strokeWidth="1.5" opacity="0.5" />
          <line x1="100" y1="200" x2="240" y2="270" stroke="var(--p)" strokeWidth="1.5" opacity="0.5" />

          {/* Level 1 nodes */}
          <g className={styles.mockBranchKeep}>
            <circle cx="260" cy="130" r="20" fill="var(--p)" stroke="var(--p)" strokeWidth="2" />
            <text x="260" y="134" textAnchor="middle" fontSize="9" fill="#fff" fontWeight="700">A1</text>
          </g>
          <g className={styles.mockBranchRollback}>
            <circle cx="260" cy="270" r="20" fill="#fff" stroke="var(--p)" strokeWidth="2" />
            <text x="260" y="274" textAnchor="middle" fontSize="9" fill="var(--p)" fontWeight="700">B1</text>
          </g>

          {/* Level 2 — B1 의 자식 (rollback 시 취소될 분기) */}
          <g className={styles.mockToRollback}>
            <line x1="280" y1="270" x2="410" y2="230" stroke="var(--p)" strokeWidth="1.5" opacity="0.5" />
            <line x1="280" y1="270" x2="410" y2="320" stroke="var(--p)" strokeWidth="1.5" opacity="0.5" />
            <circle cx="430" cy="230" r="18" fill="#fff" stroke="var(--p)" strokeWidth="1.8" />
            <text x="430" y="234" textAnchor="middle" fontSize="9" fill="var(--p)">B2</text>
            <circle cx="430" cy="320" r="18" fill="#fff" stroke="var(--p)" strokeWidth="1.8" />
            <text x="430" y="324" textAnchor="middle" fontSize="9" fill="var(--p)">B3</text>
          </g>

          {/* Click ripple on B1 (rollback target) */}
          <circle cx="260" cy="270" r="28" className={styles.mockRollbackRipple} fill="none" stroke="var(--p)" strokeWidth="2" />

          {/* Replacement branch — appears after rollback (B1 우측에 새 ? 노드) */}
          <g className={styles.mockNewBranch}>
            <line x1="280" y1="270" x2="410" y2="270" stroke="var(--p)" strokeWidth="1.5" opacity="0.5" />
            <circle cx="430" cy="270" r="18" fill="#fff" stroke="var(--p)" strokeWidth="1.8" strokeDasharray="3 3" />
            <text x="430" y="274" textAnchor="middle" fontSize="9" fill="var(--p)">?</text>
          </g>
        </svg>
      </div>
    </div>
  )
}

// ===== Panel 4 Screen — Step 영역 선택 → .md 다운로드 =====
function PanelScreen4({ playing }) {
  return (
    <div className={`${styles.mock} ${playing ? styles.mockPlaying : ''}`}>
      <div className={styles.mockNav}>
        <div className={styles.mockNavTitle}>Stages</div>
        {['아이디어 구체화', '프로젝트 계획', '요구사항 정의', '설계', '개발', '테스트 및 검증'].map(
          (label, i) => (
            <div
              key={label}
              className={`${styles.mockNavItem} ${i === 3 ? styles.mockNavActive : ''}`}
            >
              <span className={styles.mockNavNum}>{i + 1}</span>
              <span>{label}</span>
            </div>
          )
        )}
      </div>

      <div className={styles.mockCanvas}>
        <svg viewBox="0 0 600 400" preserveAspectRatio="xMidYMid meet" className={styles.mockSvg}>
          <defs>
            <pattern id="grid4" width="30" height="30" patternUnits="userSpaceOnUse">
              <circle cx="1" cy="1" r="1" fill="rgba(108, 99, 181, 0.08)" />
            </pattern>
          </defs>
          <rect width="600" height="400" fill="url(#grid4)" />

          {/* Faint background tree (dim while modal up) */}
          <g opacity="0.18">
            <polygon points="120,80 145,105 120,130 95,105" fill="#fff" stroke="var(--p)" strokeWidth="1.5" />
            <circle cx="120" cy="180" r="16" fill="#fff" stroke="var(--p)" strokeWidth="1.5" />
            <circle cx="120" cy="240" r="16" fill="var(--p)" stroke="var(--p)" />
            <circle cx="120" cy="300" r="16" fill="#fff" stroke="var(--p)" strokeWidth="1.5" />
            <line x1="120" y1="105" x2="120" y2="295" stroke="var(--p)" strokeWidth="1" />
          </g>

          {/* Export Modal */}
          <g className={styles.mockModal}>
            <rect x="220" y="60" width="320" height="280" rx="16" fill="#fff" stroke="var(--border)" />
            {/* Modal title */}
            <rect x="240" y="84" width="120" height="14" rx="3" fill="var(--t-strong)" />
            <rect x="240" y="106" width="220" height="6" rx="2" fill="var(--border-soft)" />
            {/* Checklist rows */}
            <g className={styles.mockCheck1}>
              <rect x="240" y="138" width="14" height="14" rx="3" className={styles.mockCheckBox} />
              <rect x="262" y="142" width="180" height="6" rx="2" fill="var(--t-strong)" />
            </g>
            <g className={styles.mockCheck2}>
              <rect x="240" y="166" width="14" height="14" rx="3" className={styles.mockCheckBox} />
              <rect x="262" y="170" width="200" height="6" rx="2" fill="var(--t-strong)" />
            </g>
            <g className={styles.mockCheck3}>
              <rect x="240" y="194" width="14" height="14" rx="3" className={styles.mockCheckBox} />
              <rect x="262" y="198" width="160" height="6" rx="2" fill="var(--t-strong)" />
            </g>
            {/* Download button */}
            <g className={styles.mockDownloadBtn}>
              <rect x="380" y="280" width="140" height="36" rx="18" fill="var(--p)" />
              <text x="450" y="303" textAnchor="middle" fontSize="11" fill="#fff" fontWeight="700">
                내보내기
              </text>
            </g>
          </g>

          {/* Download toast (slides in bottom right after click) */}
          <g className={styles.mockToast}>
            <rect x="380" y="350" width="180" height="36" rx="10" fill="#fff" stroke="var(--border)" />
            <circle cx="400" cy="368" r="6" fill="var(--p)" />
            <rect x="414" y="364" width="110" height="6" rx="2" fill="var(--t-strong)" />
            <rect x="414" y="374" width="80" height="4" rx="2" fill="var(--border-soft)" />
          </g>
        </svg>
      </div>
    </div>
  )
}

const PERSONAS = [
  { glyph: '🤔', title: '캡스톤을 준비 중인 대학생', body: '첫 팀 프로젝트, 어디서부터 시작해야 할지 모를 때.' },
  { glyph: '😕', title: '사이드 프로젝트를 구상 중인 개발자', body: '아이디어는 넘치는데, 체계적으로 정리하고 싶을 때.' },
  { glyph: '🤥', title: '초기 스타트업 창업팀', body: '회사 표준도 멘토도 없는데, 표준 위에서 첫 사이클을 완주하고 싶을 때.' },
]

// SDLC 6 Stage — Scene 4 다이어그램
const SDLC_STAGES = [
  { num: 1, name: '아이디어 구체화', en: 'Ideation' },
  { num: 2, name: '프로젝트 계획', en: 'Planning' },
  { num: 3, name: '요구사항 정의', en: 'Requirement' },
  { num: 4, name: '설계', en: 'Design' },
  { num: 5, name: '개발', en: 'Development' },
  { num: 6, name: '테스트 및 검증', en: 'Test' },
]

// 타임라인 도트 위치(%) — Claude Design 원본 그대로 (12.5 / 37.5 / 62.5 / 87.5)
const DOT_TOPS = [12.5, 37.5, 62.5, 87.5]

// ===== Reusable atoms =====
function ArrowRight() {
  return (
    <svg className={styles.arr} width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path
        d="M3 7h8m0 0L7.5 3.5M11 7L7.5 10.5"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function ArrowDown() {
  return (
    <svg width="12" height="12" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path
        d="M7 3v8m0 0L3.5 7.5M7 11l3.5-3.5"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

// IntersectionObserver 1회용 reveal hook — 진입 후 in 클래스 부여 후 unobserve
function useReveal(ref) {
  const [visible, setVisible] = useState(false)
  useEffect(() => {
    const el = ref.current
    if (!el) return undefined
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            setVisible(true)
            io.unobserve(e.target)
          }
        })
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    )
    io.observe(el)
    return () => io.disconnect()
  }, [ref])
  return visible
}

function Reveal({ as = 'div', delay = 0, className = '', children, ...rest }) {
  const ref = useRef(null)
  const visible = useReveal(ref)
  const delayClass =
    delay === 1 ? styles.d1
      : delay === 2 ? styles.d2
      : delay === 3 ? styles.d3
      : delay === 4 ? styles.d4
      : ''
  // eslint-plugin-react가 없어 JSX 태그를 직접 받지 못함. capital 변수로 변환 후 JSX 사용.
  const Tag = as
  return (
    <Tag
      ref={ref}
      className={`${styles.reveal} ${visible ? styles.revealIn : ''} ${delayClass} ${className}`.trim()}
      {...rest}
    >
      {children}
    </Tag>
  )
}

// ===== Main =====
export default function LandingPage() {
  const navigate = useNavigate()
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [navScrolled, setNavScrolled] = useState(false)
  const [activePanel, setActivePanel] = useState(0)
  const [railHeight, setRailHeight] = useState(0)
  // SDLC stage stagger-fill: 진입 시 280 + i*360ms 마다 active, 그 직후 이전 stage lit
  const [sdlcActive, setSdlcActive] = useState(new Set())
  const [sdlcLit, setSdlcLit] = useState(new Set())

  const [menuOpen, setMenuOpen] = useState(false)

  const stageRef = useRef(null)
  const panelRefs = useRef([])
  const sdlcRef = useRef(null)

  // 로그인 상태 확인
  useEffect(() => {
    let cancelled = false
    getMe()
      .then(() => { if (!cancelled) setIsLoggedIn(true) })
      .catch(() => { if (!cancelled) setIsLoggedIn(false) })
    return () => { cancelled = true }
  }, [])

  useEffect(() => {
    document.documentElement.style.scrollbarGutter = 'stable'
    return () => { document.documentElement.style.scrollbarGutter = '' }
  }, [])

  // CTA 동작 — 로그인 상태에 따라 분기
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

  // anchor click → smooth scroll into view
  const handleAnchorClick = useCallback((e, id) => {
    e.preventDefault()
    const target = document.getElementById(id)
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [])

  // Nav scrolled state
  useEffect(() => {
    const onScroll = () => setNavScrolled(window.scrollY > 12)
    window.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  //
  const location = useLocation()
  useEffect(() => {
    if (location.state?.scrollTo) {
      document.getElementById(location.state.scrollTo)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [location.state])

  // Sticky showcase: 가장 viewport 중심에 가까운 panel을 active로,
  // stage scroll progress를 timeline fill 높이로 변환.
  useEffect(() => {
    const stage = stageRef.current
    if (!stage) return undefined

    function update() {
      const vh = window.innerHeight
      const center = vh / 2

      // 가장 중앙에 가까운 panel idx 찾기
      let best = 0
      let bestDist = Infinity
      panelRefs.current.forEach((p, i) => {
        if (!p) return
        const r = p.getBoundingClientRect()
        const pCenter = r.top + r.height / 2
        const d = Math.abs(pCenter - center)
        if (d < bestDist) { bestDist = d; best = i }
      })
      setActivePanel(best)

      // stage 진행률 0..1
      const sr = stage.getBoundingClientRect()
      const stageH = stage.offsetHeight
      const scrolled = vh - sr.top
      const total = stageH + vh
      let p = scrolled / total
      if (p < 0) p = 0
      if (p > 1) p = 1
      // first→last dot 범위에 맞게 tighten
      const tight = Math.max(0, Math.min(1, (p - 0.18) / 0.64))
      setRailHeight(tight * 100)
    }

    window.addEventListener('scroll', update, { passive: true })
    window.addEventListener('resize', update)
    update()
    return () => {
      window.removeEventListener('scroll', update)
      window.removeEventListener('resize', update)
    }
  }, [])

  // 각 panel reveal observer — sticky 영역은 한 번에 마운트되어 있어 별도 in 필요
  useEffect(() => {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) e.target.classList.add(styles.panelIn)
        })
      },
      { threshold: 0.15 }
    )
    panelRefs.current.forEach((p) => p && io.observe(p))
    return () => io.disconnect()
  }, [])

  // SDLC stagger-fill — Scene 4 진입 시 6개 stage를 280 + i*360ms 마다 active.
  // 각 stage가 active되면 직전 stage는 lit으로 고정되어 connector·diamond가 채워짐.
  // 빠져나가면 모두 리셋해서 재진입 시 다시 재생.
  useEffect(() => {
    const el = sdlcRef.current
    if (!el) return undefined
    const timers = []
    function clearAll() {
      timers.forEach(clearTimeout)
      timers.length = 0
      setSdlcActive(new Set())
      setSdlcLit(new Set())
    }
    function play() {
      clearAll()
      SDLC_STAGES.forEach((_, i) => {
        const t = setTimeout(() => {
          setSdlcActive((prev) => new Set(prev).add(i))
          if (i > 0) {
            setSdlcLit((prev) => new Set(prev).add(i - 1))
          }
        }, 280 + i * 360)
        timers.push(t)
      })
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) play()
          else clearAll()
        })
      },
      { threshold: 0.35 }
    )
    io.observe(el)
    return () => {
      io.disconnect()
      timers.forEach(clearTimeout)
    }
  }, [])

  return (
    <div className={styles.page}>
      {/* ===== NAV ===== */}
      <nav className={`${styles.nav} ${navScrolled ? styles.navScrolled : ''}`}>
        <div className={styles.brand}>
          <PocoLogo height={25} />
        </div>
        <ul className={styles.navMenu}>
          <li><a href="#scene-1" onClick={(e) => handleAnchorClick(e, 'scene-1')}>서비스</a></li>
          <li><a href="#scene-3" onClick={(e) => handleAnchorClick(e, 'scene-3')}>기능</a></li>
          <li><a href="#scene-4" onClick={(e) => handleAnchorClick(e, 'scene-4')}>근거</a></li>
          <li><a href="#scene-5" onClick={(e) => handleAnchorClick(e, 'scene-5')}>사용자</a></li>
          <li><a href="/usecase" onClick={(e) => { e.preventDefault(); navigate('/usecase') }}>사용사례</a></li>
        </ul>
        <div className={styles.navRight}>
          {isLoggedIn ? (
            <button type="button" className={styles.navLogout} onClick={handleLogout}>로그아웃</button>
          ) : null}
          <button type="button" className={styles.navCta} onClick={handleStart}>시작하기</button>
        </div>

        {/* 햄버거 (좁을 때만 CSS로 표시) */}
        <button className={styles.hamburger} onClick={() => setMenuOpen(true)} aria-label="메뉴 열기">
          <HiMenu size={26} />
        </button>
      </nav>

      {/* 우측 드로어 */}
      <div
        className={`${styles.drawerOverlay} ${menuOpen ? styles.drawerOpen : ''}`}
        onClick={() => setMenuOpen(false)}
      />
      <aside className={`${styles.drawer} ${menuOpen ? styles.drawerOpen : ''}`}>
        <button className={styles.drawerClose} onClick={() => setMenuOpen(false)} aria-label="메뉴 닫기">
          <HiX size={24} />
        </button>
        <ul className={styles.drawerMenu}>
          <li><a href="#scene-1" onClick={(e) => { handleAnchorClick(e, 'scene-1'); setMenuOpen(false) }}>서비스</a></li>
          <li><a href="#scene-3" onClick={(e) => { handleAnchorClick(e, 'scene-3'); setMenuOpen(false) }}>기능</a></li>
          <li><a href="#scene-4" onClick={(e) => { handleAnchorClick(e, 'scene-4'); setMenuOpen(false) }}>근거</a></li>
          <li><a href="#scene-5" onClick={(e) => { handleAnchorClick(e, 'scene-5'); setMenuOpen(false) }}>사용자</a></li>
          <li><a href="/usecase" onClick={(e) => { e.preventDefault(); navigate('/usecase') }}>사용사례</a></li>
        </ul>
        <div className={styles.drawerActions}>
          {isLoggedIn ? <button className={styles.navLogout} onClick={() => { handleLogout(); setMenuOpen(false) }}>로그아웃</button> : null}
          <button className={styles.navCta} onClick={() => { handleStart(); setMenuOpen(false) }}>시작하기</button>
        </div>
      </aside>

      {/* ===== SCENE 1 — Opening ===== */}
      <section className={styles.scene1} id="scene-1">
        <div className={styles.scene1Inner}>
          <Reveal as="h1" className={styles.heroTitle}>
            AI가 다 만들어주는 시대,<br />
            무엇을 · 왜 만들지 정의하고 계신가요?
          </Reveal>
          <Reveal as="p" delay={1} className={styles.heroSub}>
            Poco — 조금씩, 한 걸음씩 사고를 정리해주는 AI 캔버스.
          </Reveal>
          <Reveal delay={2} className={styles.heroVis}>
            <div className={styles.heroDevice}>
              <img src={`${BASE}assets/hero-imac.png`} alt="" />
              <div className={styles.heroDisplay}>
                <HeroDemoVideo />
              </div>
            </div>
          </Reveal>
          <Reveal delay={3} className={styles.heroCtas}>
            <button type="button" className={styles.btnPrimary} onClick={handleStart}>
              시작하기
              <ArrowRight />
            </button>
            <button
              type="button"
              className={styles.btnText}
              onClick={(e) => handleAnchorClick(e, 'scene-3')}
            >
              어떻게 동작하나요?
              <ArrowDown />
            </button>
          </Reveal>
        </div>
        <div className={styles.heroMeta}>
          <span>국민대학교 AWS 분반 캡스톤</span>
          <span className={styles.heroMetaDot} />
          <span>59팀</span>
          <span className={styles.heroMetaDot} />
          <span>2026</span>
        </div>
      </section>

      {/* ===== SCENE 2 — The Quiet Question ===== */}
      <section className={styles.scene2} id="scene-2">
        <div className={styles.scene2Inner}>
          <Reveal as="p" className={styles.scene2Intro}>이런 적, 있으셨을 거예요.</Reveal>
          <div className={styles.scene2Quotes}>
            <Reveal as="p" delay={1} className={styles.scene2Q}>
              AI한테 뭐라도 시켜보려는데, 정작 내가 뭘 만들고 싶은 건지부터 모르겠다.
            </Reveal>
            <Reveal as="p" delay={2} className={styles.scene2Q}>
              용어도 어렵고, 빠뜨린 단계는 없는지 불안하다.
            </Reveal>
            <Reveal as="p" delay={3} className={styles.scene2Q}>
              왜 이 결정을 했는지, 사람들에게 설명할 자신이 없다.
            </Reveal>
          </div>
          <Reveal as="p" delay={4} className={styles.scene2Closer}>
            Poco는 그 막연함을, 다음 한 걸음으로 바꿉니다.
          </Reveal>
        </div>
      </section>

      {/* ===== SCENE 3 — Sticky Showcase ===== */}
      <section className={styles.scene3} id="scene-3">
        <Reveal className={styles.scene3Intro}>
          <h2>Poco가 하는 일</h2>
        </Reveal>
        <div className={styles.stage} ref={stageRef}>
          <div className={styles.stageInner}>
            {/* LEFT: text panels with timeline rail */}
            <div className={styles.stageText}>
              <div className={styles.timeline} aria-hidden="true">
                <div className={styles.timelineLine} />
                <div className={styles.timelineFill} style={{ height: `${railHeight}%` }} />
                <span className={styles.timelineCursor} style={{ top: `${railHeight}%` }} />
                {DOT_TOPS.map((top, i) => {
                  const stateClass =
                    i < activePanel
                      ? styles.timelineDotDone
                      : i === activePanel
                      ? styles.timelineDotCurrent
                      : ''
                  return (
                    <span
                      key={i}
                      className={`${styles.timelineDot} ${stateClass}`}
                      style={{ top: `${top}%` }}
                    />
                  )
                })}
              </div>
              {PANELS.map((panel, i) => (
                <div
                  key={i}
                  ref={(el) => { panelRefs.current[i] = el }}
                  className={styles.panel}
                >
                  <h3>{panel.title}</h3>
                  <p className={styles.panelBody}>{panel.body}</p>
                  <p className={styles.panelCaption}>{panel.caption}</p>
                </div>
              ))}
            </div>

            {/* RIGHT: pinned iMac frame */}
            <div className={styles.stageDevice}>
              <div className={styles.device}>
                <img className={styles.deviceFrame} src={`${BASE}assets/show-imac.png`} alt="" />
                <div className={styles.deviceDisplay}>
                  <div className={styles.screens}>
                    {PANELS.map((_, i) => {
                      const Fallback = [PanelScreen1, PanelScreen2, PanelScreen3, PanelScreen4][i]
                      return (
                        <div
                          key={i}
                          className={`${styles.screen} ${i === activePanel ? styles.screenActive : ''}`}
                        >
                          <DemoVideo index={i} playing={i === activePanel} fallback={Fallback} />
                        </div>
                      )
                    })}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== SCENE 4 — Foundation (SDLC diagram) ===== */}
      <section className={styles.scene4} id="scene-4">
        <div className={styles.scene4Inner}>
          <Reveal as="p" className={styles.scene4Label}>
            검증된 소프트웨어 개발 방법론 위에서
          </Reveal>
          <Reveal delay={1} className={styles.sdlc}>
            <div ref={sdlcRef} className={styles.sdlcStages} aria-label="6 Stage SDLC diagram">
              {SDLC_STAGES.map((s, i) => {
                const stageClass = [
                  styles.sdlcStage,
                  sdlcActive.has(i) ? styles.sdlcStageActive : '',
                  sdlcLit.has(i) ? styles.sdlcStageLit : '',
                ].filter(Boolean).join(' ')
                return (
                  <div key={s.num} className={stageClass}>
                    <span className={styles.sdlcNode}>{s.num}</span>
                    <span className={styles.sdlcName}>{s.name}</span>
                    <span className={styles.sdlcEn}>{s.en}</span>
                  </div>
                )
              })}
            </div>
          </Reveal>
          <Reveal as="p" delay={2} className={styles.sdlcCount}>
            <b>6 Stage</b> &nbsp;·&nbsp; <b>24 핵심 관문</b>
          </Reveal>
          <Reveal delay={3} className={styles.scene4Foot}>
            <p>
              Poco의 6단계 Stage와 24개 핵심 관문은, 미국 법무부(DOJ)의 SDLC Guidance Document를 재검토·선별하고, SWEBOK V4.0a의 토픽 구조를 참고하여 팀이 자체 설계했습니다.
            </p>
            <ol>
              <li>
                <a
                  href="https://www.justice.gov/archive/jmd/irm/lifecycle/table.htm"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  U.S. Department of Justice — SDLC Guidance Document
                </a>
              </li>
              <li>
                <a
                  href="https://www.computer.org/education/bodies-of-knowledge/software-engineering#about"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  SWEBOK V4.0a — IEEE Software Engineering Body of Knowledge
                </a>
              </li>
            </ol>
          </Reveal>
        </div>
      </section>

      {/* ===== SCENE 5 — Who Uses ===== */}
      <section className={styles.scene5} id="scene-5">
        <div className={styles.scene5Inner}>
          <Reveal as="h2">이런 분들에게 잘 맞습니다</Reveal>
          <div className={styles.scene5Cols}>
            {PERSONAS.map((p, i) => (
              <Reveal key={i} delay={i + 1} className={styles.scene5Col}>
                <span className={styles.scene5Glyph} aria-hidden="true">{p.glyph}</span>
                <h3>{p.title}</h3>
                <p>{p.body}</p>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ===== SCENE 6 — Closing ===== */}
      <section className={styles.scene6} id="scene-6">
        <div className={styles.scene6Inner}>
          <Reveal as="h2">
            조금씩, 한 걸음씩<br />
            첫 한 걸음을 시작하세요.
          </Reveal>
          <Reveal as="p" delay={1} className={styles.scene6Sub}>
            Poco는 그 답을 스스로 찾아가는 구조를 제공합니다.
          </Reveal>
          <Reveal delay={2}>
            <button type="button" className={styles.btnPrimary} onClick={handleStart}>
              시작하기
              <ArrowRight />
            </button>
          </Reveal>
        </div>
        <Reveal delay={3} className={styles.scene6Footer}>
          <p className={styles.scene6FooterTagline}>
            아이디어를 설계까지 쌓아가는 사고의 캔버스.
          </p>
          <div className={styles.scene6FooterMeta}>
            <button type="button" onClick={handleGitHub}>GitHub</button>
            <span className={styles.scene6FooterSep} />
            <span>국민대학교 캡스톤 디자인 2026 AWS Team 59</span>
          </div>
        </Reveal>
      </section>
    </div>
  )
}
