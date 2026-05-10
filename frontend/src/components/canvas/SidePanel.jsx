import { useState, useEffect, useCallback } from 'react'
import ReactMarkdown from 'react-markdown'
import { HiX, HiCheck } from 'react-icons/hi'
import styles from './SidePanel.module.css'

function NotionIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
      <path d="M4.459 4.208c.746.606 1.026.56 2.428.466l13.215-.793c.28 0 .047-.28-.046-.326L17.86 1.968c-.42-.326-.981-.7-2.055-.607L3.01 2.295c-.466.046-.56.28-.374.466zm.793 3.08v13.904c0 .747.373 1.027 1.214.98l14.523-.84c.841-.046.935-.56.935-1.167V6.354c0-.606-.233-.933-.748-.887l-15.177.887c-.56.047-.747.327-.747.933zm14.337.745c.093.42 0 .84-.42.888l-.7.14v10.264c-.608.327-1.168.514-1.635.514-.748 0-.935-.234-1.495-.933l-4.577-7.186v6.952L12.21 19s0 .84-1.168.84l-3.222.186c-.093-.186 0-.653.327-.746l.84-.233V9.854L7.822 9.76c-.094-.42.14-1.026.793-1.073l3.456-.233 4.764 7.279v-6.44l-1.215-.14c-.093-.514.28-.887.747-.933zM1.936 1.035l13.31-.98c1.634-.14 2.055-.047 3.082.7l4.249 2.986c.7.513.934.653.934 1.213v16.378c0 1.026-.373 1.634-1.68 1.726l-15.458.934c-.98.047-1.448-.093-1.962-.747l-3.129-4.06c-.56-.747-.793-1.306-.793-1.96V2.667c0-.839.374-1.54 1.447-1.632z"/>
    </svg>
  )
}

function TypewriterText({ text, speed = 13, onComplete }) {
  const [displayed, setDisplayed] = useState('')

  useEffect(() => {
    if (!text) {
      const id = setTimeout(() => onComplete?.(), 0)
      return () => clearTimeout(id)
    }
    let i = 0
    const id = setInterval(() => {
      i += 1
      if (i >= text.length) {
        clearInterval(id)
        setDisplayed(text)
        setTimeout(() => onComplete?.(), 0)
      } else {
        setDisplayed(text.slice(0, i))
      }
    }, speed)
    return () => clearInterval(id)
  }, [text, speed, onComplete])

  return <>{displayed}</>
}

function SectionSkeleton() {
  return (
    <div className={styles.mentoringSection}>
      <div className={styles.skeletonTitle} />
      <div className={styles.skeletonLine} />
      <div className={styles.skeletonLine} />
      <div className={styles.skeletonLineShort} />
    </div>
  )
}

function RevealList({ items, renderItem, onComplete, itemDelay = 100 }) {
  const [activeIndex, setActiveIndex] = useState(0)
  const [doneIndices, setDoneIndices] = useState([])

  const handleItemDone = useCallback((index) => {
    setDoneIndices(prev => [...prev, index])
    if (index + 1 >= items.length) {
      setTimeout(() => onComplete?.(), 0)
    } else {
      setTimeout(() => setActiveIndex(index + 1), itemDelay)
    }
  }, [items.length, itemDelay, onComplete])

  return (
    <>
      {items.map((item, i) => {
        if (doneIndices.includes(i)) return renderItem(item, i, false)
        if (i === activeIndex) return renderItem(item, i, true, () => handleItemDone(i))
        return null
      })}
    </>
  )
}

const LOADING_SKELETONS = [
  '📖 Step 설명',
  '👀 생각해보면 좋은 관점',
  '🎯 이 Step의 목표',
  '🔥 추천 방법',
  '💡 한 줄 팁',
]

function TitledSkeleton({ title }) {
  return (
    <div className={styles.mentoringSection}>
      <h4 className={styles.mentoringSectionTitle}>{title}</h4>
      <div className={styles.skeletonLine} />
      <div className={styles.skeletonLine} />
      <div className={styles.skeletonLineShort} />
    </div>
  )
}

