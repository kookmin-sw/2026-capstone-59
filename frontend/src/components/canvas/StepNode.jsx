import { Handle, Position } from '@xyflow/react'
import styles from './StepNode.module.css'

export default function StepNode({ data }) {
  const { label, status = 'READY', stageNumber, keep = false } = data

  return (
    <div className={[
      styles.wrapper,
      styles[status.toLowerCase()],
      keep ? styles.keep : '',
    ].join(' ')}>
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <span className={styles.stageNumber}>stage {stageNumber}</span>
      <div className={styles.node}>
        <p className={styles.label}>{label}</p>
      </div>
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
    </div>
  )
}