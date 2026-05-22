import { Handle, Position } from '@xyflow/react'
import { motion } from 'framer-motion'
import styles from './RequiredStepNode.module.css'

export default function RequiredStepNode({ data }) {
  const {
    label,
    status,
    isNew = false,
    isExiting = false,
    isReparented = false,
    // accept 응답에 required 가 새로 포함되어 옆에서 밀고 들어오는 단계
    isPushingIn = false,
    // phase A 단계에서는 마운트만 되고 시각적으로는 숨김 (phase B 에서 isPushingIn 으로 전환)
    isWaiting = false,
  } = data

  const shouldGrow = isNew || isReparented

  // 우선순위:
  //   isExiting > isWaiting > isPushingIn > shouldGrow > idle
  let initial = false
  let animate = { opacity: 1, scale: 1, x: 0 }
  let transition = { duration: 0.45, ease: 'easeOut' }

  if (isWaiting) {
    // phase A — required 는 아직 자리만 잡고 숨김
    initial = { opacity: 0, scale: 0.95, x: 80 }
    animate = { opacity: 0, scale: 0.95, x: 80 }
    transition = { duration: 0 }
  } else if (isExiting) {
    animate = { opacity: 0, scale: 0.95, x: 0 }
    transition = { duration: 0.3, ease: 'easeOut' }
  } else if (isPushingIn) {
    // 우측에서 슬라이드 + 살짝 펄스
    initial = { opacity: 0, scale: 0.9, x: 80 }
    animate = { opacity: [0, 1, 1], scale: [0.9, 1.1, 1], x: [80, -6, 0] }
    transition = {
      duration: 0.55,
      times: [0, 0.6, 1],
      ease: 'easeOut',
    }
  } else if (shouldGrow) {
    initial = { opacity: 0, scale: 1.0 }
    animate = { opacity: [0, 1, 1], scale: [1.0, 1.1, 1.0] }
    transition = {
      duration: 0.45,
      times: [0, 0.5, 1],
      ease: 'easeOut',
    }
  }

  return (
    <motion.div
      className={styles.wrapper}
      initial={initial}
      animate={animate}
      transition={transition}
    >
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <div className={styles.diamondWrap}>
        <div className={`${styles.diamond} ${status === 'ACCEPTED' ? styles.accepted : ''}`} />
      </div>
      <span className={styles.label}>{label}</span>
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
    </motion.div>
  )
}
