import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createProject } from '../api/projects'

const currentYear = new Date().getFullYear()
const years = Array.from({ length: 5 }, (_, i) => currentYear + i)
const months = Array.from({ length: 12 }, (_, i) => i + 1)
const members = Array.from({ length: 20 }, (_, i) => i + 1)

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

    if (nextStartYear > endYear) {
      setEndYear(nextStartYear)
    }

    if (nextStartYear === endYear && startMonth > endMonth) {
      setEndMonth(startMonth)
    }
  }

  function handleStartMonthChange(e) {
    const nextStartMonth = Number(e.target.value)
    setStartMonth(nextStartMonth)

    if (startYear === endYear && nextStartMonth > endMonth) {
      setEndMonth(nextStartMonth)
    }
  }

  function handleEndYearChange(e) {
    const nextEndYear = Number(e.target.value)
    setEndYear(nextEndYear)

    if (nextEndYear < startYear) {
      setStartYear(nextEndYear)
    }

    if (startYear === nextEndYear && endMonth < startMonth) {
      setStartMonth(endMonth)
    }
  }

  function handleEndMonthChange(e) {
    const nextEndMonth = Number(e.target.value)
    setEndMonth(nextEndMonth)

    if (startYear === endYear && nextEndMonth < startMonth) {
      setStartMonth(nextEndMonth)
    }
  }

  function handleNoDurationChange(e) {
    const checked = e.target.checked
    setNoDuration(checked)
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

    if (!memberCount) {
      alert('프로젝트 인원을 선택해주세요.')
      return
    }

    if (!noDuration && endValue < startValue) {
      alert('종료 시점은 시작 시점보다 빠를 수 없습니다.')
      return
    }

    setLoading(true)

    try {
      await createProject({
        name: name.trim() || null,
        member_count: Number(memberCount),
        duration_months: calcDurationMonths(),
        description: description.trim() || null,
        constraint: constraint.trim() || null,
        prompt: prompt.trim(),
      })

      navigate('/projects')
    } catch (err) {
      alert('생성 실패: ' + (err.message ?? '알 수 없는 오류'))
    } finally {
      setLoading(false)
    }
  }

  if (step === 1) {
    return (
      <div>
        <h1>어떤 걸 만들고 싶으신가요? 🤔</h1>
        <p>프로젝트 정보(이름, 인원, 기간 등)를 적어주세요.</p>

        <form onSubmit={handleNext}>
          <div>
            <label>프로젝트 이름</label>
            <input
              type="text"
              maxLength={20}
              placeholder="1 ~ 20자"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div>
            <label>프로젝트 인원 *</label>
            <select
              required
              value={memberCount}
              onChange={(e) => setMemberCount(e.target.value)}
            >
              <option value="">1 ~ 20명</option>
              {members.map((m) => (
                <option key={m} value={m}>
                  {m}명
                </option>
              ))}
            </select>
          </div>

          <div>
            <label>프로젝트 기간 *</label>

            <select
              disabled={noDuration}
              value={startYear}
              onChange={handleStartYearChange}
            >
              {availableStartYears.map((y) => (
                <option key={y} value={y}>
                  {y}년
                </option>
              ))}
            </select>

            <select
              disabled={noDuration}
              value={startMonth}
              onChange={handleStartMonthChange}
            >
              {availableStartMonths.map((m) => (
                <option key={m} value={m}>
                  {m}월
                </option>
              ))}
            </select>

            {' ~ '}

            <select
              disabled={noDuration}
              value={endYear}
              onChange={handleEndYearChange}
            >
              {availableEndYears.map((y) => (
                <option key={y} value={y}>
                  {y}년
                </option>
              ))}
            </select>

            <select
              disabled={noDuration}
              value={endMonth}
              onChange={handleEndMonthChange}
            >
              {availableEndMonths.map((m) => (
                <option key={m} value={m}>
                  {m}월
                </option>
              ))}
            </select>

            <label>
              <input
                type="checkbox"
                checked={noDuration}
                onChange={handleNoDurationChange}
              />
              기간 없음
            </label>
          </div>

          <div>
            <label>프로젝트 설명</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          <div>
            <label>프로젝트 제약 사항</label>
            <textarea
              value={constraint}
              onChange={(e) => setConstraint(e.target.value)}
            />
          </div>

          <button type="submit">다음으로 이동 →</button>
          <button type="button" onClick={() => navigate('/projects')}>← 뒤로</button>
        </form>
      </div>
    )
  }

  return (
    <div>
      <h1>현재 상황을 자유롭게 적어주세요!</h1>
      <p>상황에 맞춰 poco가 단계별 프로젝트를 설계해드릴게요.</p>

      <form onSubmit={handleSubmit}>
        <textarea
          required
          placeholder="예) 현재 팀원 3명이서 2개월 동안 캡스톤 프로젝트를 진행해야해. 주제는 아직 정하지 않았지만 대학생과 관련한 걸로 하고 싶어."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={8}
        />

        <button type="button" onClick={() => setStep(1)}>
          이전으로
        </button>

        <button type="submit" disabled={loading}>
          {loading ? '생성 중...' : '프로젝트 생성 →'}
        </button>
      </form>
    </div>
  )
}
