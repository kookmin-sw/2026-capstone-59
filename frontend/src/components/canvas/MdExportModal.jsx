import { useEffect, useRef, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { BsChevronDown, BsCheck } from 'react-icons/bs'
import { IoClose } from 'react-icons/io5'
import { HiOutlineQuestionMarkCircle } from 'react-icons/hi2'
import { REQUIRED_STEPS_BY_STAGE, STAGE_NAMES } from '../../utils/canvasUtils'
import { getAcceptedRequiredSteps } from '../../api/exports'
import styles from './MdExportModal.module.css'

/**
 * .md 파일로 내보내기 모달
 * - 24개 RS를 stage별로 트리뷰로 표시
 * - accept된 RS만 체크 가능, 그 외는 회색 비활성
 * - 사용자가 다운로드 버튼 클릭 시 onDownload(selectedStepIds) 호출
 */
export default function MdExportModal({ projectId, onClose, onDownload }) {
  const [accepted, setAccepted] = useState([])  // [{ step_id, name, stage_sequence }, ...]
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedIds, setSelectedIds] = useState(new Set())
  const [collapsedStages, setCollapsedStages] = useState(new Set())
  const [helpOpen, setHelpOpen] = useState(false)
  const helpRef = useRef(null)

  //accepted RS 조회
  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    getAcceptedRequiredSteps(projectId)
      .then(res => {
        if (cancelled) return
        setAccepted(res?.required_steps ?? [])
      })
      .catch(() => {
        if (cancelled) return
        setError('목록을 불러오지 못했어요.')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => { cancelled = true }
  }, [projectId])

  useEffect(() => {
    if (!helpOpen) return
    function handleClickOutside(e) {
      if (helpRef.current && !helpRef.current.contains(e.target)) {
        setHelpOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [helpOpen])

  // (stage, name) → step_id 매핑 (accept된 것만)
  const acceptedMap = useMemo(() => {
    const map = new Map()
    accepted.forEach(rs => {
      map.set(`${rs.stage_sequence}::${rs.name}`, rs.step_id)
    })
    return map
  }, [accepted])

  // stage별로 [{ name, stepId|null }] 형태로 정리
  const stages = useMemo(() => {
    return Object.entries(REQUIRED_STEPS_BY_STAGE).map(([seqStr, names]) => {
      const seq = Number(seqStr)
      const items = names.map(name => ({
        name,
        stepId: acceptedMap.get(`${seq}::${name}`) ?? null,  // null이면 비활성
      }))
      const enabledCount = items.filter(i => i.stepId).length
      return { sequence: seq, name: STAGE_NAMES[seq], items, enabledCount }
    })
  }, [acceptedMap])

  // 전체 활성 id 목록
  const allEnabledIds = useMemo(() => {
    const ids = []
    stages.forEach(s => s.items.forEach(i => { if (i.stepId) ids.push(i.stepId) }))
    return ids
  }, [stages])

  const allSelected = allEnabledIds.length > 0 && allEnabledIds.every(id => selectedIds.has(id))
  const selectedCount = selectedIds.size

  function toggleId(stepId) {
    if (!stepId) return
    setSelectedIds(prev => {
      const next = new Set(prev)
      if (next.has(stepId)) next.delete(stepId)
      else next.add(stepId)
      return next
    })
  }

  function toggleAll() {
    if (allSelected) setSelectedIds(new Set())
    else setSelectedIds(new Set(allEnabledIds))
  }

  function toggleStage(stage) {
    const stageIds = stage.items.filter(i => i.stepId).map(i => i.stepId)
    if (stageIds.length === 0) return
    const allOn = stageIds.every(id => selectedIds.has(id))
    setSelectedIds(prev => {
      const next = new Set(prev)
      if (allOn) stageIds.forEach(id => next.delete(id))
      else stageIds.forEach(id => next.add(id))
      return next
    })
  }

  function toggleCollapse(seq) {
    setCollapsedStages(prev => {
      const next = new Set(prev)
      if (next.has(seq)) next.delete(seq)
      else next.add(seq)
      return next
    })
  }

  function handleDownload() {
    if (selectedCount === 0) return
    onDownload(Array.from(selectedIds))
  }

  return (
    <div className={styles.overlay} onClick={onClose}>
      <motion.div
        className={styles.modal}
        onClick={e => e.stopPropagation()}
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.18, ease: 'easeOut' }}
      >
        {/* 헤더 */}
        <div className={styles.header}>
          <div className={styles.titleWrap}>
            <span className={styles.titleIcon}>📂</span>
            <p className={styles.title}>.md 파일로 내보내기</p>
            <div className={styles.helpWrap} ref={helpRef}>
              <button
                type="button"
                className={styles.helpBtn}
                onClick={() => setHelpOpen(v => !v)}
                aria-label="도움말"
              >
                <HiOutlineQuestionMarkCircle className={styles.helpIcon} />
              </button>
              <div className={`${styles.helpTooltip} ${helpOpen ? styles.helpTooltipOpen : ''}`}>
                선택한 필수 Step의 사고 과정을 마크다운 파일로 내려받습니다.
              </div>
            </div>
            </div>
          <button className={styles.closeBtn} onClick={onClose} aria-label="닫기">
            ✕
          </button>
        </div>

        {/* 전체 선택 + 카운트 */}
        <div className={styles.controlRow}>
          <label className={styles.selectAllLabel}>
            <Checkbox checked={allSelected} onChange={toggleAll} disabled={allEnabledIds.length === 0} />
            <span>전체 선택</span>
          </label>
          <span className={styles.count}>{selectedCount}개 선택됨</span>
        </div>

        {/* 트리뷰 */}
        <div className={styles.tree}>
          {loading && <p className={styles.placeholder}>불러오는 중...</p>}
          {error && <p className={styles.placeholderError}>{error}</p>}
          {!loading && !error && stages.map(stage => {
            const collapsed = collapsedStages.has(stage.sequence)
            const stageIds = stage.items.filter(i => i.stepId).map(i => i.stepId)
            const allStageSelected = stageIds.length > 0 && stageIds.every(id => selectedIds.has(id))
            const stageDisabled = stage.enabledCount === 0

            return (
              <div key={stage.sequence} className={styles.stageBlock}>
                <div className={`${styles.stageHeader} ${stageDisabled ? styles.disabled : ''}`}>
                  <Checkbox
                    checked={allStageSelected}
                    onChange={() => toggleStage(stage)}
                    disabled={stageDisabled}
                  />
                  <button
                    className={styles.stageToggle}
                    onClick={() => toggleCollapse(stage.sequence)}
                    type="button"
                  >
                    <BsChevronDown
                      className={`${styles.chevron} ${collapsed ? styles.chevronCollapsed : ''}`}
                      size={14}
                    />
                    <span className={styles.stageName}>
                      Stage {stage.sequence} | {stage.name}
                    </span>
                  </button>
                </div>

                {!collapsed && (
                  <ul className={styles.itemList}>
                    {stage.items.map(item => {
                      const enabled = !!item.stepId
                      const checked = enabled && selectedIds.has(item.stepId)
                      return (
                        <li
                          key={`${stage.sequence}-${item.name}`}
                          className={`${styles.item} ${enabled ? '' : styles.disabled}`}
                        >
                          <Checkbox
                            checked={checked}
                            onChange={() => toggleId(item.stepId)}
                            disabled={!enabled}
                          />
                          <span className={styles.itemName}>{item.name}</span>
                        </li>
                      )
                    })}
                  </ul>
                )}
              </div>
            )
          })}
        </div>

        {/* 푸터 */}
        <div className={styles.footer}>
          <button
            className={styles.downloadBtn}
            onClick={handleDownload}
            disabled={selectedCount === 0}
          >
            다운로드 <span className={styles.arrow}>→</span>
          </button>
        </div>
      </motion.div>
    </div>
  )
}

// 커스텀 체크박스
function Checkbox({ checked, onChange, disabled }) {
  return (
    <button
      type="button"
      onClick={disabled ? undefined : onChange}
      className={`${styles.checkbox} ${checked ? styles.checked : ''} ${disabled ? styles.checkboxDisabled : ''}`}
      disabled={disabled}
      aria-checked={checked}
      role="checkbox"
    >
      {checked && <BsCheck size={16} className={styles.checkIcon} />}
    </button>
  )
}