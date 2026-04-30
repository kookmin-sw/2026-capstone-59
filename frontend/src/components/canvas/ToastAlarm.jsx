import { useState, useEffect, useRef } from 'react'
import { BsChevronDown } from 'react-icons/bs'
import styles from './ToastAlarm.module.css'

export default function ToastAlarm({ message, visible, onToggle }) {
  const [show, setShow] = useState(false)
  const [fading, setFading] = useState(false)
  const timer = useRef(null)
  const isShown = useRef(false)

  useEffect(() => {
  if (visible) {
    clearTimeout(timer.current)
    isShown.current = true
    setTimeout(() => {
      setFading(false)
      setShow(true)
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
}, [visible])

  return (
    <button
      type="button"
      className={[
        styles.pill,
        show ? styles.pillOpen : '',
        fading ? styles.pillFading : '',
      ].join(' ')}
      onClick={onToggle}
      aria-expanded={show}
    >
      <span className={styles.message}>{message}</span>
      {!show && <BsChevronDown size={13} className={styles.icon} />}
    </button>
  )
}
