import { useState, useEffect, useRef } from 'react'
import { BsChevronDown, BsX } from 'react-icons/bs'
import styles from './ToastAlarm.module.css'

export default function ToastAlarm({
  message,
  visible,
  onToggle,
  onClose,
  showProgress = false,
  duration = 3000,
}) {
  const [show, setShow] = useState(false)
  const [fading, setFading] = useState(false)
  const [progressKey, setProgressKey] = useState(0)
  const timer = useRef(null)
  const isShown = useRef(false)

  useEffect(() => {
  if (visible) {
    clearTimeout(timer.current)
    isShown.current = true
    setTimeout(() => {
      setFading(false)
      setShow(true)
      if (showProgress) setProgressKey((k) => k + 1)
    }, 0)
  } else if (isShown.current) {
    isShown.current = false
    setTimeout(() => setFading(true), 0)
    timer.current = setTimeout(() => {
      setShow(false)
      setFading(false)
    }, 400)
  }
  return () => clearTimeout(timer.current)
}, [visible, showProgress])

  return (
    <div
      className={[
        styles.pill,
        show ? styles.pillOpen : '',
        fading ? styles.pillFading : '',
      ].join(' ')}
    >
      {showProgress && show && (
        <div
          key={progressKey}
          className={styles.progressBar}
          style={{ animationDuration: `${duration}ms` }}
        />
      )}
      <div className={styles.pillContent}>
      <button
        type="button"
        className={styles.pillToggle}
        onClick={onToggle}
        aria-expanded={show}
      >
        <span className={styles.message}>{message}</span>
        {!show && <BsChevronDown size={13} className={styles.icon} />}
      </button>
      {show && (
        <button
          type="button"
          className={styles.closeBtn}
          onClick={onClose}
          aria-label="닫기"
        >
          <BsX size={16} />
        </button>
      )}
      </div>
    </div>
  )
}