export const X_GAP = 300
export const Y_GAP = 120

export const STAGE_ENGLISH = {
  1: 'Ideation', 2: 'Planning', 3: 'Requirement',
  4: 'Design', 5: 'Development', 6: 'Test',
}

export const EDGE_STYLE = {
  type: 'straight',
  style: { stroke: '#291C80', strokeWidth: 1.5, strokeDasharray: '5,5' },
}

export function makeEdge(sourceId, targetId) {
  return {
    id: `e-${sourceId}-${targetId}`,
    source: sourceId,
    target: targetId,
    ...EDGE_STYLE,
  }
}

export function flattenTree(steps, stageSequence) {
  const nodes = []
  const edges = []

  function build(node, depth, centerY) {
    nodes.push({
      id: node.step_id,
      type: node.is_required ? 'requiredStepNode' : 'stepNode',
      position: { x: depth * X_GAP + 50, y: centerY },
      data: {
        label: node.name,
        status: node.status,
        is_required: node.is_required,
        stageNumber: stageSequence,
        step_id: node.step_id,
      },
    })

    if (node.parent_step_id) edges.push(makeEdge(node.parent_step_id, node.step_id))

    const children = node.children ?? []
    if (children.length === 0) return
    const totalHeight = (children.length - 1) * Y_GAP
    const startY = centerY - totalHeight / 2
    children.forEach((child, index) => build(child, depth + 1, startY + index * Y_GAP))
  }

  const rootGap = 260
  const rootStartY = 200 - (steps.length - 1) * rootGap / 2
  steps.forEach((root, index) => build(root, 0, rootStartY + index * rootGap))

  return { nodes, edges }
}