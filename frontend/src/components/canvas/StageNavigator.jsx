import { useState } from 'react'
import { BsChevronLeft, BsChevronRight, BsCheckLg } from 'react-icons/bs'
import styles from './StageNavigator.module.css'

export default function StageNavigator({
  stages,
  currentStageId,
  selectedStageId,
  onSelectStage,
  collapsed,
  onToggle,
}) {
  const [visible, setVisible] = useState(true)

  function handleToggle() {
    setVisible(false)
    setTimeout(() => {
      onToggle()
      setTimeout(() => setVisible(true), 10)
    }, 100)
  }

  return (
    <aside
      className={`${styles.nav} ${collapsed ? styles.collapsed : ''}`}
      style={{
        opacity: visible ? 1 : 0,
        transition: 'opacity 0.8s ease',
      }}
    >
      <div className={styles.header}>
        {!collapsed && <span className={styles.title}>STAGES</span>}
        <button className={styles.toggleBtn} onClick={handleToggle}>
          {collapsed ? <BsChevronRight size={12} /> : <BsChevronLeft size={12} />}
        </button>
      </div>

      <ul className={styles.list}>
        {stages.map((stage) => {
          const isCurrent = stage.id === currentStageId
          const isSelected = stage.id === selectedStageId
          const isCompleted = stage.status === 'completed'
          const isLocked = stage.status === 'locked'
          const isClickable = !isLocked

          const badgeClass = isCompleted
            ? styles.badgeCompleted
            : isCurrent
            ? styles.badgeActive
            : styles.badge

          return (
            <li
              key={stage.id}
              className={[
                styles.item,
                isSelected ? styles.selected : '',
                isCurrent ? styles.current : '',
                isCompleted ? styles.completed : '',
                isLocked ? styles.locked : '',
              ].join(' ')}
              onClick={() => isClickable && onSelectStage(stage.id)}
            >
              <div className={`${styles.badge} ${badgeClass}`}>
                {isCompleted ? <BsCheckLg size={11} /> : stage.sequence}
              </div>
              {!collapsed && (
                <div className={styles.stageInfo}>
                  <span className={styles.stageName}>{stage.name}</span>
                  <span className={styles.stageEnglish}>{stage.englishName}</span>
                </div>
              )}
            </li>
          )
        })}
      </ul>
    </aside>
  )
}