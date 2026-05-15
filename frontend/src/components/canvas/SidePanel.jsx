import { useState, useEffect, useRef } from 'react'
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

function TypewriterText({ text, className, speed = 12, onComplete }) {
  const [displayedLen, setDisplayedLen] = useState(0)
  const textRef = useRef(text)
  const onCompleteRef = useRef(onComplete)
  const completedRef = useRef(false)

  useEffect(() => {
    textRef.current = text
    completedRef.current = false
  }, [text])

  useEffect(() => { onCompleteRef.current = onComplete }, [onComplete])

  useEffect(() => {
    completedRef.current = false

    const interval = setInterval(() => {
      setDisplayedLen(prev => {
        const chars = Array.from(textRef.current)
        if (prev < chars.length) {
          const next = prev + 1
          if (next >= chars.length && !completedRef.current) {
            completedRef.current = true
            setTimeout(() => onCompleteRef.current?.(), 0)
          }
          return next
        }
        return prev
      })
    }, speed)

    return () => clearInterval(interval)
  }, [speed])

  const displayed = Array.from(text).slice(0, displayedLen).join('')
  return <p className={className}>{displayed}</p>
}

function parseStreamingMentoring(text) {
  if (!text) return {}
  try { return JSON.parse(text) } catch {
    //
  }

  const result = {}

  function extractString(key) {
    const re = new RegExp(`"${key}"\\s*:\\s*"((?:[^"\\\\]|\\\\.)*)"`)
    const m = text.match(re)
    return m ? m[1].replace(/\\n/g, '\n').replace(/\\"/g, '"') : undefined
  }

  function extractArray(key) {
    const re = new RegExp(`"${key}"\\s*:\\s*\\[`)
    const m = text.match(re)
    if (!m) return undefined
    const start = m.index + m[0].length - 1
    let depth = 0, inString = false, i = start
    while (i < text.length) {
      const c = text[i]
      if (inString) {
        if (c === '\\') { i += 2; continue }
        if (c === '"') inString = false
      } else {
        if (c === '"') inString = true
        else if (c === '[') depth++
        else if (c === ']') {
          depth--
          if (depth === 0) {
            try { return JSON.parse(text.slice(start, i + 1)) } catch { return undefined }
          }
        }
      }
      i++
    }
    const items = []
    let j = start + 1  // '[' 다음부터
    while (j < text.length) {
      while (j < text.length && /\s/.test(text[j])) j++
      if (text[j] !== '{') break
      let objDepth = 0, inStr = false, k = j
      while (k < text.length) {
        const ch = text[k]
        if (inStr) {
          if (ch === '\\') { k += 2; continue }
          if (ch === '"') inStr = false
        } else {
          if (ch === '"') inStr = true
          else if (ch === '{') objDepth++
          else if (ch === '}') {
            objDepth--
            if (objDepth === 0) {
              try {
                items.push(JSON.parse(text.slice(j, k + 1)))
                j = k + 1
                while (j < text.length && /[\s,]/.test(text[j])) j++
              } catch { return items.length > 0 ? items : undefined }
              break
            }
          }
        }
        k++
      }
      if (objDepth > 0) break
    }
    return items.length > 0 ? items : undefined
  }

  result.description = extractString('description')
  result.recommended_methods = extractArray('recommended_methods')
  result.common_mistakes = extractArray('common_mistakes')
  result.one_line_tip = extractString('one_line_tip')

  Object.keys(result).forEach(k => { if (result[k] === undefined) delete result[k] })
  return result
}

function DotsLoading({ text = '템플릿을 불러오는 중이에요' }) {
  return (
    <p className={styles.templateLoading}>
      {text}
      <span className={styles.bounceDots}>
        <span></span>
        <span></span>
        <span></span>
      </span>
    </p>
  )
}

function MethodListTyping({ items }) {
  const [typingIndex, setTypingIndex] = useState(0)
  const [doneIndex, setDoneIndex] = useState(-1)

  const handleComplete = () => {
    setDoneIndex(typingIndex)
    if (typingIndex < items.length - 1) {
      setTimeout(() => setTypingIndex(t => t + 1), 150)
    }
  }

  return (
    <div className={styles.methodList}>
      {items.slice(0, typingIndex + 1).map((m, i) => (
        <div key={i} className={styles.methodItem}>
          {i < typingIndex ? (
            <>
              <p className={styles.methodTitle}>{i + 1}. {m.title}</p>
              {m.content.split('\n').filter(Boolean).map((line, j) => (
                <p key={j} className={styles.methodContent}>{line}</p>
              ))}
            </>
          ) : (
            <>
              <TypewriterText
                key={`method-${i}`}
                text={`${i + 1}. ${m.title}`}
                className={styles.methodTitle}
                onComplete={handleComplete}
              />
              {doneIndex >= i && m.content.split('\n').filter(Boolean).map((line, j) => (
                <p key={j} className={styles.methodContent}>{line}</p>
              ))}
            </>
          )}
        </div>
      ))}
    </div>
  )
}

function MistakeListTyping({ items }) {
  const [typingIndex, setTypingIndex] = useState(0)
  const [doneIndex, setDoneIndex] = useState(-1)

  const handleComplete = () => {
    setDoneIndex(typingIndex)
    if (typingIndex < items.length - 1) {
      setTimeout(() => setTypingIndex(t => t + 1), 150)
    }
  }

  return (
    <div className={styles.mistakeList}>
      {items.slice(0, typingIndex + 1).map((m, i) => (
        <div key={i} className={styles.mistakeItem}>
          {i < typingIndex ? (
            <>
              <p className={styles.mistakeTitle}>{i + 1}. {m.mistake}</p>
              {(m.bad_example || m.good_example) && (
                <div className={styles.mistakeExamples}>
                  {m.bad_example && <p className={styles.mistakeBad}>❌ "{m.bad_example}"</p>}
                  {m.good_example && <p className={styles.mistakeGood}>✅ "{m.good_example}"</p>}
                </div>
              )}
              {m.explanation && <p className={styles.mistakeExplanation}>{m.explanation}</p>}
            </>
          ) : (
            <>
              <TypewriterText
                key={`mistake-${i}`}
                text={`${i + 1}. ${m.mistake}`}
                className={styles.mistakeTitle}
                onComplete={handleComplete}
              />
              {doneIndex >= i && (
                <>
                  {(m.bad_example || m.good_example) && (
                    <div className={styles.mistakeExamples}>
                      {m.bad_example && <p className={styles.mistakeBad}>❌ "{m.bad_example}"</p>}
                      {m.good_example && <p className={styles.mistakeGood}>✅ "{m.good_example}"</p>}
                    </div>
                  )}
                  {m.explanation && <p className={styles.mistakeExplanation}>{m.explanation}</p>}
                </>
              )}
            </>
          )}
        </div>
      ))}
    </div>
  )
}

function StreamingStructuredView({ data }) {
  return (
    <div className={styles.mentoringJson}>
      {data.description
        ? <section className={`${styles.mentoringSection} ${styles.fadeInSection}`}>
            <h4 className={styles.mentoringSectionTitle}>📖 Step 설명</h4>
            <p className={styles.mentoringDescription}>{data.description}</p>
          </section>
        : <TitledSkeleton title="📖 Step 설명" />}

      {data.recommended_methods?.length > 0
        ? <section className={`${styles.mentoringSection} ${styles.fadeInSection}`}>
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
        : <TitledSkeleton title="🔥 추천 방법" />}

      {data.common_mistakes?.length > 0
        ? <section className={`${styles.mentoringSection} ${styles.fadeInSection}`}>
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
        : <TitledSkeleton title="⚠️ 자주 하는 실수" />}

      {data.one_line_tip
        ? <div className={`${styles.tipBox} ${styles.fadeInSection}`}>
            <span className={styles.tipTitle}>💡 한 줄 팁</span>
            <p className={styles.tipText}>{data.one_line_tip}</p>
          </div>
        : <TitledSkeleton title="💡 한 줄 팁" />}
    </div>
  )
}

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

function AllSkeleton() {
  return (
    <div className={styles.mentoringJson}>
      <TitledSkeleton title="📖 Step 설명" />
      <TitledSkeleton title="🔥 추천 방법" />
      <TitledSkeleton title="⚠️ 자주 하는 실수" />
      <TitledSkeleton title="💡 한 줄 팁" />
    </div>
  )
}

function MentoringContent({ raw, isLoading, streamingText, isRequired }) {
  if (isLoading && !streamingText) {
    return <AllSkeleton />
  }

  if (streamingText) {
    const partialData = parseStreamingMentoring(streamingText)
    return <StreamingStructuredView data={partialData} />
  }

  let data = null
  if (raw && typeof raw === 'object') data = raw
  else if (typeof raw === 'string') { try { data = JSON.parse(raw) } catch {
    //
  } }

  if (!data) return <div className={styles.markdown}><ReactMarkdown>{raw ?? ''}</ReactMarkdown></div>

  return (
    <div className={styles.mentoringJson}>
      {data.description && (
        <section className={styles.mentoringSection}>
          <h4 className={styles.mentoringSectionTitle}>📖 Step 설명</h4>
          <p className={styles.mentoringDescription}>{data.description}</p>
        </section>
      )}
            {isRequired ? (
        <>
          {data.perspectives?.length > 0 && (
            <section className={styles.mentoringSection}>
              <h4 className={styles.mentoringSectionTitle}>👀 생각해보면 좋은 관점</h4>
              <ul className={styles.perspectiveList}>
                {data.perspectives.map((p, i) => <li key={i} className={styles.perspectiveItem}>{p}</li>)}
              </ul>
            </section>
          )}
          {data.goals?.length > 0 && (
            <section className={styles.mentoringSection}>
              <h4 className={styles.mentoringSectionTitle}>🎯 이 Step의 목표</h4>
              <ul className={styles.goalList}>
                {data.goals.map((g, i) => (
                  <li key={i} className={styles.goalItem}><span className={styles.goalCheck}>✓</span>{g}</li>
                ))}
              </ul>
            </section>
          )}
        </>
      ) : (
        data.recommended_methods?.length > 0 && (
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
        )
      )}
      {data.common_mistakes?.length > 0 && (
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
      )}
      {data.one_line_tip && (
        <div className={styles.tipBox}>
          <span className={styles.tipTitle}>💡 한 줄 팁</span>
          <p className={styles.tipText}>{data.one_line_tip}</p>
        </div>
      )}
    </div>
  )
}

export default function SidePanel({ step, detail, streamingText, isOpen, onClose, onAccept, hasChildren, isAccepting }) {
  const [lastStep, setLastStep] = useState(step)
  const [activeTab, setActiveTab] = useState('mentoring')
  const [tabStepId, setTabStepId] = useState(step?.id)

  if (step?.id !== tabStepId) {
    setTabStepId(step?.id)
    setActiveTab('mentoring')
  }

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
        <div style={{ display: activeTab === 'mentoring' ? 'block' : 'none' }}>
          <MentoringContent raw={mentoring} isLoading={!detail} streamingText={streamingText} isRequired={isRequired} />
        </div>

        <div style={{ display: activeTab === 'dictionary' ? 'block' : 'none' }}>
          <div className={styles.dictionaryList}>
            {!detail
              ? [...Array(3)].map((_, i) => (
                  <div key={i} className={styles.dictionaryItem}>
                    <div className={styles.skeletonTitle} />
                    <div className={styles.skeletonLine} />
                  </div>
                ))
              : dictionary.map((item, i) => (
                  <div key={i} className={styles.dictionaryItem}>
                    <p className={styles.dictionaryTerm}>{item.term}</p>
                    <p className={styles.dictionaryDefinition}>{item.definition}</p>
                  </div>
                ))
            }
          </div>
        </div>

        <div style={{ display: activeTab === 'template' ? 'block' : 'none' }}>
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
                  <NotionIcon size={18} />
                  Notion에서 템플릿 열기
                </a>
                <p className={styles.templateHint}>
                  작성한 내용을 Poco에 제출할 필요는 없어요.<br />
                  Notion에서 복제 후 자유롭게 활용하세요!
                </p>
              </div>
            ) : (
              <DotsLoading />
            )}
          </div>
        </div>
      </div>

      <div className={styles.footer}>
        {(status !== 'ACCEPTED' && !hasChildren && onAccept) && (
          <button className={styles.acceptBtn} onClick={onAccept} disabled={isAccepting}>
            <HiCheck size={15} />
            accept
          </button>
        )}
      </div>
    </div>
  )
}