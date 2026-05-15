// 프로젝트 카드의 미니 캔버스 미리보기 전용 레이아웃 계산기.
// 캔버스의 flattenTree 와 동일한 LR 트리 알고리즘을 작게 압축한 버전.

const X_GAP = 28
const Y_GAP = 16

function getSubtreeSize(node) {
  const children = node.children ?? []
  if (children.length === 0) return 0.6
  return children.reduce((sum, child) => sum + getSubtreeSize(child), 0)
}

/**
 * Step 트리(roots: StepTreeNode[])를 SVG 렌더용으로 변환한다.
 * 반환:
 *   { nodes: [{ id, x, y, status, isRequired, isKeep }],
 *     edges: [{ from: {x,y}, to: {x,y}, accepted }],
 *     bbox: { x, y, width, height } }
 */
export function computeThumbnailLayout(roots) {
  const nodes = []
  const edges = []

  if (!roots?.length) return { nodes, edges, bbox: { x: 0, y: 0, width: 0, height: 0 } }

  function build(node, depth, centerY, parentInfo) {
    const x = depth * X_GAP
    const y = centerY

    nodes.push({
      id: node.step_id,
      x,
      y,
      status: node.status,
      isRequired: node.is_required,
      isKeep: node.is_keep ?? false,
    })

    if (parentInfo) {
      edges.push({
        from: { x: parentInfo.x, y: parentInfo.y },
        to: { x, y },
        accepted: node.status === 'ACCEPTED',
      })
    }

    const children = node.children ?? []
    if (children.length === 0) return

    const regularChildren = children.filter(c => !c.is_required)
    const requiredChildren = children.filter(c => c.is_required)

    const sizes = regularChildren.map(c => getSubtreeSize(c))
    const totalLeaves = sizes.reduce((s, v) => s + v, 0)
    const totalHeight = totalLeaves > 0 ? (totalLeaves - 1) * Y_GAP : 0

    let lastRegularY = y
    let currentY = y - totalHeight / 2

    regularChildren.forEach((child, i) => {
      const childCenterY = currentY + (sizes[i] - 1) * Y_GAP / 2
      build(child, depth + 1, childCenterY, { x, y })
      lastRegularY = childCenterY
      currentY += sizes[i] * Y_GAP
    })

    requiredChildren.forEach((child) => {
      build(child, depth + 1, lastRegularY + Y_GAP * 0.5, { x, y })
    })
  }

  roots.forEach(root => build(root, 0, 0, null))

  // bbox 계산 (노드 + 약간의 여백)
  const xs = nodes.map(n => n.x)
  const ys = nodes.map(n => n.y)
  const PAD = 12
  const minX = Math.min(...xs) - PAD
  const minY = Math.min(...ys) - PAD
  const maxX = Math.max(...xs) + PAD
  const maxY = Math.max(...ys) + PAD

  return {
    nodes,
    edges,
    bbox: { x: minX, y: minY, width: maxX - minX, height: maxY - minY },
  }
}
