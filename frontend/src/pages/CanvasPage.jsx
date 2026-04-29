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
// import { getStep } from '../api/step'


import styles from './CanvasPage.module.css'
import { HiOutlineUser } from 'react-icons/hi'

const nodeTypes = {
  stepNode: StepNode,
  requiredStepNode: RequiredStepNode,
}

const STAGE_ENGLISH = {
  1: 'Ideation', 2: 'Planning', 3: 'Requirement',
  4: 'Design', 5: 'Development', 6: 'Test',
}

const X_GAP = 300
const Y_GAP = 120

function flattenTree(steps, stageSequence) {
  const nodes = []
  const edges = []

  function build(node, depth, centerY) {
    nodes.push({
      id: node.step_id,
      type: node.is_required ? 'requiredStepNode' : 'stepNode',
      position: {
        x: depth * X_GAP + 50,
        y: centerY,
      },
      data: {
        label: node.name,
        status: node.status,
        is_required: node.is_required,
        stageNumber: stageSequence,
        step_id: node.step_id,
      },
    })

    if (node.parent_step_id) {
      edges.push({
        id: `e-${node.parent_step_id}-${node.step_id}`,
        source: node.parent_step_id,
        target: node.step_id,
        type: 'straight',
        style: {
          stroke: '#291C80',
          strokeWidth: 1.5,
          strokeDasharray: '5,5',
        },
      })
    }

    const children = node.children ?? []
    const count = children.length

    if (count === 0) return

    const totalHeight = (count - 1) * Y_GAP
    const startY = centerY - totalHeight / 2

    children.forEach((child, index) => {
      const childY = startY + index * Y_GAP
      build(child, depth + 1, childY)
    })
  }

  const rootGap = 260
  const totalRootHeight = (steps.length - 1) * rootGap
  const rootStartY = 200 - totalRootHeight / 2

  steps.forEach((root, index) => {
    const rootY = rootStartY + index * rootGap
    build(root, 0, rootY)
  })

  return { nodes, edges }
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
    setToast(`📌 ${node.data.label}을(를) 시작합니다!`)
    if (node.type === 'requiredStepNode') {
      // setToast(`📌 ${detail.name}을(를) 시작합니다!`)
      setToastVisible(true)
      setTimeout(() => setToastVisible(false), 3000)
    }
  }

  async function handleAccept() {
    if (!selectedStep) return

    try {
      await acceptStep(selectedStep.id)
    } catch {
      alert('Step 저장에 실패했어요. 다시 시도해주세요.')
      return
    }

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
    const newEdges = (data.generated_steps ?? []).map(s => ({
      id: `e-${selectedStep.id}-${s.step_id}`,
      source: selectedStep.id,
      target: s.step_id,
    }))
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