function MentoringContent({ raw, isLoading, streamingText }) {
  const [revealedIndex, setRevealedIndex] = useState(-1)

  useEffect(() => {
    const reset = setTimeout(() => setRevealedIndex(-1), 0)
    if (isLoading) return () => clearTimeout(reset)
    const start = setTimeout(() => setRevealedIndex(0), 200)
    return () => { clearTimeout(reset); clearTimeout(start) }
  }, [raw, isLoading])

  const advance = useCallback(() => setRevealedIndex(prev => prev + 1), [])

  if (isLoading) {
    if (streamingText) {
      return (
        <div className={styles.markdown}>
          <ReactMarkdown>{streamingText}</ReactMarkdown>
        </div>
      )
    }
    return (
      <div className={styles.mentoringJson}>
        {LOADING_SKELETONS.map((title, i) => (
          <TitledSkeleton key={i} title={title} />
        ))}
      </div>
    )
  }

  let data = null
  if (raw && typeof raw === 'object') data = raw
  else if (typeof raw === 'string') { try { data = JSON.parse(raw) } catch { data = null } }

  if (!data) return <div className={styles.markdown}><ReactMarkdown>{raw ?? ''}</ReactMarkdown></div>

  const sections = [
    data.description && {
      key: 'desc',
      skeleton: () => <TitledSkeleton title="📖 Step 설명" />,
      active: (onComplete) => (
        <section className={styles.mentoringSection}>
          <h4 className={styles.mentoringSectionTitle}>📖 Step 설명</h4>
          <p className={styles.mentoringDescription}>
            <TypewriterText text={data.description} onComplete={onComplete} />
          </p>
        </section>
      ),
      done: () => (
        <section className={styles.mentoringSection}>
          <h4 className={styles.mentoringSectionTitle}>📖 Step 설명</h4>
          <p className={styles.mentoringDescription}>{data.description}</p>
        </section>
      ),
    },

    data.perspectives?.length > 0 && {
      key: 'persp',
      skeleton: () => <TitledSkeleton title="👀 생각해보면 좋은 관점" />,
      active: (onComplete) => (
        <section className={styles.mentoringSection}>
          <h4 className={styles.mentoringSectionTitle}>👀 생각해보면 좋은 관점</h4>
          <ul className={styles.perspectiveList}>
            <RevealList
              items={data.perspectives}
              renderItem={(p, i, isTyping, onItemDone) => (
                <li key={i} className={styles.perspectiveItem}>
                  {isTyping ? <TypewriterText text={p} onComplete={onItemDone} /> : p}
                </li>
              )}
              onComplete={onComplete}
            />
          </ul>
        </section>
      ),
      done: () => (
        <section className={styles.mentoringSection}>
          <h4 className={styles.mentoringSectionTitle}>👀 생각해보면 좋은 관점</h4>
          <ul className={styles.perspectiveList}>
            {data.perspectives.map((p, i) => <li key={i} className={styles.perspectiveItem}>{p}</li>)}
          </ul>
        </section>
      ),
    },

    data.goals?.length > 0 && {
      key: 'goals',
      skeleton: () => <TitledSkeleton title="🎯 이 Step의 목표" />,
      active: (onComplete) => (
        <section className={styles.mentoringSection}>
          <h4 className={styles.mentoringSectionTitle}>🎯 이 Step의 목표</h4>
          <ul className={styles.goalList}>
            <RevealList
              items={data.goals}
              renderItem={(g, i, isTyping, onItemDone) => (
                <li key={i} className={styles.goalItem}>
                  <span className={styles.goalCheck}>✓</span>
                  {isTyping ? <TypewriterText text={g} onComplete={onItemDone} /> : g}
                </li>
              )}
              onComplete={onComplete}
            />
          </ul>
        </section>
      ),
      done: () => (
        <section className={styles.mentoringSection}>
          <h4 className={styles.mentoringSectionTitle}>🎯 이 Step의 목표</h4>
          <ul className={styles.goalList}>
            {data.goals.map((g, i) => (
              <li key={i} className={styles.goalItem}>
                <span className={styles.goalCheck}>✓</span>{g}
              </li>
            ))}
          </ul>
        </section>
      ),
    },

    data.recommended_methods?.length > 0 && {
      key: 'methods',
      skeleton: () => <TitledSkeleton title="🔥 추천 방법" />,
      active: (onComplete) => (
        <section className={styles.mentoringSection}>
          <h4 className={styles.mentoringSectionTitle}>🔥 추천 방법</h4>
          <div className={styles.methodList}>
            <RevealList
              items={data.recommended_methods}
              itemDelay={300}
              renderItem={(m, i, isTyping, onItemDone) => (
                <div key={i} className={styles.methodItem}>
                  <p className={styles.methodTitle}>{i + 1}. {m.title}</p>
                  {isTyping
                    ? <p className={styles.methodContent}><TypewriterText text={m.content} onComplete={onItemDone} /></p>
                    : m.content.split('\n').filter(Boolean).map((line, j) => (
                        <p key={j} className={styles.methodContent}>{line}</p>
                      ))
                  }
                </div>
              )}
              onComplete={onComplete}
            />
          </div>
        </section>
      ),
      done: () => (
        <section className={styles.mentoringSection}>
          <h4 className={styles.mentoringSectionTitle}>🔥 추천 방법</h4>
          <div className={styles.methodList}>
            {data.recommended_methods.map((m, i) => (
              <div key={i} className={styles.methodItem}>
                <p className={styles.methodTitle}>{i + 1}. {m.title}</p>
                {m.content.split('\n').filter(Boolean).map((line, j) => (
                  <p key={j} className={styles.methodContent}>{line}</p>
                ))}
              </div>
            ))}
          </div>
        </section>
      ),
    },

    data.common_mistakes?.length > 0 && {
      key: 'mistakes',
      skeleton: () => <TitledSkeleton title="⚠️ 자주 하는 실수" />,
      active: (onComplete) => (
        <section className={styles.mentoringSection}>
          <h4 className={styles.mentoringSectionTitle}>⚠️ 자주 하는 실수</h4>
          <div className={styles.mistakeList}>
            <RevealList
              items={data.common_mistakes}
              itemDelay={300}
              renderItem={(m, i, isTyping, onItemDone) => (
                <div key={i} className={styles.mistakeItem}>
                  <p className={styles.mistakeTitle}>
                    {isTyping
                      ? <TypewriterText text={`${i + 1}. ${m.mistake}`} onComplete={onItemDone} />
                      : `${i + 1}. ${m.mistake}`}
                  </p>
                  {!isTyping && (m.bad_example || m.good_example) && (
                    <div className={styles.mistakeExamples}>
                      {m.bad_example && <p className={styles.mistakeBad}>❌ "{m.bad_example}"</p>}
                      {m.good_example && <p className={styles.mistakeGood}>✅ "{m.good_example}"</p>}
                    </div>
                  )}
                  {!isTyping && m.explanation && <p className={styles.mistakeExplanation}>{m.explanation}</p>}
                </div>
              )}
              onComplete={onComplete}
            />
          </div>
        </section>
      ),
      done: () => (
        <section className={styles.mentoringSection}>
          <h4 className={styles.mentoringSectionTitle}>⚠️ 자주 하는 실수</h4>
          <div className={styles.mistakeList}>
            {data.common_mistakes.map((m, i) => (
              <div key={i} className={styles.mistakeItem}>
                <p className={styles.mistakeTitle}>{i + 1}. {m.mistake}</p>
                {(m.bad_example || m.good_example) && (
                  <div className={styles.mistakeExamples}>
                    {m.bad_example && <p className={styles.mistakeBad}>❌ "{m.bad_example}"</p>}
                    {m.good_example && <p className={styles.mistakeGood}>✅ "{m.good_example}"</p>}
                  </div>
                )}
                {m.explanation && <p className={styles.mistakeExplanation}>{m.explanation}</p>}
              </div>
            ))}
          </div>
        </section>
      ),
    },

    data.one_line_tip && {
      key: 'tip',
      skeleton: () => <TitledSkeleton title="💡 한 줄 팁" />,
      active: (onComplete) => (
        <div className={styles.tipBox}>
          <span className={styles.tipTitle}>💡 한 줄 팁</span>
          <p className={styles.tipText}>
            <TypewriterText text={data.one_line_tip} onComplete={onComplete} />
          </p>
        </div>
      ),
      done: () => (
        <div className={styles.tipBox}>
          <span className={styles.tipTitle}>💡 한 줄 팁</span>
          <p className={styles.tipText}>{data.one_line_tip}</p>
        </div>
      ),
    },
  ].filter(Boolean)

  return (
    <div className={styles.mentoringJson}>
      {sections.map((section, i) => {
        if (i > revealedIndex) return <div key={section.key}>{section.skeleton()}</div>
        if (i === revealedIndex) return <div key={section.key}>{section.active(advance)}</div>
        return <div key={section.key}>{section.done()}</div>
      })}
    </div>
  )
}

