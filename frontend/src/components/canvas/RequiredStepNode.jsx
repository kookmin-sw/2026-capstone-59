import { Handle, Position } from '@xyflow/react'
import { motion } from 'framer-motion'
import styles from './RequiredStepNode.module.css'

export default function RequiredStepNode({ data }) {
  const { label, status, isNew = false, isExiting = false, isRearented = false } = data

  const shouldGrow = isNew || isRearented

  return (
    <motion.div
      className={styles.wrapper}
      initial={shouldGrow ? { opacity: 0, scale: 1.0 } : false}
      animate={
        isExiting
          ? { opacity: 0, scale: 0.95 }
          : shouldGrow
            ? { opacity: [0, 1, 1], scale: [1.0, 1.1, 1.0] }
            : {opacity : 1, scale: 1.0 }
      }
      transition={{
        duration: isExiting ? 0.3 : 0.45,
        times: shouldGrow && !isExiting ? [0, 0.5, 1] : undefined,
        ease: 'easeOut',
      }}
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