import { useState, useEffect } from 'react'
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
import { getStepTree, acceptStep, generateSteps } from '../api/step'

import { X_GAP, Y_GAP, STAGE_ENGLISH, makeEdge, flattenTree } from '../utils/canvasUtils'

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

  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  const onConnect = (params) => setEdges((eds) => addEdge(params, eds))

  // Stage 목록 조회
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

  // Step 트리 조회
  useEffect(() => {
    if (!selectedStageId || !projectId) return
    const stage = stages.find(s => s.stage_id === selectedStageId)
    getStepTree(projectId, selectedStageId).then((data) => {
      const { nodes: n, edges: e } = flattenTree(
        data.steps ?? [],
        stage?.stage_sequence
      )
      setNodes(n)
      setEdges(e)
    })
  }, [selectedStageId])

  // Stage UI 포맷 변환
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

  async function handleNodeClick(event, node) {
    setSelectedStep(node)
    setStepDetail(null)
    // const detail = await getStep(node.id)
    // setStepDetail(detail)
  }

  async function handleAccept() {
    if (!selectedStep) return

    let acceptResult
    try {
      acceptResult = await acceptStep(selectedStep.id)
    } catch {
      alert('Step 저장에 실패했어요. 다시 시도해주세요.')
      return
    }

    // 필수 Step Accept 시 "시작" 토스트
    if (selectedStep.type === 'requiredStepNode') {
      setToast(`📌 ${selectedStep.data.label}이(가) 시작됐어요!`)
      setToastVisible(true)
      setTimeout(() => setToastVisible(false), 3000)
    }

    // 필수 Step 완료 시 "종료" 토스트
    if (acceptResult?.is_current_required_step_completed) {
      setToast(`✅ ${selectedStep.data.label}이(가) 종료됐어요!`)
      setToastVisible(true)
      setTimeout(() => setToastVisible(false), 3000)
    }

    setNodes((nds) =>
      nds.map((n) =>
        n.id === selectedStep.id
          ? { ...n, data: { ...n.data, status: 'ACCEPTED' } }
          : n
      )
    )

    let data
    let retryCount = 0
    while (retryCount < 3) {
      try {
        data = await generateSteps(selectedStep.id)
        break
      } catch {
        retryCount++
        if (retryCount === 3) {
          alert('AI Step 생성에 실패했어요. 잠시 후 다시 시도해주세요.')
          return
        }
      }
    }

    const stage = stages.find(s => s.stage_id === selectedStageId)
    const newNodes = (data.generated_steps ?? []).map((s, i) => ({
      id: s.step_id,
      type: s.is_required ? 'requiredStepNode' : 'stepNode',
      position: {
        x: selectedStep.position.x + X_GAP,
        y: selectedStep.position.y + (i - 1) * Y_GAP,
      },
      data: {
        label: s.name,
        status: s.status,
        is_required: s.is_required,
        stageNumber: stage?.stage_sequence,
      },
    }))
    const newEdges = (data.generated_steps ?? []).map(s => makeEdge(selectedStep.id, s.step_id))
    setNodes(prev => [...prev, ...newNodes])
    setEdges(prev => [...prev, ...newEdges])
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
              if (next) setTimeout(() => setToastVisible(false), 3000)
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
            fitView
            minZoom={0.3}
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
      </div>
    </div>
  )
}