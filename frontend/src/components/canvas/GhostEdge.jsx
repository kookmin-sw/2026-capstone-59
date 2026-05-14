import { getBezierPath } from '@xyflow/react'
import { motion } from 'framer-motion'

export default function GhostEdge({
  sourceX, sourceY, targetX, targetY,
  sourcePosition, targetPosition,
}) {
  const [edgePath] = getBezierPath({
    sourceX, sourceY, sourcePosition,
    targetX, targetY, targetPosition,
  })

  return (
    <motion.path
      d={edgePath}
      fill="none"
      stroke="#C5BDFB"
      strokeWidth={1.5}
      initial={{ pathLength: 0, opacity: 0 }}
      animate={{ pathLength: 1, opacity: 1 }}
      transition={{ duration: 0.7, ease: 'easeOut' }}
    />
  )
}