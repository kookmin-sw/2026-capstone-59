import { useState, useCallback } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import {
  ReactFlow,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  addEdge,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import StageNavigator from '../components/canvas/StageNavigator'
import SidePanel from '../components/canvas/SidePanel'
import ToastAlarm from '../components/canvas/ToastAlarm'
import ContextMenu from '../components/canvas/onNodeContext'
import StepNode from '../components/canvas/StepNode'
import RequiredStepNode from '../components/canvas/RequiredStepNode'

import styles from './CanvasPage.module.css'
import { HiOutlineUser } from 'react-icons/hi'

const nodeTypes = {
  stepNode: StepNode,
  requiredStepNode: RequiredStepNode,
}

const DUMMY_STAGES = [
  { id: 1, sequence: 1, name: '아이디어 구체화', englishName: 'Ideation', status: 'completed' },
  { id: 2, sequence: 2, name: '프로젝트 계획', englishName: 'Planning', status: 'completed' },
  { id: 3, sequence: 3, name: '요구사항 정의', englishName: 'Requirement', status: 'active' },
  { id: 4, sequence: 4, name: '설계', englishName: 'Design', status: 'locked' },
  { id: 5, sequence: 5, name: '개발', englishName: 'Development', status: 'locked' },
  { id: 6, sequence: 6, name: '테스트 및 검증', englishName: 'Test', status: 'locked' },
]

const INITIAL_NODES = [
  {
    id: 'req-1',
    type: 'requiredStepNode',
    position: { x: 500, y: 200 },
    data: { label: '결과 분석 및 결함 기록' },
  },
  {
    id: 'step-1',
    type: 'stepNode',
    position: { x: 50, y: 150 },
    data: { label: '사용자 인터뷰 계획 세우기', status: 'ACCEPTED', stageNumber: 1 },
  },
  {
    id: 'step-2',
    type: 'stepNode',
    position: { x: 280, y: 80 },
    data: { label: '브레인 스토밍 수행', status: 'ACCEPTED', stageNumber: 1, keep: true },
  },
  {
    id: 'step-3',
    type: 'stepNode',
    position: { x: 280, y: 270 },
    data: { label: '시장 조사 분석', status: 'READY', stageNumber: 1 },
  },
]

const INITIAL_EDGES = []

export default function CanvasPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const projectName = location.state?.projectName ?? 'Project'

  const [currentStageId, setCurrentStageId] = useState(3)
  const [selectedStageId, setSelectedStageId] = useState(3)
  const [navCollapsed, setNavCollapsed] = useState(false)
  const [selectedStep, setSelectedStep] = useState(null)
  const [contextMenu, setContextMenu] = useState(null)
  const [toast, setToast] = useState(null)
  const [toastVisible, setToastVisible] = useState(true)

  const [nodes, setNodes, onNodesChange] = useNodesState(INITIAL_NODES)
  const [edges, setEdges, onEdgesChange] = useEdgesState(INITIAL_EDGES)

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    []
  )

  function handleNodeClick(event, node) {
    setSelectedStep(node)
    if (node.type === 'requiredStepNode') {
      setToast('아이디어를 구체화 하기 위한 문제 정의를 시작합니다!')
      setToastVisible(true)
      setTimeout(() => setToastVisible(false), 3000)
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
    setSelectedStep(null)
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
          stages={DUMMY_STAGES}
          currentStageId={currentStageId}
          selectedStageId={selectedStageId}
          onSelectStage={(id) => setSelectedStageId(id)}
          collapsed={navCollapsed}
          onToggle={() => setNavCollapsed(!navCollapsed)}
        />

        <div className={styles.canvasWrapper}>
          {toast && (
            <ToastAlarm
              message={toast}
              visible={toastVisible}
              onToggle={() => setToastVisible(!toastVisible)}
            />
          )}

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
            <Controls position="bottom-center" />
          </ReactFlow>
        </div>

        {selectedStep && (
          <SidePanel
            step={selectedStep}
            onClose={() => setSelectedStep(null)}
            onAccept={() => setSelectedStep(null)}
          />
        )}

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