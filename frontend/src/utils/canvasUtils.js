import dagre from '@dagrejs/dagre'

// 기존 X_GAP/Y_GAP 은 CanvasPage 의 ghost 노드(생성 애니메이션) 좌표 계산에서 사용되므로 유지.
// flattenTree 내부에서는 더 이상 사용하지 않고, Dagre 의 ranksep/nodesep 으로 대체된다.
export const X_GAP = 350
export const Y_GAP = 170

export const STAGE_ENGLISH = {
  1: 'Ideation', 2: 'Planning', 3: 'Requirement',
  4: 'Design', 5: 'Development', 6: 'Test',
}

// 24개 필수 Step 정의 (Stage별 4개)
export const REQUIRED_STEPS_BY_STAGE = {
  1: ['문제/기회 정의', '대상 사용자 파악', '핵심 컨셉 정의', '실현 가능성 검토'],
  2: ['일정 계획 수립', '역할 분담', '위험 식별', '개발 환경/도구 결정'],
  3: ['요구사항 도출', '기능 요구사항 정의', '비기능 요구사항 정의', '요구사항 검토'],
  4: ['시스템 아키텍처 정의', '데이터 모델 설계', '인터페이스 설계', '설계 리뷰'],
  5: ['개발 환경 구축', '핵심 기능 구현', '코드 통합', '코드 리뷰 및 자체 검증'],
  6: ['테스트 계획 수립', '테스트 수행', '결과 분석 및 결함 기록', '수용 테스트/최종 검토'],
}

