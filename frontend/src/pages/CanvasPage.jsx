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
import { getStepTree, getStepDetail, acceptStep, generateSteps, rollbackStep } from '../api/step'

import { STAGE_ENGLISH, flattenTree } from '../utils/canvasUtils'

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
  const [navCollapsed, setNavCollapsed] = useState(false)
  const [selectedStep, setSelectedStep] = useState(null)
  const [stepDetail, setStepDetail] = useState(null)
  const [contextMenu, setContextMenu] = useState(null)
  const [toast, setToast] = useState(null)
  const [toastVisible, setToastVisible] = useState(false)
  const [rfInstance, setRfInstance] = useState(null)
  const [rollbackModal, setRollbackModal] = useState(false)

  const timerRef = useRef(null)
  const currentRequiredStepName = useRef(null)
  const autoOpenedStageRef = useRef(null)

  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  const onConnect = (params) => setEdges((eds) => addEdge(params, eds))

  useEffect(() => {
    if (!projectId) return
    getStages(projectId).then((data) => {
      const list = data.stages ?? []
      setStages(list)
      const active = list.find(s => s.is_active)
      if (active) {
        setCurrentStageSequence(active.stage_sequence)
        setSelectedStageId(active.stage_id)
      }
    })
  }, [projectId])

  async function fetchAndRenderTree(stageId) {
    const treeData = await getStepTree(projectId, stageId)
    const stage = stages.find((s) => s.stage_id === stageId)
    const { nodes: n, edges: e } = flattenTree(treeData.steps ?? [], stage?.stage_sequence)
    setNodes(n)
    setEdges(e)

    if (autoOpenedStageRef.current !== stageId) {
      const firstRequired = n.find((node) => node.type === 'requiredStepNode')
      if (firstRequired) {
        autoOpenedStageRef.current = stageId
        setSelectedStep(firstRequired)
        setStepDetail(null)
        try {
          const detail = await getStepDetail(firstRequired.id)
          setStepDetail(detail)
        } catch {}
      }
    }
  }

  useEffect(() => {
    if (!rfInstance || nodes.length === 0) return
    if (nodes.length >= 4) {
      ;(async () => {
        await rfInstance.fitView({ duration: 0, padding: 0.1 })
        const { y, zoom } = rfInstance.getViewport()
        rfInstance.setViewport({ x: 80 - 50 * zoom, y, zoom }, { duration: 200 })
      })()
    }
  }, [nodes, rfInstance])

  useEffect(() => {
    if (!selectedStageId || !projectId) return
    fetchAndRenderTree(selectedStageId)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedStageId, projectId])

  useEffect(() => {
    setSelectedStep(null)
    setStepDetail(null)
    autoOpenedStageRef.current = null
  }, [selectedStageId])

  const uiStages = stages.map(s => ({
    id: s.stage_id,
    sequence: s.stage_sequence,
    name: s.stage_name,
    englishName: STAGE_ENGLISH[s.stage_sequence] ?? '',
    status: s.is_active ? 'active'
      : s.stage_sequence < currentStageSequence ? 'completed'
      : 'locked',
  }))

  const currentStageId = stages.find(s => s.is_active)?.stage_id ?? null
  const targetSeq = stages.find(s => s.stage_id === selectedStageId)?.stage_sequence ?? 0
  const currentSeq = stages.find(s => s.stage_id === currentStageId)?.stage_sequence ?? 0
  const stagesToClear = uiStages
    .filter(s => s.sequence > targetSeq && s.sequence <= currentSeq)
    .map(s => s.sequence)
    .join(', ')

  async function handleNodeClick(event, node) {
    setSelectedStep(node)
    setStepDetail(null)
    try {
      const detail = await getStepDetail(node.id)
      setStepDetail(detail)
    } catch {
      // 상세 정보 로드 실패해도 노드 선택은 유지
    }
  }

  async function handleAccept() {
    if (!selectedStep) return

    if (selectedStageId !== currentStageId) {
      setRollbackModal(selectedStageId)
      return
    }

    await executeAccept()
  }

  async function handleRollbackConfirm() {
    setRollbackModal(null)
    currentRequiredStepName.current = null

    await executeAccept()

    const data = await getStages(projectId)
    const list = data.stages ?? []
    setStages(list)
    const active = list.find(s => s.is_active)
    if (active) {
      setCurrentStageSequence(active.stage_sequence)
      setSelectedStageId(active.stage_id)
    }
  }

  function findRequiredStep(nodeId) {
    const parentEdge = edges.find(e => e.target === nodeId)
    if (!parentEdge) return null
    const parentNode = nodes.find(n => n.id === parentEdge.source)
    if (!parentNode) return null
    if (parentNode.type === 'requiredStepNode') return parentNode
    return findRequiredStep(parentNode.id)
  }

  async function executeAccept() {
    if (selectedStep.data?.status === 'CANCELED') {
      try {
        await rollbackStep(selectedStep.id)
      } catch (err) {
        const msg =
          err?.code === 'INVALID_ROLLBACK_TARGET'
            ? '자식 Step이 있는 노드는 롤백할 수 없어요.\n마지막 Step을 선택해주세요.'
            : '롤백에 실패했어요. 다시 시도해주세요.'
        alert(msg)
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

    if (acceptResult?.is_current_required_step_completed) {
      const requiredNode = selectedStep.type === 'requiredStepNode'
        ? selectedStep
        : findRequiredStep(selectedStep.id)
      const name = requiredNode?.data?.label
      if (name) {
        const isStageComplete = acceptResult?.is_current_stage_completed
        const message = isStageComplete
          ? `✅ ${name}이(가) 종료됐어요. 이제 다음 스테이지로 이동할 수 있어요.`
          : `✅ ${name}이(가) 종료됐어요!`
        if (timerRef.current) clearTimeout(timerRef.current)
        setToast(message)
        setToastVisible(true)
        timerRef.current = setTimeout(() => setToastVisible(false), 3000)
        if (isStageComplete) {
          getStages(projectId).then((data) => {
            const list = data.stages ?? []
            setStages(list)
            const active = list.find(s => s.is_active)
            if (active) setCurrentStageSequence(active.stage_sequence)
          })
        }
      }
    }

    let retryCount = 0
    while (retryCount < 3) {
      try {
        await generateSteps(selectedStep.id)
        break
      } catch {
        retryCount++
        if (retryCount === 3) {
          alert('Step 생성에 실패했어요. 다시 시도해주세요.')
          return
        }
      }
    }

    if (selectedStep.type === 'requiredStepNode') {
      currentRequiredStepName.current = selectedStep.data.label
      if (timerRef.current) clearTimeout(timerRef.current)
      setToast(`📌 ${selectedStep.data.label}이(가) 시작됐어요!`)
      setToastVisible(true)
      timerRef.current = setTimeout(() => setToastVisible(false), 3000)
    }

    await fetchAndRenderTree(selectedStageId)
    setSelectedStep(null)
    setStepDetail(null)
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
    setSelectedStep(null)
    setStepDetail(null)
  }

  const selectedHasChildren = edges.some(e => e.source === selectedStep?.id)

  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.logo} onClick={() => navigate('/projects')}>poco</span>
          <span className={styles.projectName}>{projectName}</span>
        </div>
        <div className={styles.headerRight}>
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
          onSelectStage={(id) => setSelectedStageId(id)}
          collapsed={navCollapsed}
          onToggle={() => setNavCollapsed(!navCollapsed)}
        />

        <div className={styles.canvasWrapper}>
          <ToastAlarm
            message={toast}
            visible={toastVisible}
            onToggle={() => {
              const next = !toastVisible
              setToastVisible(next)
              if (next) {
                if (currentRequiredStepName.current) {
                  setToast(`📌 ${currentRequiredStepName.current} 진행 중이에요`)
                }
                if (timerRef.current) clearTimeout(timerRef.current)
                timerRef.current = setTimeout(() => setToastVisible(false), 3000)
              }
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
          isOpen={!!selectedStep}
          hasChildren={selectedHasChildren}
          onClose={() => { setSelectedStep(null); setStepDetail(null) }}
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
          <div className={styles.overlay} onClick={() => setRollbackModal(null)}>
            <div className={styles.modal} onClick={e => e.stopPropagation()}>
              <div className={styles.iconWrap}>⚠️</div>
              <p className={styles.title}>선택한 Step으로 돌아가시겠습니까?</p>
              <p className={styles.desc}>
                stage {stagesToClear}의 모든 진행 내역이 삭제됩니다. 계속 하시겠습니까?
              </p>
              <div className={styles.actions}>
                <button className={styles.cancelBtn} onClick={() => setRollbackModal(null)}>
                  취소
                </button>
                <button className={styles.rollbackBtn} onClick={handleRollbackConfirm}>
                  롤백하기
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}