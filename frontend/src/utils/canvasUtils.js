import { flextree } from 'd3-flextree'

// 기존 X_GAP/Y_GAP 은 CanvasPage 의 ghost 노드 좌표 계산에서 사용되므로 유지.
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
  6: ['테스트 계획 수립', '테스트 수행', '결과 분석 및 결함 기록', '최종 검토'],
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

// ===== Tidy tree 레이아웃 (d3-flextree 기반) =====
// 노드 타입별 실제 크기를 d3-flextree에 알려서 겹침 없이 컴팩트하게 배치.
// Walker's 알고리즘 기반이라 자식 순서가 자동으로 보존되고, 얕은 가지가
// 깊은 가지의 빈 공간에 자연스럽게 배치됨.

const NODE_W = 200
const STEP_H = 85
const REQUIRED_H = 130

const LEVEL_GAP = 150
const SIBLING_GAP = 45
const MARGIN_X = 40
const MARGIN_Y = 40

function nodeHeightOf(stepData) {
  return stepData?.is_required ? REQUIRED_H : STEP_H
}

function normalizeChildren(children = []) {
  const regular = children.filter((c) => !c.is_required)
  const required = children.filter((c) => c.is_required)
  return [...regular, ...required]
}

function normalize(node) {
  const children = normalizeChildren(node.children ?? []).map(normalize)

  if (children.length === 0) {
    return { ...node, children: [] }
  }

  const regular = children.filter((c) => !c.is_required)
  const required = children.find((c) => c.is_required)

  // regular 슬롯 3개 채우기 (자식이 하나라도 있으면 항상 3 슬롯은 유지 —
  // 부분 응답 / 누락 케이스에서도 가로 정렬을 유지하기 위함)
  const paddedRegular = [...regular]
  while (paddedRegular.length < 3) {
    paddedRegular.push({
      step_id: `__phantom_regular_${node.step_id}_${paddedRegular.length}__`,
      name: '',
      is_required: false,
      __phantom: true,
      children: [],
    })
  }

  // required 슬롯은 실제 required 자식이 존재할 때만 추가.
  // (없으면 phantom 도 두지 않아 3-children 레이아웃이 부모 Y 기준 대칭이 됨.)
  const finalChildren = required !== undefined
    ? [...paddedRegular, required]
    : paddedRegular

  return {
    ...node,
    children: finalChildren,
  }
}

function layoutOrderedTree(steps) {
  if (!steps?.length) return { nodes: [], edges: [] }

  // 가상 루트로 감싸서 멀티 루트 지원
  const rootData = steps.length === 1
    ? normalize(steps[0])
    : {
        step_id: '__virtual_root__',
        name: '',
        is_required: false,
        __virtual: true,
        children: steps.map(normalize),
      }

  const layout = flextree({
    nodeSize: (node) => [
      nodeHeightOf(node.data) + SIBLING_GAP, // 수직 spread (sibling 간격 포함)
      NODE_W + LEVEL_GAP,                     // 수평 depth (level 간격 포함)
    ],
    spacing: 0,
  })

  const tree = layout.hierarchy(rootData)
  layout(tree)

  const positioned = []
  const edges = []

  tree.each((node) => {
    if (node.data.__virtual) return
    if (node.data.__phantom) return

    const data = node.data
    const h = nodeHeightOf(data)

    positioned.push({
      id: data.step_id,
      type: data.is_required ? 'requiredStepNode' : 'stepNode',
      position: {
        x: MARGIN_X + node.y,            // d3 y = 우리의 x (depth)
        y: MARGIN_Y + node.x - h / 2,    // d3 x = 우리의 y (spread), 중심→top 변환
      },
      data: {
        label: data.name,
        status: data.status,
        is_required: data.is_required,
        stageNumber: data.stageNumber,
        step_id: data.step_id,
        keep: data.is_keep ?? false,
      },
    })

    if (node.parent && !node.parent.data.__virtual) {
      edges.push(makeEdge(
        node.parent.data.step_id,
        data.step_id,
        data.status === 'ACCEPTED'
      ))
    }
  })

  return { nodes: positioned, edges }
}