export const STAGE_NAMES = {
  1: '아이디어 구체화',
  2: '프로젝트 계획',
  3: '요구사항 정의',
  4: '설계',
  5: '개발',
  6: '테스트 및 검증',
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

// Dagre 레이아웃 파라미터
// - DAGRE_NODE_W/H 는 시각용 노드의 대략적 bounding box (StepNode 180w·~70h, RequiredStepNode 180w·120h)
// - RANKSEP 은 깊이(랭크) 사이 간격, NODESEP 은 같은 깊이 형제 사이 간격
// - 형제 간 노드 중심 거리 ≈ DAGRE_NODE_H + NODESEP

const DAGRE_STEP_NODE_W = 200
const DAGRE_STEP_NODE_H = 90
const DAGRE_REQUIRED_NODE_H = 130
const DAGRE_RANKSEP = 150
const DAGRE_NODESEP = 36

function nodeHeightOf(stepData) {
  return stepData?.is_required ? DAGRE_REQUIRED_NODE_H : DAGRE_STEP_NODE_H
}

function nodeWidthOf() {
  return DAGRE_STEP_NODE_W
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

  const meta = new Map()
  const parentToOrderedChildren = new Map()

  function walk(node, parentId) {
    meta.set(node.step_id, node)

    g.setNode(node.step_id, {
      width: nodeWidthOf(node),
      height: nodeHeightOf(node),
    })

    if (parentId) {
      g.setEdge(parentId, node.step_id)
      if (!parentToOrderedChildren.has(parentId)) {
        parentToOrderedChildren.set(parentId, [])
      }
      parentToOrderedChildren.get(parentId).push(node.step_id)
    }

    const children = node.children ?? []
    const regular = children.filter((c) => !c.is_required)
    const required = children.filter((c) => c.is_required)

    regular.forEach((c) => walk(c, node.step_id))
    required.forEach((c) => walk(c, node.step_id))
  }

  steps.forEach((root) => walk(root, null))

  dagre.layout(g)

  function getDescendants(nodeId) {
    const result = [nodeId]
    const queue = [nodeId]
    const visited = new Set([nodeId])

    while (queue.length > 0) {
      const cur = queue.shift()
      const successors = g.successors(cur) ?? []

      for (const next of successors) {
        if (!visited.has(next)) {
          visited.add(next)
          result.push(next)
          queue.push(next)
        }
      }
    }

    return result
  }

  function getHeightById(id) {
    return nodeHeightOf(meta.get(id))
  }

  parentToOrderedChildren.forEach((childIds) => {
    if (childIds.length <= 1) return

    const subtreeInfos = childIds.map((id) => {
      const descendants = getDescendants(id)
      const tops = descendants.map((d) => g.node(d).y - getHeightById(d) / 2)
      const bottoms = descendants.map((d) => g.node(d).y + getHeightById(d) / 2)
      const top = Math.min(...tops)
      const bottom = Math.max(...bottoms)

      return {
        id,
        top,
        bottom,
        height: bottom - top,
      }
    })

    const subtreeMap = new Map(subtreeInfos.map((info) => [info.id, info]))
    const totalTop = Math.min(...subtreeInfos.map((s) => s.top))
    const totalBottom = Math.max(...subtreeInfos.map((s) => s.bottom))
    const totalHeight = subtreeInfos.reduce((sum, s) => sum + s.height, 0)
    const totalSpace = totalBottom - totalTop

    const gap =
      childIds.length > 1
        ? Math.max(DAGRE_NODESEP, (totalSpace - totalHeight) / (childIds.length - 1))
        : 0

    let currentTop = totalTop

    childIds.forEach((id) => {
      const subtree = subtreeMap.get(id)
      const deltaY = currentTop - subtree.top

      if (deltaY !== 0) {
        getDescendants(id).forEach((descId) => {
          g.node(descId).y += deltaY
        })
      }

      currentTop += subtree.height + gap
    })
  })

  const nodes = g.nodes().map((id) => {
    const layoutNode = g.node(id)
    const stepData = meta.get(id)
    const h = nodeHeightOf(stepData)
    const w = nodeWidthOf(stepData)

    return {
      id,
      type: stepData.is_required ? 'requiredStepNode' : 'stepNode',
      position: {
        x: layoutNode.x - w / 2,
        y: layoutNode.y - h / 2,
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

  const edges = g.edges().map((e) => {
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

  // accept 노드의 형제 중 READY 상태의 필수 노드 찾기 (reparent 대상)
  const acceptedParentEdge = realEdges.find(e => e.target === acceptedNodeId)
  const acceptedParentId = acceptedParentEdge?.source
  let siblingRequiredId = null
  if (acceptedParentId) {
    const siblingIds = realEdges
      .filter(e => e.source === acceptedParentId && e.target !== acceptedNodeId)
      .map(e => e.target)
    const siblingReq = realNodes.find(
      n => siblingIds.includes(n.id) 
        && n.type === 'requiredStepNode' 
        && n.data?.status === 'READY'
    )
    siblingRequiredId = siblingReq?.id ?? null
  }

  // parent → children 인접 리스트 (sibling 필수 edge는 제거)
  const childrenMap = new Map()
  realNodes.forEach(n => childrenMap.set(n.id, []))
  realEdges.forEach(e => {
    if (e.target === siblingRequiredId) return  // 옛 부모와의 연결 끊기
    childrenMap.get(e.source)?.push(e.target)
  })

  // 가짜 자식: 일반 3개 + 필수 1개 (또는 sibling required reparent)
  const fakeIds = ['__gp0', '__gp1', '__gp2']
  fakeIds.forEach(id => childrenMap.set(id, []))
  childrenMap.get(acceptedNodeId)?.push(...fakeIds)

  // 필수 슬롯: sibling required가 있으면 그걸, 없으면 가짜 필수 추가
  const fakeRequiredId = '__gpR'
  let requiredSlotId
  if (siblingRequiredId) {
    childrenMap.get(acceptedNodeId)?.push(siblingRequiredId)
    requiredSlotId = siblingRequiredId
  } else {
    childrenMap.set(fakeRequiredId, [])
    childrenMap.get(acceptedNodeId)?.push(fakeRequiredId)
    requiredSlotId = fakeRequiredId
  }

  const hasParent = new Set(
    realEdges
      .filter(e => e.target !== siblingRequiredId)
      .map(e => e.target)
  )
  const roots = realNodes.filter(n => !hasParent.has(n.id))
  const nodeMap = new Map(realNodes.map(n => [n.id, n]))

  function buildStep(nodeId) {
    const isFakeRegular = fakeIds.includes(nodeId)
    const isFakeRequired = nodeId === fakeRequiredId
    const isFake = isFakeRegular || isFakeRequired
    const node = nodeMap.get(nodeId)
    return {
      step_id: nodeId,
      name: isFake ? '' : (node?.data?.label ?? ''),
      status: isFake ? 'READY' : (node?.data?.status ?? 'READY'),
      is_required: isFakeRequired || (isFake ? false : node?.type === 'requiredStepNode'),
      is_keep: false,
      children: (childrenMap.get(nodeId) ?? []).map(buildStep),
    }
  }

  const steps = roots.map(r => buildStep(r.id))
  const { nodes: layoutNodes } = flattenTree(steps, stageSequence)

  const fakeSet = new Set([...fakeIds, fakeRequiredId])

  const ghostPositions = fakeIds
    .map(id => layoutNodes.find(n => n.id === id)?.position)
    .filter(Boolean)

  const requiredSlot = layoutNodes.find(n => n.id === requiredSlotId)?.position ?? null

  // existingPositions: 실제 존재하는 노드만 (가짜 제외)
  const existingPositions = new Map(
    layoutNodes
      .filter(n => !fakeSet.has(n.id))
      .map(n => [n.id, n.position])
  )

  return { ghostPositions, requiredSlot, existingPositions, siblingRequiredId }
}