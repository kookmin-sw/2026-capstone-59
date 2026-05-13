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
  const [description, setDescription] = useState('')
  const [constraint, setConstraint] = useState('')
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [durationMonth, setDurationMonth] = useState('')


  function handleNext(e) {
    e.preventDefault()
    if (!memberCount) {
      alert('프로젝트 인원을 선택해주세요.')
      return
    }
    if (!noDuration && !durationMonth) {
      alert('프로젝트 기간을 선택해주세요.')
      return
    }
    setStep(2)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!prompt.trim()) {
      alert('현재 상황을 입력해주세요.')
      return
      
    }
    setLoading(true)
    try {
      const project = await createProject({
        name: name.trim() || null,
        member_count: Number(memberCount),
        duration_months: noDuration ? 0 : Number(durationMonth),
        description: description.trim() || null,
        constraint: constraint.trim() || null,
        prompt: prompt.trim(),
      })
      navigate(`/canvas/${project.project_id}`, { state: { projectName: name.trim() || 'Project' } })

    } catch (err) {
      alert('생성 실패: ' + (err.message ?? '알 수 없는 오류'))
    } finally {
      setLoading(false)
    }
  }

  const Logo = (
    <Link to="/projects">
      <div className={styles.logo}>
        <span>poco</span>
      </div>
    </Link>
  )

  if (step === 1) {
    return (
      <div className={styles.page}>
        <nav className={styles.nav}>
          {Logo}
        </nav>

        <div className={styles.content}>
          <h1 className={styles.title}>
            <span className={styles.titleDark}>어떤 걸 </span>
            <span className={styles.titleLight}>만들고</span>
            <br />
            <span className={styles.titleDark}>싶으신가요? 🤔</span>
          </h1>

          <div className={styles.formWrapper}>
            <p className={styles.subtitle}>프로젝트 정보(이름, 인원, 기간 등)를 적어주세요.</p>

            <form className={styles.form} onSubmit={handleNext}>
              <div className={styles.field}>
                <label className={styles.label}>프로젝트 이름</label>
                <input
                  className={styles.input}
                  type="text"
                  maxLength={20}
                  placeholder="1 ~ 20자"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>

              <div className={styles.field}>
                <label className={styles.label}>
                  프로젝트 인원 <span className={styles.required}>*</span>
                </label>
                <select
                  className={styles.select}
                  required
                  value={memberCount}
                  onChange={(e) => setMemberCount(e.target.value)}
                >
                  <option value="" disabled>
                    1 ~ 20명
                  </option>
                  {members.map((m) => (
                    <option key={m} value={m}>{m}명</option>
                  ))}
                </select>
              </div>

              <div className={styles.field}>
                <label className={styles.label}>
                  프로젝트 기간 <span className={styles.required}>*</span>
                </label>
                <div className={styles.durationRow}>
                  <select
                    className={styles.select}
                    disabled={noDuration}
                    value={durationMonth}
                    onChange={(e) => setDurationMonth(e.target.value)}
                  >
                    <option value="" disabled>
                      1 ~ 12개월
                    </option>
                    {durations.map((d) => (
                      <option key={d} value={d}>{d}개월</option>
                    ))}
                  </select>
                  <label className={styles.checkboxLabel}>
                    <input
                      type="checkbox"
                      checked={noDuration}
                      onChange={(e) => {
                        setNoDuration(e.target.checked)
                        if (e.target.checked) setDurationMonth('')
                      }}
                    />
                    기간 없음
                  </label>
                </div>
              </div>

              <div className={styles.field}>
                <label className={styles.label}>프로젝트 설명</label>
                <textarea
                  className={styles.textarea}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>

              <div className={styles.field}>
                <label className={styles.label}>프로젝트 제약 사항</label>
                <textarea
                  className={styles.textarea}
                  value={constraint}
                  onChange={(e) => setConstraint(e.target.value)}
                />
              </div>

              <div className={styles.actions}>
                <button type="submit" className={styles.btnPrimary}>
                  다음으로 이동 →
                </button>
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
        <button
          type="button"
          className={styles.btnBack}
          onClick={() => setStep(1)}
        >
          
          <span> {'<'} </span> 이전으로
        </button>
      </nav>

      <div className={styles.content}>
        <h1 className={styles.title}>
          <span className={styles.titleDark}>현재 상황을 </span>
          <span className={styles.titleLight}>자유롭게</span>
          <br />
          <span className={styles.titleDark}>적어주세요!</span>
        </h1>

        <p className={styles.subtitleCenter}>
          상황에 맞춰 poco가 단계별 프로젝트를 설계해드릴게요.
        </p>

        <form className={styles.promptForm} onSubmit={handleSubmit}>
          <div className={styles.promptCard}>
            <textarea
              className={styles.promptTextarea}
              required
              placeholder="예) 현재 팀원 3명이서 2개월 동안 캡스톤 프로젝트를 진행해야해. 주제는 아직 정하지 않았지만 대학생과 관련한 걸로 하고 싶어."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
            <div className={styles.promptActions}>
              <button
                type="submit"
                className={styles.createBtn}
                disabled={loading}
              >
                {loading ? '생성 중...' : '프로젝트 생성 →'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}