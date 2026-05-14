import { Handle, Position } from '@xyflow/react'
import styles from './RequiredStepNode.module.css'

export default function RequiredStepNode({ data }) {
  const { label, status } = data

  return (
    <div className={styles.wrapper}>
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <div className={styles.diamondWrap}>
        <div className={`${styles.diamond} ${status === 'ACCEPTED' ? styles.accepted : ''}`} />
      </div>
      <span className={styles.label}>{label}</span>
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
    </div>
  )
}