export default function SidePanel({ step, detail, streamingText, isOpen, onClose, onAccept, hasChildren, isAccepting }) {
  const [activeTab, setActiveTab] = useState('mentoring')
  const [lastStep, setLastStep] = useState(step)

  useEffect(() => {
    if (step) setTimeout(() => setLastStep(step), 0)
  }, [step])

  const current = step ?? lastStep
  const status = current?.data?.status
  const isRequired = current?.data?.is_required ?? (current?.type === 'requiredStepNode')
  const name = current?.data?.label ?? ''

  const mentoring = detail?.mentoring ?? ''
  const dictionary = detail?.dictionary ?? []
  const artifact = detail?.template_url ? { notion_template_url: detail.template_url } : null

  const tabs = isRequired
    ? ['mentoring', 'dictionary', 'template']
    : ['mentoring', 'dictionary']

  const tabLabels = {
    mentoring: 'AI Mentoring',
    dictionary: 'Dictionary',
    template: 'Template',
  }

  return (
    <div className={`${styles.panel} ${isOpen ? styles.panelOpen : ''} ${isRequired ? styles.requiredPanel : ''}`}>
      <div className={styles.header}>
        <span className={styles.stepDetails}>STEP DETAILS</span>
        <button className={styles.closeBtn} onClick={onClose}>
          <HiX size={18} />
        </button>
      </div>

      <div className={styles.titleSection}>
        <h2 className={styles.stepName}>{name}</h2>
        {isRequired && <span className={styles.requiredBadge}>필수 STEP</span>}
      </div>

      <div className={styles.tabs}>
        {tabs.map((tab) => (
          <button
            key={tab}
            className={`${styles.tab} ${activeTab === tab ? styles.activeTab : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tabLabels[tab]}
          </button>
        ))}
      </div>

      <div className={styles.content}>
        {activeTab === 'mentoring' && (
          <MentoringContent raw={mentoring} isLoading={!detail} streamingText={streamingText}/>
        )}

        {activeTab === 'dictionary' && (
          <div className={styles.dictionaryList}>
            {!detail
              ? [...Array(4)].map((_, i) => <SectionSkeleton key={i} />)
              : dictionary.map((item, i) => (
                  <div key={i} className={styles.dictionaryItem}>
                    <p className={styles.dictionaryTerm}>{item.term}</p>
                    <p className={styles.dictionaryDefinition}>{item.definition}</p>
                  </div>
                ))
            }
          </div>
        )}

        {activeTab === 'template' && (
          <div className={styles.templateTab}>
            <p className={styles.templateIntro}>
              이 단계의 산출물인 템플릿이 준비되어 있어요.<br />
              Notion에서 바로 작성을 시작할 수 있어요.
            </p>
            {artifact ? (
              <div className={styles.templateCard}>
                <div className={styles.templateCardTop}>
                  <span>📄</span>
                  <span className={styles.templateCardTitle}>{name}</span>
                </div>
                <a
                  href={artifact.notion_template_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={styles.notionBtn}
                >
                  <NotionIcon size={16} />
                  Notion에서 템플릿 열기
                </a>
                <p className={styles.templateHint}>
                  작성한 내용을 Poco에 제출할 필요는 없어요.<br />
                  Notion에서 복제 후 자유롭게 활용하세요!
                </p>
              </div>
            ) : (
              <p className={styles.templateHint}>템플릿을 불러오는 중이에요.</p>
            )}
          </div>
        )}
      </div>

      <div className={styles.footer}>
        {(status !== 'ACCEPTED' || !hasChildren) && (
          <button className={styles.acceptBtn} onClick={onAccept} disabled={isAccepting}>
            <HiCheck size={15} />
            accept
          </button>
        )}
      </div>
    </div>
  )
}