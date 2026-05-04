export const X_GAP = 350
export const Y_GAP = 90

export const STAGE_ENGLISH = {
  1: 'Ideation', 2: 'Planning', 3: 'Requirement',
  4: 'Design', 5: 'Development', 6: 'Test',
}

export const EDGE_STYLE = {
  type: '',
  style: { stroke: '#291C80', strokeWidth: 1, strokeDasharray: '8,8' },
}

export function makeEdge(sourceId, targetId, solid = false) {
  return {
    id: `e-${sourceId}-${targetId}`,
    source: sourceId,
    target: targetId,
    type: 'default',
    style: {
      stroke: '#291C80',
      strokeWidth: solid ?  1.5: 1.5,
      strokeDasharray: solid ? undefined : '5,5',
    },
  }
}

export function flattenTree(steps, stageSequence) {
  const nodes = []
  const edges = []

  function getSubtreeSize(node) {
    const children = node.children ?? []
    if (children.length === 0) return 1
    return children.reduce((sum, child) => sum + getSubtreeSize(child), 0)
  }

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

    if (node.parent_step_id) {
      edges.push(makeEdge(node.parent_step_id, node.step_id, node.status === 'ACCEPTED'))
    }

    const children = node.children ?? []
    if (children.length === 0) return

    const sorted = [...children].sort((a, b) => (a.is_required ? 1 : 0) - (b.is_required ? 1 : 0))
    const sizes = sorted.map(child => getSubtreeSize(child))
    const totalLeaves = sizes.reduce((sum, s) => sum + s, 0)
    const totalHeight = (totalLeaves - 1) * Y_GAP

    let currentY = centerY - totalHeight / 2
    sorted.forEach((child, index) => {
      const childCenterY = currentY + (sizes[index] - 1) * Y_GAP / 2
      build(child, depth + 1, childCenterY)
      currentY += sizes[index] * Y_GAP
    })
  }

  const rootGap = 260
  const rootStartY = 200 - (steps.length - 1) * rootGap / 2
  steps.forEach((root, index) => build(root, 0, rootStartY + index * rootGap))

  return { nodes, edges }
}