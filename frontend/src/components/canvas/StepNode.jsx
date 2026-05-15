import { Handle, Position } from '@xyflow/react'
import { motion } from 'framer-motion'
import styles from './StepNode.module.css'

export default function StepNode({ data }) {
  const { label, status = 'READY', stageNumber, keep = false, isNew = false } = data

  return (
    <div className={[styles.wrapper, styles[status.toLowerCase()], keep ? styles.keep : ''].join(' ')}>
      <Handle type="target" position={Position.Left} style={{ opacity: 0, left: 3, top: '60%' }} />
      {status === 'ACCEPTED' && <div className={styles.dot} />}
      <span className={styles.stageNumber}>stage {stageNumber}</span>
      <div className={styles.node}>
        <p className={styles.label}>{label}</p>
      </div>
      <Handle type="source" position={Position.Right} style={{ opacity: 0, right: 3, top: '60%' }} />
    </div>
  )
}