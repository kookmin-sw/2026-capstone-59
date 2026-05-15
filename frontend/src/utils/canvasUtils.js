export const X_GAP = 350
export const Y_GAP = 170

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
      stroke: solid ? '#3c2ab0' : '#C5BDFB',
      strokeWidth: 1.5,
    },
  }
}

export function flattenTree(steps, stageSequence) {
  const nodes = []
  const edges = []

  function getSubtreeSize(node) {
    const children = node.children ?? []
    if (children.length === 0) return 0.6
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
        keep: node.is_keep ?? false,
      },
    })

    if (node.parent_step_id) {
      edges.push(makeEdge(node.parent_step_id, node.step_id, node.status === 'ACCEPTED'))
    }

    const children = node.children ?? []
    if (children.length === 0) return

    const regularChildren = children.filter(c => !c.is_required)
    const requiredChildren = children.filter(c => c.is_required)

    const sizes = regularChildren.map(child => getSubtreeSize(child))
    const totalLeaves = sizes.reduce((sum, s) => sum + s, 0)
    const totalHeight = totalLeaves > 0 ? (totalLeaves - 1) * Y_GAP : 0

    let currentY = centerY - totalHeight / 2

    regularChildren.forEach((child, index) => {
      const childCenterY = currentY + (sizes[index] - 1) * Y_GAP / 2
      build(child, depth + 1, childCenterY)
      currentY += sizes[index] * Y_GAP
    })

    const requiredY = regularChildren.length > 0
      ? currentY + Y_GAP * 0.2
      : centerY

    requiredChildren.forEach((child) => {
      build(child, depth + 1, requiredY)
    })
  }

  const rootGap = 260
  const rootStartY = 280 - (steps.length - 1) * rootGap / 2
  steps.forEach((root, index) => build(root, 0, rootStartY + index * rootGap))

  return { nodes, edges }
}

export function getStageProgressFromTree(nodes, edges) {
  const firstRequired = nodes.find(
    (node) =>
      node.type === 'requiredStepNode' &&
      !edges.some((edge) => edge.target === node.id)
  )
  return firstRequired
    ? edges.some((edge) => edge.source === firstRequired.id)
    : false
}

export function findRequiredStep(nodeId, nodes, edges) {
  const parentEdge = edges.find((e) => e.target === nodeId)
  if (!parentEdge) return null
  const parentNode = nodes.find((n) => n.id === parentEdge.source)
  if (!parentNode) return null
  if (parentNode.type === 'requiredStepNode') return parentNode
  return findRequiredStep(parentNode.id, nodes, edges)
}

export function getLatestActiveStage(stageList) {
  const activeStages = stageList.filter((s) => s.is_active)
  return activeStages.length > 0
    ? activeStages.reduce((max, s) =>
        s.stage_sequence > max.stage_sequence ? s : max
      )
    : null
}