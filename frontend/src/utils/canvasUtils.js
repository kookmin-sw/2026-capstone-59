import dagre from '@dagrejs/dagre'

// 기존 X_GAP/Y_GAP 은 CanvasPage 의 ghost 노드(생성 애니메이션) 좌표 계산에서 사용되므로 유지.
// flattenTree 내부에서는 더 이상 사용하지 않고, Dagre 의 ranksep/nodesep 으로 대체된다.
export const X_GAP = 350
export const Y_GAP = 170

// Dagre 레이아웃 파라미터
// - DAGRE_NODE_W/H 는 시각용 노드의 대략적 bounding box (StepNode 180w·~70h, RequiredStepNode 180w·120h)
// - RANKSEP 은 깊이(랭크) 사이 간격, NODESEP 은 같은 깊이 형제 사이 간격
// - 형제 간 노드 중심 거리 ≈ DAGRE_NODE_H + NODESEP
const DAGRE_NODE_W = 200
const DAGRE_NODE_H = 90
const DAGRE_RANKSEP = 150
const DAGRE_NODESEP = 36

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

/**
 * Step 트리를 Dagre 자동 레이아웃으로 평탄화한다.
 * - 좌→우(LR) 트리. 깊이가 같은 형제는 일정 간격(NODESEP)만 유지하므로
 *   자식이 늘어나도 상위 노드가 과도하게 벌어지지 않는다.
 * - Required Step 의 형제 정렬 우선순위는 build 순서(=children 배열 순서) 가 영향을 주며,
 *   기존처럼 일반 Step 을 먼저 배치한 뒤 Required Step 을 마지막에 추가해 시각적 흐름을 맞춘다.
 */
export function flattenTree(steps, stageSequence) {
  if (!steps?.length) return { nodes: [], edges: [] }

  const g = new dagre.graphlib.Graph()
  g.setGraph({
    rankdir: 'LR',
    nodesep: DAGRE_NODESEP,
    ranksep: DAGRE_RANKSEP,
    marginx: 40,
    marginy: 40,
  })
  g.setDefaultEdgeLabel(() => ({}))

  const meta = new Map() // step_id → step (원본 데이터 보관)

  function walk(node, parentId) {
    meta.set(node.step_id, node)
    g.setNode(node.step_id, { width: DAGRE_NODE_W, height: DAGRE_NODE_H })
    if (parentId) g.setEdge(parentId, node.step_id)

    // 일반 Step 을 먼저 추가하고 Required Step 을 마지막에 추가해
    // Dagre 가 형제 순서를 유지하면서 정렬하도록 한다.
    const children = node.children ?? []
    const regular = children.filter(c => !c.is_required)
    const required = children.filter(c => c.is_required)
    regular.forEach(c => walk(c, node.step_id))
    required.forEach(c => walk(c, node.step_id))
  }

  steps.forEach(root => walk(root, null))

  dagre.layout(g)

  const nodes = g.nodes().map(id => {
    const layoutNode = g.node(id)
    const stepData = meta.get(id)
    return {
      id,
      type: stepData.is_required ? 'requiredStepNode' : 'stepNode',
      // Dagre 는 노드 중심 좌표를 주므로 React Flow 의 좌상단 기준으로 변환
      position: {
        x: layoutNode.x - DAGRE_NODE_W / 2,
        y: layoutNode.y - DAGRE_NODE_H / 2,
      },
      data: {
        label: stepData.name,
        status: stepData.status,
        is_required: stepData.is_required,
        stageNumber: stageSequence,
        step_id: stepData.step_id,
        keep: stepData.is_keep ?? false,
      },
    }
  })

  const edges = g.edges().map(e => {
    const child = meta.get(e.w)
    return makeEdge(e.v, e.w, child?.status === 'ACCEPTED')
  })

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

export function predictGhostPositions(acceptedNodeId, rfNodes, rfEdges, stageSequence) {
  const realNodes = rfNodes.filter(n => n.type !== 'ghostNode')
  const realEdges = rfEdges.filter(e => e.type !== 'ghostEdge')

  const childrenMap = new Map()
  realNodes.forEach(n => childrenMap.set(n.id, []))
  realEdges.forEach(e => {
    childrenMap.get(e.source)?.push(e.target)
  })

  const fakeIds = ['__gp0', '__gp1', '__gp2']
  fakeIds.forEach(id => childrenMap.set(id, []))
  childrenMap.get(acceptedNodeId)?.push(...fakeIds)

  const hasParent = new Set(realEdges.map(e => e.target))
  const roots = realNodes.filter(n => !hasParent.has(n.id))
  const nodeMap = new Map(realNodes.map(n => [n.id, n]))

  function buildStep(nodeId) {
    const isFake = fakeIds.includes(nodeId)
    const node = nodeMap.get(nodeId)
    return {
      step_id: nodeId,
      name: isFake ? '' : (node?.data?.label ?? ''),
      status: isFake ? 'READY' : (node?.data?.status ?? 'READY'),
      is_required: isFake ? false : (node?.type === 'requiredStepNode'),
      is_keep: false,
      children: (childrenMap.get(nodeId) ?? []).map(buildStep),
    }
  }

  const steps = roots.map(r => buildStep(r.id))
  const { nodes: layoutNodes } = flattenTree(steps, stageSequence)

  const fakeSet = new Set(fakeIds)

  const ghostPositions = fakeIds
    .map(id => layoutNodes.find(n => n.id === id)?.position)
    .filter(Boolean)

  const existingPositions = new Map(
    layoutNodes
      .filter(n => !fakeSet.has(n.id))
      .map(n => [n.id, n.position])
  )

  return { ghostPositions, existingPositions }
}