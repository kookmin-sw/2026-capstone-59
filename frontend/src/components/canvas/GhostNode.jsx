import { Handle, Position } from '@xyflow/react'
import { motion } from 'framer-motion'
import styles from './GhostNode.module.css'

export default function GhostNode({ data }) {
  const { isExiting = false } = data

  return (
    <motion.div
      className={styles.wrapper}
      initial={{ opacity: 0 }}
      animate={isExiting ? { opacity: 0 } : { opacity: 1 }}
      transition={{ duration: 0.25, delay: 0.6 }}
    >
      <div className={styles.stageRow}>
        <div className={styles.stageSkeletonLine} />
      </div>
      <div className={styles.node}>
        <Handle type="target" position={Position.Left} style={{ opacity: 0, left: 3, top: '60%' }} />
        <div className={styles.skeletonLine} />
        <Handle type="source" position={Position.Right} style={{ opacity: 0, right: 3, top: '60%' }} />
      </div>
    </motion.div>
  )
}