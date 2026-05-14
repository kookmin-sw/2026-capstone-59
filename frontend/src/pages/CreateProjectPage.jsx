import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { createProject } from '../api/projects'
import styles from './CreateProjectPage.module.css'

const durations = Array.from({ length: 12 }, (_, i) => i + 1)
const members = Array.from({ length: 20 }, (_, i) => i + 1)

export default function CreateProjectPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)

  const [name, setName] = useState('')
  const [memberCount, setMemberCount] = useState('')
  const [noDuration, setNoDuration] = useState(false)
  const [durationMonth, setDurationMonth] = useState('')
  const [description, setDescription] = useState('')
  const [constraints, setConstraints] = useState([])
  const [constraintInput, setConstraintInput] = useState('')
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [constraintError, setConstraintError] = useState('')

  function handleAddConstraint() {
    const trimmed = constraintInput.trim()
    if (!trimmed || constraints.includes(trimmed)) return
    if (trimmed.length > 50) { setConstraintError('제약 사항은 50자 이하로 입력해주세요.'); return }
    if (constraints.length >= 10) { setConstraintError('제약 사항은 최대 10개까지 추가할 수 있어요.'); return }
    setConstraints([...constraints, trimmed])
    setConstraintInput('')
    setConstraintError('')
  }

  function handleNext(e) {
    e.preventDefault()
    if (!memberCount) { alert('프로젝트 인원을 선택해주세요.'); return }
    if (!noDuration && !durationMonth) { alert('프로젝트 기간을 선택해주세요.'); return }
    setStep(2)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!prompt.trim()) { alert('현재 상황을 입력해주세요.'); return }
    setLoading(true)
    try {
      const project = await createProject({
        name: name.trim() || null,
        member_count: Number(memberCount),
        duration_months: noDuration ? 0 : Number(durationMonth),
        description: description.trim() || null,
        constraints: constraints.length > 0 ? constraints : null,
        prompt: prompt.trim(),
      })
      navigate(`/canvas/${project.project_id}`, { state: { projectName: project.name } })
    } catch (err) {
      alert('생성 실패: ' + (err.message ?? '알 수 없는 오류'))
    } finally {
      setLoading(false)
    }
  }

  const Logo = (
    <Link to="/projects">
      <img src="/poco-logo-text.svg" alt="poco" height={25} />
    </Link>
  )

  if (step === 1) {
    return (
      <div className={styles.page}>
        <nav className={styles.nav}>{Logo}</nav>

        <div className={styles.content}>
          <h1 className={styles.title}>
            <span className={styles.titleDark}>어떤 걸 </span>
            <span className={styles.titleLight}>만들고</span>
            <br />
            <span className={styles.titleDark}>싶으신가요? 🤔</span>
          </h1>

          <div className={styles.formWrapper}>
            <p className={styles.subtitle}>
              프로젝트 정보를 적어주세요.
              <br />
              <span className={styles.subtitleWarn}>한 번 정한 이후엔 인원·기간·제약사항을 자유롭게 바꾸기 어려워요.</span>
            </p>

            <form className={styles.form} onSubmit={handleNext}>
              {/* 이름 */}
              <div className={styles.field}>
                <label className={styles.label}>프로젝트 이름</label>
                <input
                  className={styles.input}
                  type="text"
                  maxLength={20}
                  placeholder="1 ~ 20자"
                  value={name}
                  onChange={(e) => {
                  const value = e.target.value.slice(0, 20)
                  e.target.value = value
                  setName(value)
                }}
                />
              </div>

              {/* 인원 */}
              <div className={styles.field}>
                <label className={styles.label}>프로젝트 인원 <span className={styles.required}>*</span></label>
                <select className={styles.select} required value={memberCount} onChange={(e) => setMemberCount(e.target.value)}>
                  <option value="" disabled>1 ~ 20명</option>
                  {members.map((m) => <option key={m} value={m}>{m}명</option>)}
                </select>
              </div>

              {/* 기간 */}
              <div className={styles.field}>
                <label className={styles.label}>프로젝트 기간 <span className={styles.required}>*</span></label>
                <div className={styles.durationRow}>
                  <select
                    className={styles.select}
                    required
                    disabled={noDuration}
                    value={durationMonth}
                    onChange={(e) => setDurationMonth(e.target.value)}
                  >
                    <option value="" disabled>1 ~ 12개월</option>
                    {durations.map((d) => <option key={d} value={d}>{d}개월</option>)}
                  </select>
                  <label className={styles.checkboxLabel}>
                    <input
                      type="checkbox"
                      checked={noDuration}
                      onChange={(e) => { setNoDuration(e.target.checked); if (e.target.checked) setDurationMonth('') }}
                    />
                    기간 없음
                  </label>
                </div>
              </div>

              {/* 설명 */}
              <div className={styles.field}>
                <div className={styles.labelRow}>
                  <label className={styles.label}>프로젝트 설명</label>
                  <span className={styles.charCount}>{description.length} / 100자</span>
                </div>
                <textarea
                  className={`${styles.input} ${styles.inputAutoResize}`}
                  maxLength={100}
                  placeholder="예: 배달 라이더의 경로 비효율을 해결하는 AI 모바일 앱"
                  value={description}
                  onChange={(e) => {
                  const value = e.target.value.slice(0, 100)
                  e.target.value = value
                  setDescription(value)
                  e.target.style.height = 'auto'
                  e.target.style.height = e.target.scrollHeight + 'px'
                }}
                  rows={1}
                />
                <p className={styles.hint}>💡 한 줄로 짧게! 외부에 이 프로젝트를 소개할 때 쓰는 부제 같은 거예요.</p>
              </div>

              {/* 제약 사항 */}
              <div className={styles.field}>
                <label className={styles.label}>프로젝트 제약 사항</label>
                <div className={styles.chipInputRow}>
                  <input
                    className={styles.input}
                    type="text"
                    placeholder={`예: "AWS ElastiCache 금지", "React로 제한", "AWS 크레딧 활용 가능"`}
                    value={constraintInput}
                    onChange={(e) => setConstraintInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.nativeEvent.isComposing) {
                        e.preventDefault()
                        handleAddConstraint()
                      }
                    }}
                  />
                  <button type="button" className={styles.addChipBtn} onClick={handleAddConstraint}>
                    +
                  </button>
                </div>
                {constraints.length > 0 && (
                  <div className={styles.chipList}>
                    {constraints.map((c, i) => (
                      <span key={i} className={styles.chip}>
                        {c}
                        <button
                          type="button"
                          className={styles.chipRemove}
                          onClick={() => setConstraints(constraints.filter((_, j) => j !== i))}
                        >✕</button>
                      </span>
                    ))}
                  </div>
                )}
                {constraintError && <p className={styles.errorMsg}>{constraintError}</p>}
                <p className={styles.hint}>
                  💡 이 프로젝트의 한계나 제약을 적어주세요. 시작 후엔 추가만 가능해요!<br />
                </p>
              </div>

              <div className={styles.actions}>
                <button type="submit" className={styles.btnPrimary}>다음으로 이동 →</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.page}>
      <nav className={styles.nav}>
        {Logo}
        <button type="button" className={styles.btnBack} onClick={() => setStep(1)}>
          <span>{'<'}</span> 이전으로
        </button>
      </nav>

      <div className={styles.content}>
        <h1 className={styles.title}>
          <span className={styles.titleDark}>현재 상황을 </span>
          <span className={styles.titleLight}>자유롭게</span>
          <br />
          <span className={styles.titleDark}>적어주세요!</span>
        </h1>

        <p className={styles.subtitleCenter}>상황에 맞춰 poco가 단계별 프로젝트를 설계해드릴게요.</p>

        <form className={styles.promptForm} onSubmit={handleSubmit}>
          <div className={styles.promptCard}>
            <textarea
              className={styles.promptTextarea}
              required
              maxLength={500}
              placeholder= {`예시 1) 배달 라이더의 경로 비효율 문제를 AI로 해결하는 앱을 만들고 싶어요. 아직 어떤 기술을 쓸지는 모르지만, 라이더의 시간 절약이 핵심이에요.
예시 2) 뭘 만들지 정하지 못했어요. 평소에 일정 관리가 어려워서 뭔가 도와주는 서비스가 있으면 좋겠다 정도? 친구들 4명이서 졸업작품으로 시작해보려고요.`}
              
              value={prompt}
              onChange={(e) => {
                const value = e.target.value.slice(0, 500)
                e.target.value = value
                setPrompt(value)
              }}
            />
            <div className={styles.promptActions}>
              <span className={styles.promptCounter}>{prompt.length} / 500자</span>
              <button type="submit" className={styles.createBtn} disabled={loading}>
                {loading ? '생성 중...' : '프로젝트 생성 →'}
              </button>
            </div>
          </div>

          <div className={styles.promptExamples}>
            <p className={styles.promptTip}>
              💡 친구한테 "이런 거 만들어보려고…" 하고 얘기한다 생각하고 풀어보세요. 디테일은 poco와 진행하면서 단계별로 정리해 나가요!<br />             
            </p>
          </div>
        </form>
      </div>
    </div>
  )
}