export function flattenTree(steps, stageSequence) {
  const withStage = (node) => ({
    ...node,
    stageNumber: stageSequence,
    children: (node.children ?? []).map(withStage),
  })

  const normalized = (steps ?? []).map(withStage)
  return layoutOrderedTree(normalized)
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

export function findAcceptedLeaf(nodes, edges) {
  const acceptedNodes = nodes.filter((n) => n.data?.status === 'ACCEPTED')
  const acceptedIds = new Set(acceptedNodes.map((n) => n.id))
  const hasAcceptedChild = (parentId) =>
    edges.some((e) => e.source === parentId && acceptedIds.has(e.target))
  return acceptedNodes.find((n) => !hasAcceptedChild(n.id)) ?? null
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

// 한 번의 호출에서 두 가지 가상 레이아웃을 계산해 돌려준다.
// - phase1 : regular 3개만 (required 슬롯 없음)        → ghost 단계에서 사용
// - phase2 : regular 3개 + required 1개 (sibling reparent 또는 신규)
//
// regular 3 자리는 phase1 ↔ phase2 에서 위치가 약간 달라진다 (3-children 은
// 부모 Y 기준 대칭, 4-children 은 살짝 압축되고 required 한 칸이 아래에 추가).
// CanvasPage 에서 이를 활용해 ghost → regular(3-only) → required push-in 으로
// 순차 reveal 한다.
function buildPredictedLayout(acceptedNodeId, rfNodes, rfEdges, stageSequence, { withRequired }) {
  const realNodes = rfNodes.filter(n => n.type !== 'ghostNode')
  const realEdges = rfEdges.filter(e => e.type !== 'ghostEdge')

  // accept 노드의 형제 중 READY 상태의 필수 노드 (reparent 대상) — withRequired 인 경우만 의미 있음
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

  const reparentingSibling = withRequired && siblingRequiredId

  // parent → children 인접 리스트
  const childrenMap = new Map()
  realNodes.forEach(n => childrenMap.set(n.id, []))
  realEdges.forEach(e => {
    // reparent 단계에서만 sibling required 의 기존 edge 를 끊고 새 자리로 옮긴다
    if (reparentingSibling && e.target === siblingRequiredId) return
    childrenMap.get(e.source)?.push(e.target)
  })

  // 가짜 regular 자식 3개는 항상 추가
  const fakeIds = ['__gp0', '__gp1', '__gp2']
  fakeIds.forEach(id => childrenMap.set(id, []))
  childrenMap.get(acceptedNodeId)?.push(...fakeIds)

  // 필수 슬롯은 withRequired 일 때만 추가
  const fakeRequiredId = '__gpR'
  let requiredSlotId = null
  if (withRequired) {
    if (reparentingSibling) {
      childrenMap.get(acceptedNodeId)?.push(siblingRequiredId)
      requiredSlotId = siblingRequiredId
    } else {
      childrenMap.set(fakeRequiredId, [])
      childrenMap.get(acceptedNodeId)?.push(fakeRequiredId)
      requiredSlotId = fakeRequiredId
    }
  }

  const hasParent = new Set()
  childrenMap.forEach((children) => {
    children.forEach((childId) => {
      hasParent.add(childId)
    })
  })
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

  const requiredSlot = requiredSlotId
    ? (layoutNodes.find(n => n.id === requiredSlotId)?.position ?? null)
    : null

  const existingPositions = new Map(
    layoutNodes
      .filter(n => !fakeSet.has(n.id))
      .map(n => [n.id, n.position])
  )

  return { ghostPositions, requiredSlot, existingPositions, siblingRequiredId }
}

export function predictGhostPositions(acceptedNodeId, rfNodes, rfEdges, stageSequence) {
  // Phase 1 — required 미포함 (3-children 대칭 레이아웃)
  const phase1 = buildPredictedLayout(acceptedNodeId, rfNodes, rfEdges, stageSequence, {
    withRequired: false,
  })
  // Phase 2 — required 포함 (response 에 required 가 도착했을 때 사용)
  const phase2 = buildPredictedLayout(acceptedNodeId, rfNodes, rfEdges, stageSequence, {
    withRequired: true,
  })

  // 기존 시그니처와 하위호환을 위해 phase1 의 ghost/existing 좌표를 그대로 노출하면서,
  // phase2 의 좌표를 함께 반환한다.
  return {
    // ghost 단계용 (3 슬롯)
    ghostPositions: phase1.ghostPositions,
    existingPositions: phase1.existingPositions,
    // required 가 응답에 포함될 때 적용할 4-슬롯 좌표
    phase2RegularPositions: phase2.ghostPositions, // 3 regulars 의 새 위치
    phase2ExistingPositions: phase2.existingPositions,
    requiredSlot: phase2.requiredSlot,
    siblingRequiredId: phase2.siblingRequiredId,
  }
}