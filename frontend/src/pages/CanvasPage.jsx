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

import { getStages } from '../api/stage'
import { getStepTree, getStepDetail, acceptStep, rollbackStep, createSidePanelStream } from '../api/step'
import { createShare, deleteShare } from '../api/projects'
import { BsLink45Deg, BsCheck } from 'react-icons/bs'

import { STAGE_ENGLISH, flattenTree, getStageProgressFromTree, findRequiredStep, getLatestActiveStage } from '../utils/canvasUtils'

import styles from './CanvasPage.module.css'
import { HiOutlineUser } from 'react-icons/hi'

const nodeTypes = {
  stepNode: StepNode,
  requiredStepNode: RequiredStepNode,
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
  const [selectedStep, setSelectedStep] = useState(null)
  const [stepDetail, setStepDetail] = useState(null)
  const [streamingText, setStreamingText] = useState(null)
  const [contextMenu, setContextMenu] = useState(null)
  const [rfInstance, setRfInstance] = useState(null)
  const [rollbackModal, setRollbackModal] = useState(false)
  const [isAccepting, setIsAccepting] = useState(false)
  
  const [isStreamMode, setIsStreamMode] = useState(false)
  const [shareModal, setShareModal] = useState(false)
  const [shareUrl, setShareUrl] = useState('')
  const [shareLoading, setShareLoading] = useState(false)
  const [shareCopied, setShareCopied] = useState(false)

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
  const detailCacheRef = useRef({})
  const [toast, setToast] = useState(null)
  const [toastVisible, setToastVisible] = useState(false)
  const [toastPersistent, setToastPersistent] = useState(false)
  const [toastDuration, setToastDuration] = useState(5500)
  const shownToastsRef = useRef(new Set())
  const persistentMsgRef = useRef(null)
  const justCompletedRSRef = useRef(null)

  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  const onConnect = (params) => setEdges((eds) => addEdge(params, eds))

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
  }

  function showTimedToast(message, duration = 5500) {
    if (timerRef.current) clearTimeout(timerRef.current)
    setToast(message)
    setToastDuration(duration)
    setToastPersistent(false)
    setToastVisible(true)
    timerRef.current = setTimeout(() => setToastVisible(false), duration)
  }

  function showPersistentToast(message) {
    if (timerRef.current) clearTimeout(timerRef.current)
    setToast(message)
    setToastPersistent(true)
    setToastVisible(true)
    persistentMsgRef.current = message
  }

  function enqueueTyping(newChars) {
    typingQueueRef.current += newChars
    if (typingTimerRef.current) return  // 이미 돌고 있으면 큐에만 쌓음

    typingTimerRef.current = setInterval(() => {
      if (!typingQueueRef.current) {
        clearInterval(typingTimerRef.current)
        typingTimerRef.current = null
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
      onChunk: (delta) => {
        const b = streamBuffers.current.get(nodeId)
        if (!b) return
        b.text += delta
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

  async function fetchAndRenderTree(stageId) {
    const treeData = await getStepTree(projectId, stageId)
    const stage = stages.find((s) => s.stage_id === stageId)
    const { nodes: n, edges: e } = flattenTree(treeData.steps ?? [], stage?.stage_sequence)

    const hasProgress = getStageProgressFromTree(n, e)
    stageHasProgressRef.current[stageId] = hasProgress

    setNodes(n)
    setEdges(e)

    const newNodeIds = new Set(n.map((node) => node.id))
    streamBuffers.current.forEach((buf, id) => {
      if (!newNodeIds.has(id)) {
        buf.stream?.abort()
        streamBuffers.current.delete(id)
      }
    })

    const acceptedRequiredNode = n.find(
      (node) => node.type === 'requiredStepNode' && node.data.status === 'ACCEPTED'
    )
    if (acceptedRequiredNode) {
      currentRequiredStepName.current = acceptedRequiredNode.data.label
    }

    n.filter((node) =>
      node.data.status === 'READY' &&
      node.type !== 'requiredStepNode' &&
      !streamBuffers.current.has(node.id)
    ).forEach(async (node) => {
      try {
        const detail = await getStepDetail(node.id)
        if (!detail?.mentoring) {
          startNodeStream(node.id)
        } else {
          streamBuffers.current.set(node.id, {
            text: detail.mentoring,
            isDone: true,
            stream: null,
            onUpdate: null,
            onComplete: null,
          })
        }
      } catch {
        startNodeStream(node.id)
      }
    })
    
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
    if (nodes.length < 4) {
      rfInstance.setViewport({ x: -10, y: 0, zoom: 1 }, { duration: 0 })
      return
    }
    
    ;(async () => {
      await rfInstance.fitView({ duration: 0, padding: 0.1 })
      const { y, zoom } = rfInstance.getViewport()
      rfInstance.setViewport({ x: 80 - 50 * zoom, y, zoom }, { duration: 200 })
    })()
  }, [nodes, rfInstance])

  useEffect(() => {
    if (!selectedStageId || !projectId) return
    shouldFitViewRef.current = true
    fetchAndRenderTree(selectedStageId)
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
    persistentMsgRef.current = null
    currentRequiredStepName.current = null
    lastCompletedRequiredStepRef.current = null
    shownToastsRef.current.clear()
  }, [selectedStageId])

  const activeStage = getLatestActiveStage(stages)
  const currentStageId = activeStage?.stage_id ?? null

  const uiStages = stages.map((s) => ({
    id: s.stage_id,
    sequence: s.stage_sequence,
    name: s.stage_name,
    englishName: STAGE_ENGLISH[s.stage_sequence] ?? '',
    status: activeStage?.stage_id === s.stage_id ? 'active'
      : s.stage_sequence < currentStageSequence ? 'completed'
      : 'locked',
  }))

  async function handleNodeClick(event, node) {
    if (selectedStep?.id === node.id) return
    clearStreamCallbacks()
    setSelectedStep(node)
    setStreamingText(null)

    if (detailCacheRef.current[node.id]) {
      setStepDetail(detailCacheRef.current[node.id])
    } else {
      setStepDetail(null)
    }

    const requestId = ++detailRequestRef.current
    const buf = streamBuffers.current.get(node.id)

    if (buf?.isDone) {
      setIsStreamMode(false)
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
        clearTyping()
        try {
          const detail = await getStepDetail(node.id)
          if (requestId !== detailRequestRef.current) return
          setStepDetail(detail)
          setStreamingText(null)
          detailCacheRef.current[node.id] = detail
        } catch {
          setStreamingText(null)
        }
      }
    } else {
      setIsStreamMode(false)
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

      let acceptResult
      try {
        acceptResult = await acceptStep(selectedStep.id)
      } catch (err) {
        if (err?.code !== 'STEP_ALREADY_ACCEPTED') {
          alert('Step 생성에 실패했어요. 다시 시도해주세요.')
          return
        }
      }

      // acceptResult 처리 부분
        const isRSComplete = acceptResult?.is_current_required_step_completed
        const isStageComplete = acceptResult?.is_current_stage_completed

        const prevRSName = currentRequiredStepName.current

        // 다이아몬드 진입 토스트
        if (selectedStep.type === 'requiredStepNode') {
          const stepName = selectedStep.data.label
          currentRequiredStepName.current = stepName
          lastCompletedRequiredStepRef.current = null

          const key = `enter_${selectedStep.id}`
          const overridePersistent = toastPersistent // 완료 토스트 떠있는 상태에서 진입
          if (!shownToastsRef.current.has(key) || overridePersistent) {
            shownToastsRef.current.add(key)
            if (justCompletedRSRef.current?.nextMsgTimer) {
              clearTimeout(justCompletedRSRef.current.nextMsgTimer)
              justCompletedRSRef.current = null
            }
            persistentMsgRef.current = `📌 ${stepName} 진행 중이에요`
            showTimedToast(`📌 ${stepName}이(가) 시작됐어요!`, 5500)
          }
        }

        clearStreamCallbacks()
        setStreamingText(null)

        const { nextRequiredStepName } = await fetchAndRenderTree(selectedStageId)

        // Stage 완료
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

        // 필수 Step 완료
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
                ? `다음 핵심 단계인 ${nextRequiredStepName}로 이동할 수 있어요!`
                : `다음 필수 Step으로 이동할 수 있어요!`
              persistentMsgRef.current = nextMsg

              showTimedToast(`🎉 ${name}이(가) 종료됐어요!`, 3000)
              const t = setTimeout(() => {
                showPersistentToast(nextMsg)
                justCompletedRSRef.current = null
              }, 3000)
              justCompletedRSRef.current = { name, nextMsgTimer: t }
            }
          }
        }

        // 롤백 후 RS 바뀐 경우 (skipRollback이거나 needsRollback이면서 RS가 바뀐 경우)
        if (skipRollback || needsRollback) {
          const newRSName = currentRequiredStepName.current
          if (newRSName && newRSName !== prevRSName && selectedStep.type !== 'requiredStepNode') {
            persistentMsgRef.current = `📌 ${newRSName} 진행 중이에요`
            showTimedToast(`↩️ ${newRSName} 단계로 돌아왔어요!`, 5500)
          }
        }

    } finally {
      setIsAccepting(false)
    }
  }


  function handleNodeContextMenu(event, node) {
    event.preventDefault()
    if (node.data?.status !== 'ACCEPTED') return
    setContextMenu({ x: event.clientX, y: event.clientY, node })
  }

  function handleKeepToggle(nodeId) {
    setNodes((nds) =>
      nds.map((n) =>
        n.id === nodeId
          ? { ...n, data: { ...n.data, keep: !n.data.keep } }
          : n
      )
    )
  }

  function handlePaneClick() {
    clearStreamCallbacks()
    clearTyping() 
    setSelectedStep(null)
    setStepDetail(null)
    setStreamingText(null)
  }

  async function handleShareOpen() {
    setShareModal(true)
    setShareLoading(true)
    try {
      const result = await createShare(projectId)
      setShareUrl(`${window.location.origin}/shared/${result.share_token}`)
    } catch {
      alert('공유 링크 생성에 실패했어요.')
      setShareModal(false)
    } finally {
      setShareLoading(false)
    }
  }

  function handleShareClose() {
    setShareModal(false)
    setShareUrl('')
    setShareCopied(false)
  }

  async function handleCopyUrl() {
    try {
      await navigator.clipboard.writeText(shareUrl)
      setShareCopied(true)
      setTimeout(() => setShareCopied(false), 2000)
    } catch {
      alert('복사에 실패했어요.')
    }
  }

  async function handleShareRevoke() {
    try {
      await deleteShare(projectId)
    } catch {
      alert('공유 중지에 실패했어요.')
      return
    }
    handleShareClose()
  }

  const selectedHasChildren = edges.some((e) => e.source === selectedStep?.id)

  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.logo} onClick={() => navigate('/projects')}>poco</span>
          <span className={styles.projectName}>{projectName}</span>
        </div>
        <div className={styles.headerRight}>
        <button
          className={styles.shareBtn}
          onClick={handleShareOpen}>
            공유하기
        </button>
        <div className={styles.avatar}>
          <HiOutlineUser size={20} />
        </div>
      </div>
      </header>

      <div className={styles.body}>
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

        <div className={styles.canvasWrapper}>
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
              <div className={styles.shareModalHeader}>
                <p className={styles.shareModalTitle}>캔버스 공유하기</p>
                <button className={styles.closeBtn} onClick={handleShareClose}>✕</button>
              </div>
              <p className={styles.shareModalDesc}>
                링크를 통해 다른 사람들에게 프로젝트 캔버스를 공유할 수 있습니다.<br />
                캔버스는 읽기전용으로 공유됩니다.
              </p>
              <div className={styles.shareLinkBox}>
                {shareLoading
                  ? <span className={styles.shareLinkPlaceholder}>링크를 생성하는 중이에요...</span>
                  : <input className={styles.shareLinkInput} value={shareUrl} readOnly />
                }
                <button className={styles.copyBtn} onClick={handleCopyUrl} disabled={shareLoading}>
                  {shareCopied ? <BsCheck size={18} /> : <BsLink45Deg size={18} />}
                </button>
              </div>
              <button className={styles.revokeBtn} onClick={handleShareRevoke}>
                공유 그만하기
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}