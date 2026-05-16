import { getBezierPath } from '@xyflow/react'
import { motion } from 'framer-motion'

export default function NewEdge({
  sourceX, sourceY, targetX, targetY,
  sourcePosition, targetPosition,
  style = {},
}) {
  const [edgePath] = getBezierPath({
    sourceX, sourceY, sourcePosition,
    targetX, targetY, targetPosition,
  })

  return (
    <motion.path
      d={edgePath}
      fill="none"
      stroke={style.stroke ?? '#291C80'}
      strokeWidth={style.strokeWidth ?? 1.5}
      strokeDasharray={style.strokeDasharray}
      initial={{ pathLength: 0, opacity: 0 }}
      animate={{ pathLength: 1, opacity: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
    />
  )
}