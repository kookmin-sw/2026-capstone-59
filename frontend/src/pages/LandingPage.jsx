import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getMe, logout } from '../api/auth'
import styles from './LandingPage.module.css'

// ===== Static copy (Claude Design 결과 그대로 박제) =====
const PANELS = [
  {
    title: '다음 한 걸음을, AI가 제안합니다.',
    body: '검증된 소프트웨어 개발 방법론의 6단계 프로세스를 따라 노드가 동적으로 뻗어나갑니다. 각 단계의 핵심 관문은 다이아몬드 노드로 자연스럽게 나타납니다.',
    caption: '막연함을 다음 한 걸음으로.',
    screenLabel: 'Step Flow 캔버스 화면',
  },
  {
    title: '노드를 클릭하면, 사이드패널이 펼쳐집니다.',
    body: '해당 단계의 멘토링과 용어 사전이 함께 보이고, 핵심 관문에 도달하면 팀이 설계한 노션 템플릿이 연결됩니다.',
    caption: '딱딱한 방법론 대신, 맥락에 맞는 가이드가 곁에.',
    screenLabel: '사이드패널이 펼쳐진 화면',
  },
  {
    title: '아이디어가 흔들려도 괜찮습니다.',
    body: '이전 분기점으로 돌아가면 AI가 바뀐 맥락에 맞춰 새 길을 제안합니다. 모든 선택의 궤적이 캔버스에 트리로 남습니다.',
    caption: '되돌아갈 수 있는 선택, 자산으로 남는 사고 과정.',
    screenLabel: 'Footprint 트리 분기 화면',
  },
  {
    title: '사고가 정리되면, 외부 AI에 그대로 넘기세요.',
    body: '의사결정 궤적이 .md 한 장으로 추출됩니다. Claude · ChatGPT · Cursor 어디든 첨부할 수 있습니다.',
    caption: '외부 AI와 자연스럽게 이어지는 다리.',
    screenLabel: '다운로드 모달 + .md 미리보기',
  },
]

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
          <span className={styles.brandDot} aria-hidden="true" />
          <span>Poco</span>
        </div>
        <ul className={styles.navMenu}>
          <li><a href="#scene-3" onClick={(e) => handleAnchorClick(e, 'scene-3')}>기능</a></li>
          <li><a href="#scene-4" onClick={(e) => handleAnchorClick(e, 'scene-4')}>근거</a></li>
          <li><a href="#scene-5" onClick={(e) => handleAnchorClick(e, 'scene-5')}>사용자</a></li>
        </ul>
        <div className={styles.navRight}>
          {isLoggedIn ? (
            <button type="button" className={styles.navLogout} onClick={handleLogout}>로그아웃</button>
          ) : null}
          <button type="button" className={styles.navCta} onClick={handleStart}>시작하기</button>
        </div>
      </nav>

      {/* ===== SCENE 1 — Opening ===== */}
      <section className={styles.scene1} id="scene-1">
        <div className={styles.scene1Inner}>
          <Reveal as="h1" className={styles.heroTitle}>
            AI가 다 만들어주는 시대,<br />
            무엇을·왜 만들지 정의하고 계신가요?
          </Reveal>
          <Reveal as="p" delay={1} className={styles.heroSub}>
            Poco — 조금씩, 한 걸음씩 사고를 정리해주는 AI 캔버스.
          </Reveal>
          <Reveal delay={2} className={styles.heroVis}>
            <img src="/assets/hero-imac.png" alt="" />
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
          <span>59팀 · 2026</span>
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
                <img className={styles.deviceFrame} src="/assets/show-imac.png" alt="" />
                <div className={styles.deviceDisplay}>
                  <div className={styles.screens}>
                    {PANELS.map((panel, i) => (
                      <div
                        key={i}
                        className={`${styles.screen} ${i === activePanel ? styles.screenActive : ''}`}
                      >
                        <div className={styles.ph}>
                          <span className={styles.phLabel}>{panel.screenLabel}</span>
                        </div>
                      </div>
                    ))}
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
              <li>U.S. Department of Justice — SDLC Guidance Document</li>
              <li>SWEBOK V4.0a — IEEE Software Engineering Body of Knowledge</li>
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
          <button type="button" onClick={handleGitHub}>GitHub</button>
          <span className={styles.scene6FooterSep} />
          <span>© 2026 국민대학교 AWS 분반 캡스톤 59팀</span>
        </Reveal>
      </section>
    </div>
  )
}
