import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import {
  ReactFlow, Background, Controls,
  useNodesState, useEdgesState, addEdge,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import StageNavigator from '../components/canvas/StageNavigator'
import SidePanel from '../components/canvas/SidePanel'
import ToastAlarm from '../components/canvas/ToastAlarm'
import ContextMenu from '../components/canvas/onNodeContext'
import StepNode from '../components/canvas/StepNode'
import RequiredStepNode from '../components/canvas/RequiredStepNode'
import GhostNode from '../components/canvas/GhostNode'
import GhostEdge from '../components/canvas/GhostEdge'
import NewEdge from '../components/canvas/NewEdge'
import OnboardingTour from '../components/OnboardingTour'
import MdExportModal from '../components/canvas/MdExportModal'
import DownloadNotification from '../components/canvas/DownloadNotification'

import { getStages } from '../api/stage'
import { getStepTree, getStepDetail, acceptStep, rollbackStep, createSidePanelStream, keepStep, getSidePanelContent } from '../api/step'
import { createShare, deleteShare, getShareStatus } from '../api/projects'
import { createDesignExportStream, getDesignExportJobId, startDesignExport } from '../api/exports'
import { getMe } from '../api/auth'
import { BsLink45Deg, BsCheck } from 'react-icons/bs'

import { 
  REQUIRED_STEPS_BY_STAGE, STAGE_NAMES,
  STAGE_ENGLISH, X_GAP, Y_GAP, flattenTree, 
  getStageProgressFromTree, findRequiredStep, findAcceptedLeaf, 
  getLatestActiveStage, predictGhostPositions
} from '../utils/canvasUtils'

import styles from './CanvasPage.module.css'
import { HiOutlineUser } from 'react-icons/hi'

const nodeTypes = {
  stepNode: StepNode,
  requiredStepNode: RequiredStepNode,
  ghostNode: GhostNode,
}

const edgeTypes = {
  newEdge: NewEdge,
  ghostEdge: GhostEdge,
}

export default function CanvasPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const projectName = location.state?.projectName ?? 'Project'

  const [stages, setStages] = useState([])
  const [currentStageSequence, setCurrentStageSequence] = useState(1)
  const [selectedStageId, setSelectedStageId] = useState(null)
  const [navCollapsed, setNavCollapsed] = useState(
    () => localStorage.getItem('navCollapsed') === 'true'
  )
  const [user, setUser] = useState(null)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const userWrapperRef = useRef(null)
  const [selectedStep, setSelectedStep] = useState(null)
  const [stepDetail, setStepDetail] = useState(null)
  const [streamingText, setStreamingText] = useState(null)
  const [contextMenu, setContextMenu] = useState(null)
  const [rfInstance, setRfInstance] = useState(null)
  const [rollbackModal, setRollbackModal] = useState(false)
  const [isAccepting, setIsAccepting] = useState(false)
  
  const [isStreamMode, setIsStreamMode] = useState(false)
  const [shareModal, setShareModal] = useState(false)
  // 'loading' | 'idle'(공유 시작 전) | 'active'(공유 중) | 'error'
  const [shareStatus, setShareStatus] = useState('loading')
  const [shareUrl, setShareUrl] = useState('')
  const [shareBusy, setShareBusy] = useState(false) // 공유 / 그만하기 버튼 클릭 중복 방지
  const [shareCopied, setShareCopied] = useState(false)

  const [mdExportOpen, setMdExportOpen] = useState(false)
  const [downloadStatus, setDownloadStatus] = useState(null)  // null | 'downloading' | 'complete' | 'error'
  const exportStreamRef = useRef(null)

  const lastCompletedRequiredStepRef = useRef(null)
  const timerRef = useRef(null)
  const currentRequiredStepName = useRef(null)
  const autoOpenedStageRef = useRef(null)
  const shouldFitViewRef = useRef(false)
  const stageHasProgressRef = useRef({})
  const detailRequestRef = useRef(0)
  const streamBuffers = useRef(new Map())
  const enqueuedLenRef = useRef(0)
  const typingQueueRef = useRef('')
  const typingTimerRef = useRef(null)
  const typingDrainCallbackRef = useRef(null)
  const canvasWrapperRef = useRef(null)
  const ghostPositionsRef = useRef([])
  const savedPositionsRef = useRef(null)
  const movedPositionsRef = useRef(null)
  const requiredSlotRef = useRef(null)
  const siblingRequiredIdRef = useRef(null)

  // 첫 진입 가이드 투어 (캔버스)
  const [tourOpen, setTourOpen] = useState(false)
  useEffect(() => {
    const seen = localStorage.getItem('poco.tour.canvas')
    if (!seen) {
      const t = setTimeout(() => setTourOpen(true), 800)
      return () => clearTimeout(t)
    }
  }, [])
  const handleTourClose = () => {
    setTourOpen(false)
    localStorage.setItem('poco.tour.canvas', '1')
  }
  const TOUR_STEPS = [
    {
      selector: `[data-tour="canvas-stage-nav"]`,
      title: 'Stage Navigator',
      body: '왼쪽 패널은 6단계 SDLC 진행 상황을 보여줘요. 단계마다 핵심 관문이 있고, 클릭해서 이동할 수 있습니다.',
      placement: 'right',
    },
    {
      selector: `[data-tour="canvas-area"]`,
      title: '의사결정 캔버스',
      body: 'AI가 제안한 다음 한 걸음의 선택지가 노드로 그려져요. 마음에 드는 Step을 클릭한 뒤 우측 사이드 패널에서 Accept버튼을 클릭하면 해당 경로로 진행됩니다.',
      placement: 'top',
    },
    {
      selector: `[data-tour="canvas-share"]`,
      title: '공유하기',
      body: '읽기 전용 링크로 캔버스를 외부에 공유할 수 있어요. 팀원에게 진행 상황을 보여줄 때 유용합니다.',
      placement: 'bottom',
    },
  ]

  // SidePanel 첫 노출 가이드 투어
  const [sidePanelTourOpen, setSidePanelTourOpen] = useState(false)
  const [sidePanelTourTab, setSidePanelTourTab] = useState(null)
  const handleSidePanelTourClose = () => {
    setSidePanelTourOpen(false)
    setSidePanelTourTab(null)
    localStorage.setItem('poco.tour.sidePanel', '1')
  }
  const SIDE_PANEL_TOUR_STEPS = [
    {
      selector: `[data-tour="sidepanel-tab-mentoring"]`,
      title: 'AI Mentoring',
      body: '이 Step의 목적, 추천 방법, 자주 하는 실수, 한 줄 팁을 AI가 정리해드려요.',
      placement: 'bottom',
      onEnter: () => setSidePanelTourTab('mentoring'),
    },
    {
      selector: `[data-tour="sidepanel-tab-dictionary"]`,
      title: 'Dictionary',
      body: '이 Step에서 등장한 용어를 한 번에 모아 풀이해드려요. 처음 보는 단어가 있어도 따로 검색할 필요 없어요.',
      placement: 'bottom',
      onEnter: () => setSidePanelTourTab('dictionary'),
    },
    {
      selector: `[data-tour="sidepanel-accept"]`,
      title: 'Accept',
      body: '이 Step으로 결정하면 AI가 다음 한 걸음의 선택지 3개를 새로 만들어 드려요. 결정의 흔적은 트리에 남습니다.',
      placement: 'top',
      onEnter: () => setSidePanelTourTab('mentoring'),
    },
  ]

  // SidePanel이 처음 열렸을 때 투어 시작 (캔버스 투어가 끝나야만 시작)
  useEffect(() => {
    if (!selectedStep) return
    if (tourOpen) return /* 캔버스 투어 진행 중이면 대기 */
    const seen = localStorage.getItem('poco.tour.sidePanel')
    if (seen) return
    const t = setTimeout(() => setSidePanelTourOpen(true), 500)
    return () => clearTimeout(t)
  }, [selectedStep, tourOpen])
  const detailCacheRef = useRef({})
  const [toast, setToast] = useState(null)
  const [toastVisible, setToastVisible] = useState(false)
  const [toastPersistent, setToastPersistent] = useState(false)
  const [toastDuration, setToastDuration] = useState(5500)
  const shownToastsRef = useRef(new Set())
  const persistentMsgRef = useRef(null)
  const justCompletedRSRef = useRef(null)
  const lastToastByStageRef = useRef({})  // { stageId: { message, persistent } }

  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  const onConnect = (params) => setEdges((eds) => addEdge(params, eds))

  function addGhostNodes(acceptedNode) {
    const stage = stages.find(s => s.stage_id === selectedStageId)
    const { ghostPositions, requiredSlot, existingPositions, siblingRequiredId } = predictGhostPositions(
      acceptedNode.id,
      nodes,
      edges,
      stage?.stage_sequence
    )

    // 실패 시 복원용으로 현재 위치 저장
    savedPositionsRef.current = new Map(
      nodes.filter(n => n.type !== 'ghostNode').map(n => [n.id, n.position])
    )

    ghostPositionsRef.current = ghostPositions
    movedPositionsRef.current = existingPositions
    requiredSlotRef.current = requiredSlot
    siblingRequiredIdRef.current = siblingRequiredId

    const ghostNodes = ghostPositions.map((pos, i) => ({
      id: `ghost-${i}`,
      type: 'ghostNode',
      position: pos,
      data: {},
      selectable: false,
      draggable: false,
    }))

    const ghostEdges = ghostPositions.map((_, i) => ({
      id: `ghost-edge-${i}`,
      source: acceptedNode.id,
      target: `ghost-${i}`,
      type: 'ghostEdge',
    }))

    setNodes(nds => [
      ...nds
        .filter(n => n.type !== 'ghostNode')
        .map(n => {
          if (n.id === siblingRequiredId) {
            return { ...n, data: { ...n.data, isExiting: true } }  // 옛 자리 + fade out
          }
          return existingPositions.has(n.id)
            ? { ...n, position: existingPositions.get(n.id) }
            : n
        }),
      ...ghostNodes
    ])
    
    setEdges(eds => [
      ...eds.filter(e => e.type !== 'ghostEdge').map(e => {
        if (siblingRequiredId && e.target === siblingRequiredId) {
          return {
            ...e,
            type: 'default',
            style: { ...e.style, opacity: 0, transition: 'opacity 0.3s' }
          }
        }
        return e
      }),
      ...ghostEdges
    ])
  }

  function removeGhostNodes() {
    // 고스트 노드 fade out
    setNodes(nds => nds.map(n =>
      n.type === 'ghostNode'
        ? { ...n, data: { ...n.data, isExiting: true } }
        : n
    ))

    setTimeout(() => {
      const saved = savedPositionsRef.current
      setNodes(nds =>
        nds
          .filter(n => n.type !== 'ghostNode')
          .map(n => saved?.has(n.id) ? { ...n, position: saved.get(n.id) } : n ))
      
      setEdges(eds => eds.filter(e => e.type !== 'ghostEdge'))
      savedPositionsRef.current = null
      ghostPositionsRef.current = []
      movedPositionsRef.current = null
      requiredSlotRef.current = null
      siblingRequiredIdRef.current = null
    }, 300)
  }

  function josa(word, form) {
    const code = word.charCodeAt(word.length - 1)
    const hasBatchim = (code - 0xAC00) % 28 !== 0
    const map = { '을/를': ['을', '를'], '이/가': ['이', '가'], '은/는': ['은', '는'], '(으)로': ['으로', '로'] }
    return hasBatchim ? map[form][0] : map[form][1]
  }


  function clearStreamCallbacks() {
    streamBuffers.current.forEach((buf) => {
      buf.onUpdate = null
      buf.onComplete = null
    })
  }

  function clearTyping() {
    if (typingTimerRef.current) {
      clearInterval(typingTimerRef.current)
      typingTimerRef.current = null
    }
    typingQueueRef.current = ''
    enqueuedLenRef.current = 0
    typingDrainCallbackRef.current = null
  }

  function showTimedToast(message, duration = 5500) {
    if (timerRef.current) clearTimeout(timerRef.current)
    setToast(message)
    setToastDuration(duration)
    setToastPersistent(false)
    setToastVisible(true)
    timerRef.current = setTimeout(() => setToastVisible(false), duration)
    if (selectedStageId) {
      lastToastByStageRef.current[selectedStageId] = { message, persistent: false }
    }
  }

  function showPersistentToast(message) {
    if (timerRef.current) clearTimeout(timerRef.current)
    setToast(message)
    setToastPersistent(true)
    setToastVisible(true)
    persistentMsgRef.current = message
    if (selectedStageId) {
    lastToastByStageRef.current[selectedStageId] = { message, persistent: true }
    }
  }
  function enqueueTyping(newChars) {
    typingQueueRef.current += newChars
    if (typingTimerRef.current) return  // 이미 돌고 있으면 큐에만 쌓음

    typingTimerRef.current = setInterval(() => {
      if (!typingQueueRef.current) {
        clearInterval(typingTimerRef.current)
        typingTimerRef.current = null
        // 큐 소진 → drain 콜백 실행
        const cb = typingDrainCallbackRef.current
        typingDrainCallbackRef.current = null
        cb?.()
        return
      }
      const step = Math.min(2, typingQueueRef.current.length)
      const chars = typingQueueRef.current.slice(0, step)
      typingQueueRef.current = typingQueueRef.current.slice(step)
      setStreamingText(prev => (prev ?? '') + chars)
    }, 16)
  }

  function startNodeStream(nodeId) {
    if (streamBuffers.current.has(nodeId)) return
    const buf = { text: '', isDone: false, stream: null, onUpdate: null, onComplete: null }
    streamBuffers.current.set(nodeId, buf)

    const stream = createSidePanelStream(nodeId)
    buf.stream = stream

    stream.start({
      // 폴링은 누적 content 전체를 전달 — 대입으로 처리 (중복 누적 방지)
      onChunk: (content) => {
        const b = streamBuffers.current.get(nodeId)
        if (!b) return
        b.text = content
        b.onUpdate?.(b.text)
      },
      onDone: async () => {
        const b = streamBuffers.current.get(nodeId)
        if (!b) return
        b.isDone = true
        const complete = b.onComplete
        b.onUpdate = null
        b.onComplete = null
        await complete?.()
        if (!detailCacheRef.current[nodeId]) {
          try {
            const full = JSON.parse(b.text)
            detailCacheRef.current[nodeId] = {
              mentoring: full.mentoring ?? {},
              dictionary: full.dictionary ?? [],
            }
          } catch {
            //
          }
        }
      },
      onError: async () => {
        const b = streamBuffers.current.get(nodeId)
        if (!b) return
        b.isDone = true
        const complete = b.onComplete
        b.onUpdate = null
        b.onComplete = null
        await complete?.()
      },
    })
  }

  useEffect(() => {
    getMe().then(setUser).catch(() => {})
  }, [])

  // 아바타 메뉴 외부 클릭 시 닫기
  useEffect(() => {
    if (!userMenuOpen) return
    function handleClose(e) {
      if (userWrapperRef.current && !userWrapperRef.current.contains(e.target)) {
        setUserMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClose)
    return () => document.removeEventListener('mousedown', handleClose)
  }, [userMenuOpen])

  useEffect(() => {
    if (!projectId) return
    getStages(projectId).then((data) => {
      const list = data.stages ?? []
      setStages(list)

      const latestActive = getLatestActiveStage(list)
      if (latestActive) setCurrentStageSequence(latestActive.stage_sequence)

      const saved = sessionStorage.getItem(`selectedStage_${projectId}`)
      const savedStage = list.find((s) => s.stage_id === saved)
      if (savedStage) setSelectedStageId(savedStage.stage_id)
      else if (latestActive) setSelectedStageId(latestActive.stage_id)
    })
  }, [projectId])

  async function fetchAndRenderTree(stageId, { animateNew = false } = {}) {
    const treeData = await getStepTree(projectId, stageId)
    const stage = stages.find((s) => s.stage_id === stageId)
    
    const existingIds = animateNew
      ? new Set(nodes.filter(n => n.type !== 'ghostNode').map(n => n.id))
      : null
    
    const { nodes: n, edges: e } = flattenTree(treeData.steps ?? [], stage?.stage_sequence)

    const hasProgress = getStageProgressFromTree(n, e)
    stageHasProgressRef.current[stageId] = hasProgress

    let processedNodes
    const siblingReqId = animateNew ? siblingRequiredIdRef.current : null
    if (animateNew) {
      requiredSlotRef.current = null
      siblingRequiredIdRef.current = null
      movedPositionsRef.current = null
      ghostPositionsRef.current = []
      savedPositionsRef.current = null

      processedNodes = n.map(node => {
        const isReparentedRequired = siblingReqId && node.id === siblingReqId
        return {
          ...node,
          style: isReparentedRequired ? { transition: 'none' } : undefined,
          data: {
            ...node.data,
            isNew: !existingIds.has(node.id),
            isReparented: isReparentedRequired,
          },
        }
      })
    } else {
      processedNodes = n
    }

    setNodes(processedNodes)
      const processedEdges = animateNew
    ? e.map(edge => {
        const isReparentedTarget = siblingReqId && edge.target === siblingReqId
        return isReparentedTarget
          ? { ...edge, type: 'newEdge' }
          : edge
      })
    : e

    setEdges(processedEdges)

    const newNodeIds = new Set(n.map((node) => node.id))
    streamBuffers.current.forEach((buf, id) => {
      if (!newNodeIds.has(id)) {
        buf.stream?.abort()
        streamBuffers.current.delete(id)
      }
    })

    // 현재 진행 경로의 leaf로부터 소속 RS를 추적
    const leafAccepted = findAcceptedLeaf(n, e)
    let activeRS = null
    if (leafAccepted) {
      if (leafAccepted.type === 'requiredStepNode') {
        activeRS = leafAccepted
      } else {
        activeRS = findRequiredStep(leafAccepted.id, n, e)
      }
    }
    currentRequiredStepName.current = activeRS?.data?.label ?? null

    if (animateNew) {
      n.filter((node) =>
        !existingIds.has(node.id) &&                  // 새로 생긴 노드만
        node.data.status === 'READY' &&
        node.type !== 'requiredStepNode' &&
        !streamBuffers.current.has(node.id)
      ).forEach((node) => {
        startNodeStream(node.id)                      // 스트리밍만 시작 (getStepDetail X)
      })
    }
    
    if (!hasProgress && autoOpenedStageRef.current !== stageId) {
      const firstRequired = n.find(
        (node) =>
          node.type === 'requiredStepNode' &&
          !e.some((edge) => edge.target === node.id)
      )
      if (firstRequired) {
        autoOpenedStageRef.current = stageId
        setSelectedStep(firstRequired)
        setStepDetail(null)
        setStreamingText(null)

        const requestId = ++detailRequestRef.current
        try {
          const detail = await getStepDetail(firstRequired.id)
          if (requestId !== detailRequestRef.current) return
          setStepDetail(detail)
        } catch {
          //
        }
      }
    }
      const nextRequiredNode = n.find(
        (node) => node.type === 'requiredStepNode' && node.data.status === 'READY'
      )
      return { nextRequiredStepName: nextRequiredNode?.data?.label ?? null }
  }

  useEffect(() => {
    if (!rfInstance || nodes.length === 0) return
    if (!shouldFitViewRef.current) return
    shouldFitViewRef.current = false

    // 현재 진행 경로의 leaf — ACCEPTED 노드 중 ACCEPTED 자식이 없는 가장 끝 노드
    const acceptedNodes = nodes.filter((n) => n.data?.status === 'ACCEPTED')
    const acceptedIds = new Set(acceptedNodes.map((n) => n.id))
    const hasAcceptedChild = (parentId) =>
      edges.some((e) => e.source === parentId && acceptedIds.has(e.target))
    const leafAccepted = acceptedNodes.find((n) => !hasAcceptedChild(n.id))
    // ACCEPTED가 없으면 첫 노드(루트)로 fallback
    const focusNode = leafAccepted ?? nodes[0]
    if (!focusNode) return

    // 캔버스 wrapper의 실제 픽셀 크기 측정 (sidebar/sidepanel 제외한 실제 영역)
    const wrap = canvasWrapperRef.current
    const rect = wrap?.getBoundingClientRect()
    const viewportW = rect?.width ?? window.innerWidth
    const viewportH = rect?.height ?? window.innerHeight

    ;(async () => {
      const NODE_W = 180
      const NODE_H = focusNode.type === 'requiredStepNode' ? 120 : 70

      if (nodes.length < 4) {
        // 왼쪽 정렬 + Y만 focusNode 중앙
        const cy = (focusNode.position?.y ?? 0) + NODE_H / 2
        const targetY = viewportH / 2 - cy
        rfInstance.setViewport(
          { x: -10, y: targetY, zoom: 1 },
          { duration: 0 }
        )
        return
      }

      // 5개 이상: fitView + X/Y 모두 focusNode 중앙
      await rfInstance.fitView({ duration: 0, padding: 0.2 })
      const zoom = rfInstance.getZoom()

      const cx = (focusNode.position?.x ?? 0) + NODE_W / 2
      const cy = (focusNode.position?.y ?? 0) + NODE_H / 2
      const targetX = viewportW / 2 - cx * zoom
      const targetY = viewportH / 2 - cy * zoom

      rfInstance.setViewport(
        { x: targetX, y: targetY, zoom },
        { duration: 400 }
      )
    })()
  }, [nodes, edges, rfInstance])

  useEffect(() => {
  // if (!selectedStageId || !projectId) return
  shouldFitViewRef.current = true

  // 더미 필수 노드 1개 (디자인 확인용)
  setNodes([
    {
      id: 'dummy-required',
      type: 'requiredStepNode',
      position: { x: 100, y: 300 },
      data: {
        label: '문제/기회 정의',
        status: 'ACCEPTED',
        is_required: true,
        stageNumber: 1,
        step_id: 'dummy-required',
        keep: false,
      },
    },
  ])
  setEdges([])

  // fetchAndRenderTree(selectedStageId)   // ← 잠시 주석
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, [selectedStageId, projectId])

  useEffect(() => {
    clearTyping()
    setSelectedStep(null)
    setStepDetail(null)
    setStreamingText(null)
    autoOpenedStageRef.current = null
    streamBuffers.current.forEach((buf) => buf.stream?.abort())
    streamBuffers.current.clear()
    detailCacheRef.current = {}
    if (timerRef.current) clearTimeout(timerRef.current)
    if (justCompletedRSRef.current?.nextMsgTimer) {
      clearTimeout(justCompletedRSRef.current.nextMsgTimer)
      justCompletedRSRef.current = null
    }
    setToastVisible(false)
    setToastPersistent(false)
    // 이전 stage 기억된 토스트 → persistentMsgRef 복원 
    const remembered = lastToastByStageRef.current[selectedStageId]
    persistentMsgRef.current = remembered?.persistent ? remembered.message : null
    currentRequiredStepName.current = null
    lastCompletedRequiredStepRef.current = null
    shownToastsRef.current.clear()
  }, [selectedStageId])

  const activeStage = getLatestActiveStage(stages)
  const currentStageId = activeStage?.stage_id ?? null

  // const uiStages = stages.map((s) => ({
  //   id: s.stage_id,
  //   sequence: s.stage_sequence,
  //   name: s.stage_name,
  //   englishName: STAGE_ENGLISH[s.stage_sequence] ?? '',
  //   status: activeStage?.stage_id === s.stage_id ? 'active'
  //     : s.stage_sequence < currentStageSequence ? 'completed'
  //     : 'locked',
  // }))
  // 더미 데이터 (디자인 확인용) — 1·2 완료, 3 진행중, 4~6 잠김
const uiStages = [
  { id: 'd1', sequence: 1, name: '아이디어 구체화', englishName: 'Ideation',    status: 'completed' },
  { id: 'd2', sequence: 2, name: '프로젝트 계획',   englishName: 'Planning',    status: 'completed' },
  { id: 'd3', sequence: 3, name: '요구사항 정의',   englishName: 'Requirement', status: 'active' },
  { id: 'd4', sequence: 4, name: '설계',           englishName: 'Design',      status: 'locked' },
  { id: 'd5', sequence: 5, name: '개발',           englishName: 'Development', status: 'locked' },
  { id: 'd6', sequence: 6, name: '테스트 및 검증', englishName: 'Test',        status: 'locked' },
]

  function focusOnNode(node) {
    if (!rfInstance || !node?.position) return
    const wrap = canvasWrapperRef.current
    const rect = wrap?.getBoundingClientRect()
    if (!rect) return

    const NODE_W = 180
    const NODE_H = node.type === 'requiredStepNode' ? 120 : 70
    const cx = node.position.x + NODE_W / 2
    const cy = node.position.y + NODE_H / 2

    // SidePanel overlay 폭을 빼서 가시 영역의 중심 계산
    const SIDE_PANEL_W = 400 + 5
    const visibleW = Math.max(rect.width - SIDE_PANEL_W, rect.width * 0.5)
    const screenCenterX = visibleW / 2
    const screenCenterY = rect.height / 2

    const zoom = rfInstance.getZoom()
    rfInstance.setViewport(
      {
        x: screenCenterX - cx * zoom,
        y: screenCenterY - cy * zoom,
        zoom,
      },
      { duration: 450 }
    )
  }

  async function handleNodeClick(event, node) {
    if (node.type === 'ghostNode') return
    if (selectedStep?.id === node.id) return
    clearStreamCallbacks()
    clearTyping()
    setSelectedStep(node)
    setStreamingText(null)
    focusOnNode(node)

    if (detailCacheRef.current[node.id]) {
      setStepDetail(detailCacheRef.current[node.id])
    } else {
      setStepDetail(null)
    }

    const requestId = ++detailRequestRef.current
    let buf = streamBuffers.current.get(node.id)

    // 새로고침 등으로 in-memory buffer 가 유실된 경우 — 백엔드에 진행 상태 확인.
    // streaming/pending 이면 폴링을 재개해 화면을 복구한다.
    if (!buf && !detailCacheRef.current[node.id]) {
      try {
        const probe = await getSidePanelContent(node.id)
        if (requestId !== detailRequestRef.current) return
        if (probe.status === 'streaming' || probe.status === 'pending') {
          startNodeStream(node.id)
          buf = streamBuffers.current.get(node.id)
          if (buf && probe.content) {
            // 첫 폴링까지 기다리지 않고 누적된 raw text 를 미리 채워둠
            buf.text = probe.content
          }
        }
      } catch {
        // probe 실패는 무시 — 아래 분기에서 자연스럽게 처리됨
      }
    }

    if (buf?.isDone) {
      setIsStreamMode(false)
      if (detailCacheRef.current[node.id]) return
      try {
        const detail = await getStepDetail(node.id)
        if (requestId !== detailRequestRef.current) return
        setStepDetail(detail)
        detailCacheRef.current[node.id] = detail
      } catch {
        //
      }
    } else if (buf && !buf.isDone) {
      setIsStreamMode(false)
      clearTyping()
      const baseText = buf.text
      setStreamingText(baseText)
      enqueuedLenRef.current = baseText.length

      buf.onUpdate = (fullText) => {
        const newPart = fullText.slice(enqueuedLenRef.current)
        if (newPart) {
          enqueuedLenRef.current = fullText.length
          enqueueTyping(newPart)
        }
      }
      buf.onComplete = async () => {
        const proceed = async () => {
        try {
          const b = streamBuffers.current.get(node.id)
          const full = JSON.parse(b?.text ?? '{}')
          const detail = {
            mentoring: full.mentoring ?? {},
            dictionary: full.dictionary ?? [],
          }
          detailCacheRef.current[node.id] = detail
          if (requestId !== detailRequestRef.current) return
          setStepDetail(detail)
          setStreamingText(null)
        } catch {
          setStreamingText(null)
        }
        }
        if (!typingQueueRef.current && !typingTimerRef.current) {
          await proceed()
        } else {
          typingDrainCallbackRef.current = proceed
        }
      }
    } else {
      // ACCEPTED 노드 등 버퍼 없는 경우
      setIsStreamMode(false)
      if (detailCacheRef.current[node.id]) return
      try {
        const detail = await getStepDetail(node.id)
        if (requestId !== detailRequestRef.current) return
        setStepDetail(detail)
        detailCacheRef.current[node.id] = detail
      } catch {
        //
      }
    }
  }

  async function handleAccept() {
    if (!selectedStep) return
    if (isAccepting) return

    setIsAccepting(true) 
    try {
      const selectedStage = stages.find((s) => s.stage_id === selectedStageId)
      if (!selectedStage) return

      const hasLaterCompletedStage = stages.some(
        (s) =>
          s.stage_sequence > selectedStage.stage_sequence &&
          s.stage_sequence < currentStageSequence
      )

      if (hasLaterCompletedStage) {
        setRollbackModal(true)
        return
      }

      const latestActive = getLatestActiveStage(stages)

      if (latestActive && latestActive.stage_sequence > selectedStage.stage_sequence) {
        if (stageHasProgressRef.current[latestActive.stage_id] === undefined) {
          try {
            const treeData = await getStepTree(projectId, latestActive.stage_id)
            const { nodes: n, edges: e } = flattenTree(
              treeData.steps ?? [],
              latestActive.stage_sequence
            )
            stageHasProgressRef.current[latestActive.stage_id] = getStageProgressFromTree(n, e)
          } catch {
            alert('잠시후 다시 시도해주세요.')
            return
          }
        }

        if (stageHasProgressRef.current[latestActive.stage_id] === true) {
          setRollbackModal(true)
          return
        }
      }

      await executeAccept()
    } finally {
      setIsAccepting(false)
    }
  }

  async function handleRollbackConfirm() {
    setRollbackModal(false)
    clearStreamCallbacks()
    setStreamingText(null)

    try {
      await rollbackStep(selectedStep.id)
    } catch {
      alert('롤백에 실패했어요. 다시 시도해주세요.')
      return
    }

    const data = await getStages(projectId)
    const list = data.stages ?? []
    setStages(list)

    const latestActive = getLatestActiveStage(list)
    if (latestActive) {
      setCurrentStageSequence(latestActive.stage_sequence)
      stageHasProgressRef.current[latestActive.stage_id] = false

      const stageName = latestActive.stage_name ?? STAGE_NAMES[latestActive.stage_sequence]
      
      // selectedStep 기준으로 소속 RS 찾기
      let rsName = null
      if (selectedStep) {
        if (selectedStep.type === 'requiredStepNode') {
          rsName = selectedStep.data.label
        } else {
          const rs = findRequiredStep(selectedStep.id, nodes, edges)
          rsName = rs?.data?.label
        }
      }
      
      if (stageName) {
        const msg = rsName
          ? `🔥 ${stageName} 중 ${rsName}${josa(rsName, '(으)로')} 돌아왔어요!`
          : `🔥 ${stageName}${josa(stageName, '(으)로')} 돌아왔어요!`
        showTimedToast(msg, 5500)
      }
    }

    await executeAccept({ skipRollback: true })
  }

  async function executeAccept({ skipRollback = false } = {}) {
    setIsAccepting(true)

    try {
      const status = selectedStep.data?.status

      const parentEdge = edges.find((e) => e.target === selectedStep.id)
      const parentNode = parentEdge ? nodes.find((n) => n.id === parentEdge.source) : null
      const parentStatus = parentNode?.data?.status

      const siblings = parentEdge
        ? nodes.filter(
            (n) =>
              n.id !== selectedStep.id &&
              edges.some(
                (e) => e.source === parentEdge.source && e.target === n.id
              )
          )
        : []

      const acceptedSibling = siblings.find(
        (n) => n.data?.status === 'ACCEPTED'
      )

      const needsRollback =
        status === 'CANCELED' ||
        (status === 'READY' && !!acceptedSibling) ||
        (status === 'READY' && !!parentNode && parentStatus !== 'ACCEPTED')

      if (!skipRollback && needsRollback) {
        try {
          await rollbackStep(selectedStep.id)
        } catch {
          alert('롤백에 실패했어요. 다시 시도해주세요.')
          return
        }
      }

      addGhostNodes(selectedStep)

      let acceptResult
      try {
        acceptResult = await acceptStep(selectedStep.id)
      } catch (err) {
        if (err?.code !== 'STEP_ALREADY_ACCEPTED') {
          removeGhostNodes()
          alert('Step 생성에 실패했어요. 다시 시도해주세요.')
          return
        }
      }


      const isRSComplete = acceptResult?.is_current_required_step_completed
      const isStageComplete = acceptResult?.is_current_stage_completed

      const prevRSName = currentRequiredStepName.current

      if (selectedStep.type === 'requiredStepNode') {
        const stepName = selectedStep.data.label
        currentRequiredStepName.current = stepName
        lastCompletedRequiredStepRef.current = null

        const key = `enter_${selectedStep.id}`
        const overridePersistent = toastPersistent
        if (!shownToastsRef.current.has(key) || overridePersistent) {
          shownToastsRef.current.add(key)
          if (justCompletedRSRef.current?.nextMsgTimer) {
            clearTimeout(justCompletedRSRef.current.nextMsgTimer)
            justCompletedRSRef.current = null
          }
          persistentMsgRef.current = `✨ ${stepName}${josa(stepName, '을/를')} 진행 중이에요!`

          showTimedToast(`🔔 ${stepName}${josa(stepName, '이/가')} 시작됐어요!`, 5500)
        }
      }

      clearStreamCallbacks()
      setStreamingText(null)

      const { nextRequiredStepName } = await fetchAndRenderTree(selectedStageId, { animateNew: true })
      
      if (isStageComplete) {
        const key = `stage_complete_${selectedStageId}`
        if (!shownToastsRef.current.has(key)) {
          shownToastsRef.current.add(key)
          persistentMsgRef.current = `이제 다음 Stage로 이동할 수 있어요!`
          showPersistentToast(`🎉 Stage가 종료됐어요! 이제 다음 Stage로 이동할 수 있어요!`)
        }
        currentRequiredStepName.current = null
        getStages(projectId).then((data) => {
          const list = data.stages ?? []
          setStages(list)
          const latestActive = getLatestActiveStage(list)
          if (latestActive) setCurrentStageSequence(latestActive.stage_sequence)
        })

      } else if (isRSComplete) {
        const name = (() => {
          if (selectedStep.type === 'requiredStepNode') return selectedStep.data.label
          const req = findRequiredStep(selectedStep.id, nodes, edges)
          return req?.data?.label
        })()

        if (name && name !== lastCompletedRequiredStepRef.current) {
          lastCompletedRequiredStepRef.current = name
          const key = `complete_${name}`
          if (!shownToastsRef.current.has(key)) {
            shownToastsRef.current.add(key)
            const nextMsg = nextRequiredStepName
              ? `다음 단계인 ${nextRequiredStepName}${josa(nextRequiredStepName, '(으)로')} 이동할 수 있어요!`
              : `다음 필수 단계로 이동할 수 있어요!`
            persistentMsgRef.current = nextMsg

            showTimedToast(`🎉 ${name}${josa(name, '이/가')} 종료됐어요!`, 3000)
            const t = setTimeout(() => {
              showPersistentToast(nextMsg)
              justCompletedRSRef.current = null
            }, 3000)
            justCompletedRSRef.current = { name, nextMsgTimer: t }
          }
        }
      }

      if (skipRollback || needsRollback) {
        if (!isStageComplete && !isRSComplete && selectedStep.type !== 'requiredStepNode') {
          if (justCompletedRSRef.current?.nextMsgTimer) {
            clearTimeout(justCompletedRSRef.current.nextMsgTimer)
            justCompletedRSRef.current = null
          }
          lastCompletedRequiredStepRef.current = null

          const selectedRSName = selectedStep.type === 'requiredStepNode'
            ? selectedStep.data.label
            : findRequiredStep(selectedStep.id, nodes, edges)?.data?.label

          if (selectedRSName && selectedRSName !== prevRSName) {
            persistentMsgRef.current = `✨ ${selectedRSName}${josa(selectedRSName, '을/를')} 진행 중이에요!`
            showTimedToast(`🔥 ${selectedRSName}${josa(selectedRSName, '(으)로')} 돌아왔어요!`, 5500)
          } else {
            persistentMsgRef.current = null
          }
        }
      }

      setSelectedStep(null)
      setStepDetail(null)

    } finally {
      setIsAccepting(false)
    }
  }


  function handleNodeContextMenu(event, node) {
    event.preventDefault()
    if (node.data?.status !== 'ACCEPTED') return
    if (node.type === 'requiredStepNode') return
    setContextMenu({ x: event.clientX, y: event.clientY, node })
  }

  async function handleKeepToggle(nodeId) {
    const node = nodes.find(n => n.id === nodeId)
    const newKeep = !node?.data?.keep

    setNodes((nds) =>
      nds.map((n) =>
        n.id === nodeId
          ? { ...n, data: { ...n.data, keep: newKeep } }
          : n
      )
    )

    try {
      await keepStep(nodeId, newKeep)
    } catch {
      setNodes((nds) =>
        nds.map((n) =>
          n.id === nodeId
            ? { ...n, data: { ...n.data, keep: !newKeep } }
            : n
        )
      )
    }
  }

  function handlePaneClick() {
    clearStreamCallbacks()
    clearTyping() 
    setSelectedStep(null)
    setStepDetail(null)
    setStreamingText(null)
  }

  // 공유 모달 진입 — 모달을 즉시 열고 공유 상태를 조회
  async function handleShareOpen() {
    setShareModal(true)
    setShareStatus('loading')
    setShareCopied(false)
    try {
      const result = await getShareStatus(projectId)
      if (result?.share_token) {
        setShareUrl(`${window.location.origin}/shared/${result.share_token}`)
        setShareStatus('active')
      } else {
        setShareUrl('')
        setShareStatus('idle')
      }
    } catch {
      setShareStatus('error')
    }
  }

  function handleShareClose() {
    setShareModal(false)
    setShareUrl('')
    setShareCopied(false)
    setShareStatus('loading')
  }

  // idle 상태에서 "공유" 버튼 클릭 → 토큰 생성 → active 로 전환
  async function handleShareCreate() {
    if (shareBusy) return
    setShareBusy(true)
    try {
      const result = await createShare(projectId)
      setShareUrl(`${window.location.origin}/shared/${result.share_token}`)
      setShareStatus('active')
    } catch {
      alert('공유 링크 생성에 실패했어요.')
    } finally {
      setShareBusy(false)
    }
  }

  // active 상태에서 "공유 그만하기" 클릭 → 토큰 삭제 → idle 로 전환
  async function handleShareRevoke() {
    if (shareBusy) return
    setShareBusy(true)
    try {
      await deleteShare(projectId)
      setShareUrl('')
      setShareCopied(false)
      setShareStatus('idle')
    } catch {
      alert('공유 중지에 실패했어요.')
    } finally {
      setShareBusy(false)
    }
  }

  async function handleCopyUrl() {
    // navigator.clipboard 는 HTTPS / localhost 에서만 동작하므로
    // 실패하거나 미지원이면 document.execCommand('copy') 로 폴백한다.
    const fallbackCopy = (text) => {
      const textarea = document.createElement('textarea')
      textarea.value = text
      textarea.setAttribute('readonly', '')
      textarea.style.position = 'fixed'
      textarea.style.top = '0'
      textarea.style.left = '-9999px'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      textarea.setSelectionRange(0, text.length)
      let ok = false
      try {
        ok = document.execCommand('copy')
      } catch {
        ok = false
      }
      document.body.removeChild(textarea)
      return ok
    }

    let success = false
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(shareUrl)
        success = true
      } else {
        success = fallbackCopy(shareUrl)
      }
    } catch {
      success = fallbackCopy(shareUrl)
    }

    if (success) {
      setShareCopied(true)
      setTimeout(() => setShareCopied(false), 2000)
    } else {
      alert('복사에 실패했어요.')
    }
  }

  function handleMdExportOpen() {
    setMdExportOpen(true)
  }

  function handleMdExportClose() {
    setMdExportOpen(false)
  }

  function handleDownloadNotificationClose() {
    setDownloadStatus(null)
  }

  function runExportStream(stream) {
    exportStreamRef.current = stream
    stream.start({
      onComplete: (data) => {
        try {
          const markdown = data?.markdown ?? ''
          const filename = data?.filename ?? `design_${new Date().toISOString().slice(0, 10)}.md`

          const blob = new Blob([markdown], { type: 'text/markdown' })
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = filename
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          URL.revokeObjectURL(url)

          setDownloadStatus('complete')
        } catch {
          setDownloadStatus('error')
        } finally {
          exportStreamRef.current = null
        }
      },
      onError: () => {
        setDownloadStatus('error')
        exportStreamRef.current = null
      },
    })
  }

  async function handleStartExport(selectedStepIds) {
    setMdExportOpen(false)

    // 사전 체크 — 이미 진행 중인 다운로드가 있으면 새 요청 보내지 말고 안내만.
    if (exportStreamRef.current || getDesignExportJobId(projectId)) {
      setDownloadStatus('rate_limited')
      return
    }

    setDownloadStatus('downloading')

    // POST 트리거 — 응답까지 await 해서 429 등을 즉시 감지.
    const result = await startDesignExport(projectId, selectedStepIds)
    if (result.error) {
      const { code, status } = result.error
      if (status === 429 || code === 'DESIGN_EXPORT_RATE_LIMITED') {
        setDownloadStatus('rate_limited')
      } else {
        setDownloadStatus('error')
      }
      return
    }

    // 성공 — 폴링 시작
    runExportStream(createDesignExportStream(projectId, result.jobId))
  }

  // 새로고침 후에도 진행 중이던 design-export 가 있으면 자동 재개.
  // localStorage 에 보관된 job_id 로 폴링만 다시 시작 (POST 생략).
  useEffect(() => {
    if (!projectId) return
    if (exportStreamRef.current) return // 이미 진행 중이면 skip
    const pendingJobId = getDesignExportJobId(projectId)
    if (!pendingJobId) return

    setDownloadStatus('downloading')
    runExportStream(createDesignExportStream(projectId, pendingJobId))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId])

  const selectedHasChildren = edges.some((e) => e.source === selectedStep?.id)

  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <img src="/poco-logo-text.svg" alt="poco" height={25} onClick={() => navigate('/projects')}/>
          <span>|</span>
          <span className={styles.projectName}>{projectName}</span>
        </div>
        <div className={styles.headerRight}>
        <button
          className={styles.shareBtn}
          onClick={handleMdExportOpen}
        >
          .md로 내보내기
        </button>
        <button
          className={styles.shareBtn}
          data-tour="canvas-share"
          onClick={handleShareOpen}>
            공유하기
        </button>
        <div className={styles.userWrapper} ref={userWrapperRef}>
          <button
            className={styles.avatar}
            onClick={() => setUserMenuOpen((v) => !v)}
          >
            <HiOutlineUser size={20} />
          </button>
          {userMenuOpen && (
            <div className={styles.userDropdown}>
              <p className={styles.userEmail}>{user?.email ?? '-'}</p>
            </div>
          )}
        </div>
      </div>
      </header>

      <div className={styles.body}>
        <div data-tour="canvas-stage-nav" style={{ display: 'flex', flexShrink: 0 }}>
          <StageNavigator
            stages={uiStages}
            currentStageId={currentStageId}
            selectedStageId={selectedStageId}
            onSelectStage={(id) => {
              setSelectedStageId(id)
              sessionStorage.setItem(`selectedStage_${projectId}`, id)
            }}
            collapsed={navCollapsed}
            onToggle={() => {
              const next = !navCollapsed
              setNavCollapsed(next)
              localStorage.setItem('navCollapsed', next)
            }}
          />
        </div>

        <div className={styles.canvasWrapper} data-tour="canvas-area" ref={canvasWrapperRef}>
          <ToastAlarm
            message={toast}
            visible={toastVisible}
            showProgress={!toastPersistent}
            duration={toastDuration}
            onToggle={() => {
              if (toastVisible) {
                setToastVisible(false)
                if (timerRef.current) clearTimeout(timerRef.current)
              } else if (persistentMsgRef.current) {
                showPersistentToast(persistentMsgRef.current)
              }
            }}
            onClose={() => {
              if (timerRef.current) clearTimeout(timerRef.current)
              setToastVisible(false)
            }}
          />

          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={handleNodeClick}
            onPaneClick={handlePaneClick}
            onNodeContextMenu={handleNodeContextMenu}
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes} 
            nodesDraggable={false}
            onInit={setRfInstance}
            defaultViewport={{ x: -10, y: 0, zoom: 1 }}
            minZoom={0.01}
            maxZoom={2}
          >
            <Background variant="dots" gap={24} size={1.5} color="#C8C4E8" />
            <Controls position="bottom-center" showInteractive={false} />
          </ReactFlow>
        </div>

        <SidePanel
          step={selectedStep}
          detail={stepDetail}
          streamingText={streamingText}
          isOpen={!!selectedStep}
          isAccepting={isAccepting}
          isStreamMode={isStreamMode}
          hasChildren={selectedHasChildren}
          forceTab={sidePanelTourTab}
          onClose={() => {
            clearStreamCallbacks()
            clearTyping()
            setSelectedStep(null)
            setStepDetail(null)
            setStreamingText(null)
          }}
          onAccept={handleAccept}
        />

        {contextMenu && (
          <ContextMenu
            x={contextMenu.x}
            y={contextMenu.y}
            node={contextMenu.node}
            onKeepToggle={handleKeepToggle}
            onClose={() => setContextMenu(null)}
          />
        )}

        {rollbackModal && (
          <div className={styles.overlay} onClick={() => setRollbackModal(false)}>
            <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
              <div className={styles.iconWrap}>⚠️</div>
              <p className={styles.title}>이전 Stage로 돌아가시겠습니까?</p>
              <p className={styles.desc}>
                이후 Stage의 진행 내역이 삭제될 수 있습니다. 계속 하시겠습니까?
              </p>
              <div className={styles.actions}>
                <button className={styles.cancelBtn} onClick={() => setRollbackModal(false)}>
                  취소
                </button>
                <button className={styles.rollbackBtn} onClick={handleRollbackConfirm}>
                  롤백하기
                </button>
              </div>
            </div>
          </div>
        )}

        {shareModal && (
          <div className={styles.overlay} onClick={handleShareClose}>
            <div className={styles.shareModal} onClick={(e) => e.stopPropagation()}>
              {/* 헤더 — 상태마다 타이틀이 달라짐 */}
              <div className={styles.shareModalHeader}>
                <p className={styles.shareModalTitle}>
                  {shareStatus === 'active' ? '캔버스 공유하기' : '공유하기'}
                  {shareStatus === 'active' && (
                    <span className={styles.shareActiveBadge}>공유 중</span>
                  )}
                </p>
                <button className={styles.closeBtn} onClick={handleShareClose}>✕</button>
              </div>

              {/* 로딩 */}
              {shareStatus === 'loading' && (
                <p className={styles.shareModalDesc}>공유 상태를 확인하는 중이에요...</p>
              )}

              {/* 에러 */}
              {shareStatus === 'error' && (
                <p className={styles.shareModalDesc}>
                  공유 상태를 불러오지 못했어요.<br />
                  잠시 후 다시 시도해주세요.
                </p>
              )}

              {/* idle — 아직 공유되지 않은 상태 */}
              {shareStatus === 'idle' && (
                <>
                  <div className={styles.shareLinkIcon}>
                    <BsLink45Deg size={28} />
                  </div>
                  <p className={styles.shareModalDesc}>
                    링크를 통해 다른 사람들과 프로젝트를 공유할 수 있어요.
                  </p>
                  <button
                    className={styles.sharePrimaryBtn}
                    onClick={handleShareCreate}
                    disabled={shareBusy}
                  >
                    {shareBusy ? '공유 링크 생성 중...' : '공유'}
                  </button>
                </>
              )}

              {/* active — 공유 중 */}
              {shareStatus === 'active' && (
                <>
                  <p className={styles.shareModalDesc}>
                    링크가 있는 사람은 누구나 캔버스를 열어볼 수 있어요.<br />
                    캔버스는 읽기 전용으로 공유됩니다.
                  </p>
                  <div className={styles.shareLinkBox}>
                    <input className={styles.shareLinkInput} value={shareUrl} readOnly />
                    <button
                      className={styles.copyBtn}
                      onClick={handleCopyUrl}
                    >
                      {shareCopied ? <BsCheck size={18} /> : <BsLink45Deg size={18} />}
                    </button>
                  </div>
                  <p className={styles.shareReadonlyHint}>
                    👁  방문자는 <strong>읽기 전용</strong>으로 캔버스를 봐요
                  </p>
                  <button
                    className={styles.revokeBtn}
                    onClick={handleShareRevoke}
                    disabled={shareBusy}
                  >
                    {shareBusy ? '공유 중단 중...' : '공유 그만하기'}
                  </button>
                </>
              )}
            </div>
          </div>
        )}

        {mdExportOpen && (
          <MdExportModal
            projectId={projectId}
            onClose={handleMdExportClose}
            onDownload={handleStartExport}
          />
        )}

        <DownloadNotification
          status={downloadStatus}
          onClose={handleDownloadNotificationClose}
        />
      </div>

      {/* 첫 진입 가이드 투어 */}
      <OnboardingTour
        steps={TOUR_STEPS}
        open={tourOpen}
        onClose={handleTourClose}
      />

      {/* SidePanel 첫 노출 가이드 투어 */}
      <OnboardingTour
        steps={SIDE_PANEL_TOUR_STEPS}
        open={sidePanelTourOpen}
        onClose={handleSidePanelTourClose}
      />
    </div>
  )
}