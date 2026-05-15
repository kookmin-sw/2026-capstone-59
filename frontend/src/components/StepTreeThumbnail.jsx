import { useMemo } from 'react'
import { ReactFlow, ReactFlowProvider } from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import StepNode from './canvas/StepNode'
import RequiredStepNode from './canvas/RequiredStepNode'
import { flattenTree } from '../utils/canvasUtils'
import styles from './StepTreeThumbnail.module.css'

// 캔버스와 동일한 nodeTypes 사용 → 화면 그대로의 미리보기
const nodeTypes = {
  stepNode: StepNode,
  requiredStepNode: RequiredStepNode,
}

export default function StepTreeThumbnail({ steps, stageSequence, isLoading }) {
  const flow = useMemo(
    () => flattenTree(steps ?? [], stageSequence ?? 1),
    [steps, stageSequence]
  )

  if (isLoading && !steps) {
    return <div className={styles.skeleton} aria-hidden />
  }

  if (!steps?.length) {
    return (
      <div className={styles.empty}>
        <span>아직 진행된 Step이 없어요</span>
      </div>
    )
  }

  return (
    <div className={styles.thumbContainer}>
      <ReactFlowProvider>
        <ReactFlow
          nodes={flow.nodes}
          edges={flow.edges}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.12, includeHiddenNodes: false }}
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable={false}
          panOnDrag={false}
          zoomOnScroll={false}
          zoomOnPinch={false}
          zoomOnDoubleClick={false}
          preventScrolling={false}
          proOptions={{ hideAttribution: true }}
          minZoom={0.01}
          maxZoom={2}
        />
      </ReactFlowProvider>
    </div>
  )
}
