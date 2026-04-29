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
import StepNode from '../components/canvas/StepNode'
import RequiredStepNode from '../components/canvas/RequiredStepNode'

import styles from './CanvasPage.module.css'
import { HiOutlineUser } from 'react-icons/hi'

const nodeTypes = {
  stepNode: StepNode,
  requiredStepNode: RequiredStepNode,
}

const DUMMY_STAGES = [
  { id: 1, name: '아이디어 구체화', englishName: 'Ideation', status: 'completed' },
  { id: 2, name: '프로젝트 계획', englishName: 'Planning', status: 'completed' },
  { id: 3, name: '요구사항 정의', englishName: 'Requirement', status: 'active' },
  { id: 4, name: '설계', englishName: 'Design', status: 'locked' },
  { id: 5, name: '개발', englishName: 'Development', status: 'locked' },
  { id: 6, name: '테스트 및 검증', englishName: 'Test', status: 'locked' },
]

const INITIAL_NODES = [
  {
    id: 'req-1',
    type: 'requiredStepNode',
    position: { x: 100, y: 150 },
    data: { label: '문제/기회 정의', status: 'ready' },
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
            nodeTypes={nodeTypes}
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
      </div>
    </div>
  )
}