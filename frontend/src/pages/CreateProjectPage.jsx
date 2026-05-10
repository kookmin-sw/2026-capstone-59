import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { createProject } from '../api/projects'
import styles from './CreateProjectPage.module.css'

const currentYear = new Date().getFullYear()
const years = Array.from({ length: 5 }, (_, i) => currentYear + i)
const months = Array.from({ length: 12 }, (_, i) => i + 1)
const members = Array.from({ length: 10 }, (_, i) => i + 1)

function toMonthValue(year, month) {
  return year * 12 + month
}

export default function CreateProjectPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)

  const [name, setName] = useState('')
  const [memberCount, setMemberCount] = useState('')
  const [noDuration, setNoDuration] = useState(false)
  const [startYear, setStartYear] = useState(currentYear)
  const [startMonth, setStartMonth] = useState(new Date().getMonth() + 1)
  const [endYear, setEndYear] = useState(currentYear)
  const [endMonth, setEndMonth] = useState(new Date().getMonth() + 1)
  const [description, setDescription] = useState('')
  const [constraint, setConstraint] = useState('')
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)

  const startValue = toMonthValue(startYear, startMonth)
  const endValue = toMonthValue(endYear, endMonth)

  const availableStartYears = useMemo(() => {
    if (noDuration) return years
    return years.filter((year) => year <= endYear)
  }, [endYear, noDuration])

  const availableEndYears = useMemo(() => {
    if (noDuration) return years
    return years.filter((year) => year >= startYear)
  }, [startYear, noDuration])

  const availableStartMonths = useMemo(() => {
    if (noDuration) return months
    if (startYear !== endYear) return months
    return months.filter((month) => month <= endMonth)
  }, [startYear, endYear, endMonth, noDuration])

  const availableEndMonths = useMemo(() => {
    if (noDuration) return months
    if (startYear !== endYear) return months
    return months.filter((month) => month >= startMonth)
  }, [startYear, endYear, startMonth, noDuration])

  function calcDurationMonths() {
    if (noDuration) return 0
    return endValue - startValue + 1
  }

  function handleStartYearChange(e) {
    const nextStartYear = Number(e.target.value)
    setStartYear(nextStartYear)
    if (nextStartYear > endYear) setEndYear(nextStartYear)
    if (nextStartYear === endYear && startMonth > endMonth) setEndMonth(startMonth)
  }

  function handleStartMonthChange(e) {
    const nextStartMonth = Number(e.target.value)
    setStartMonth(nextStartMonth)
    if (startYear === endYear && nextStartMonth > endMonth) setEndMonth(nextStartMonth)
  }

  function handleEndYearChange(e) {
    const nextEndYear = Number(e.target.value)
    setEndYear(nextEndYear)
    if (nextEndYear < startYear) setStartYear(nextEndYear)
    if (startYear === nextEndYear && endMonth < startMonth) setStartMonth(endMonth)
  }

  function handleEndMonthChange(e) {
    const nextEndMonth = Number(e.target.value)
    setEndMonth(nextEndMonth)
    if (startYear === endYear && nextEndMonth < startMonth) setStartMonth(nextEndMonth)
  }

  function handleNoDurationChange(e) {
    setNoDuration(e.target.checked)
  }

  function handleNext(e) {
    e.preventDefault()
    if (!memberCount) {
      alert('프로젝트 인원을 선택해주세요.')
      return
    }
    if (!noDuration && endValue < startValue) {
      alert('종료 시점은 시작 시점보다 빠를 수 없습니다.')
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
        duration_months: calcDurationMonths(),
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
                  <option value="">1 ~ 10명</option>
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
                    className={`${styles.selectSmall} ${styles.selectYear}`}
                    disabled={noDuration}
                    value={startYear}
                    onChange={handleStartYearChange}
                  >
                    {availableStartYears.map((y) => (
                      <option key={y} value={y}>{y}년</option>
                    ))}
                  </select>
                  <select
                    className={`${styles.selectSmall} ${styles.selectMonth}`}
                    disabled={noDuration}
                    value={startMonth}
                    onChange={handleStartMonthChange}
                  >
                    {availableStartMonths.map((m) => (
                      <option key={m} value={m}>{m}월</option>
                    ))}
                  </select>

                  <span className={styles.separator}>~</span>

                  <select
                    className={`${styles.selectSmall} ${styles.selectYear}`}
                    disabled={noDuration}
                    value={endYear}
                    onChange={handleEndYearChange}
                  >
                    {availableEndYears.map((y) => (
                      <option key={y} value={y}>{y}년</option>
                    ))}
                  </select>
                  <select
                    className={`${styles.selectSmall} ${styles.selectMonth}`}
                    disabled={noDuration}
                    value={endMonth}
                    onChange={handleEndMonthChange}
                  >
                    {availableEndMonths.map((m) => (
                      <option key={m} value={m}>{m}월</option>
                    ))}
                  </select>

                  <label className={styles.checkboxLabel}>
                    <input
                      type="checkbox"
                      checked={noDuration}
                      onChange={handleNoDurationChange}
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