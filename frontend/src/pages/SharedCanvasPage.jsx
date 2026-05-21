import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ReactFlow, Background, Controls,
  useNodesState, useEdgesState,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import StageNavigator from '../components/canvas/StageNavigator'
import StepNode from '../components/canvas/StepNode'
import RequiredStepNode from '../components/canvas/RequiredStepNode'
import SidePanel from '../components/canvas/SidePanel'

import { getSharedProject, getSharedStages, getSharedStepTree, getSharedStepDetail } from '../api/shared'
import { STAGE_ENGLISH, flattenTree, getLatestActiveStage } from '../utils/canvasUtils'

import styles from './CanvasPage.module.css'

const nodeTypes = {
  stepNode: StepNode,
  requiredStepNode: RequiredStepNode,
}

export default function SharedCanvasPage() {
  const { shareToken } = useParams()
  const navigate = useNavigate()

  const [project, setProject] = useState(null)
  const [stages, setStages] = useState([])
  const [selectedStageId, setSelectedStageId] = useState(null)
  const [currentStageSequence, setCurrentStageSequence] = useState(1)
  const [navCollapsed, setNavCollapsed] = useState(false)
  const [rfInstance, setRfInstance] = useState(null)
  const [error, setError] = useState(false)
  const [selectedStep, setSelectedStep] = useState(null)
  const [stepDetail, setStepDetail] = useState(null)
  const [projectInfoOpen, setProjectInfoOpen] = useState(false)

  const shouldFitViewRef = useRef(false)
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  async function handleNodeClick(event, node) {
    setSelectedStep(node)
    setStepDetail(null)
    try {
      const detail = await getSharedStepDetail(shareToken, node.id)
      setStepDetail(detail)
    } catch {
      //
    }
  }

  useEffect(() => {
    if (!shareToken) return
    Promise.all([
      getSharedProject(shareToken),
      getSharedStages(shareToken),
    ]).then(([projectData, stagesData]) => {
      setProject(projectData)
      const list = stagesData.stages ?? []
      setStages(list)
      const latestActive = getLatestActiveStage(list)
      if (latestActive) {
        setCurrentStageSequence(latestActive.stage_sequence)
        setSelectedStageId(latestActive.stage_id)
      }
    }).catch(() => setError(true))
  }, [shareToken])

  useEffect(() => {
    if (!selectedStageId || !shareToken || stages.length === 0) return
    shouldFitViewRef.current = true
    const stage = stages.find((s) => s.stage_id === selectedStageId)
    getSharedStepTree(shareToken, selectedStageId).then((treeData) => {
      const { nodes: n, edges: e } = flattenTree(treeData.steps ?? [], stage?.stage_sequence)
      setNodes(n)
      setEdges(e)
    }).catch(() => {})
  }, [selectedStageId, shareToken, stages, setNodes, setEdges])

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

  const activeStage = getLatestActiveStage(stages)
  const currentStageId = activeStage?.stage_id ?? null

  const uiStages = stages.map((s) => ({
    id: s.stage_id,
    sequence: s.stage_sequence,
    name: s.stage_name,
    englishName: STAGE_ENGLISH[s.stage_sequence] ?? '',
    status: s.is_completed ? 'completed'
      : activeStage?.stage_id === s.stage_id ? 'active'
      : s.stage_sequence < currentStageSequence ? 'completed'
      : 'locked',
  }))

  if (error) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', flexDirection: 'column', gap: 12 }}>
        <p style={{ fontSize: 15, color: '#666' }}>유효하지 않은 공유 링크예요.</p>
        <button
          onClick={() => navigate('/')}
          style={{ padding: '8px 16px', borderRadius: 8, border: '1px solid #EEEDF8', cursor: 'pointer', fontSize: 13 }}
        >
          홈으로
        </button>
      </div>
    )
  }

  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <object data="/poco-logo-text.svg" alt="poco" height={25} onClick={() => navigate('/')}></object>
          <span>|</span>
          <span className={styles.projectName}>{project?.name ?? ''}</span>
          <span className={styles.readOnlyBadge}>view only</span>
        </div>

        <div className={styles.headerRight}>
          <button
            type="button"
            className={styles.shareBtn}
            onClick={() => setProjectInfoOpen(true)}
          >
            프로젝트 정보
          </button>
        </div>
      </header>

      <div className={styles.body}>
        <StageNavigator
          stages={uiStages}
          currentStageId={currentStageId}
          selectedStageId={selectedStageId}
          onSelectStage={(id) => setSelectedStageId(id)}
          collapsed={navCollapsed}
          onToggle={() => setNavCollapsed((v) => !v)}
        />

        <div className={styles.canvasWrapper}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={handleNodeClick}
            nodeTypes={nodeTypes}
            nodesDraggable={false}
            nodesConnectable={false}
            onInit={setRfInstance}
            defaultViewport={{ x: -10, y: 0, zoom: 1 }}
            minZoom={0.01}
            maxZoom={2}
          >

          <SidePanel
            step={selectedStep}
            detail={stepDetail}
            streamingText={null}
            isOpen={!!selectedStep}
            isAccepting={false}
            isStreamMode={false}
            hasChildren={false}
            onClose={() => {
              setSelectedStep(null)
              setStepDetail(null)
            }}
          />
            <Background variant="dots" gap={24} size={1.5} color="#C8C4E8" />
            <Controls position="bottom-center" showInteractive={false} />
          </ReactFlow>
        </div>
      </div>
      {projectInfoOpen && (
        <div className={styles.overlay} onClick={() => setProjectInfoOpen(false)}>
          <div className={styles.sharedInfoModal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.sharedInfoHeader}>
              <p className={styles.sharedInfoTitle}>프로젝트 정보</p>
              <button
                type="button"
                className={styles.closeBtn}
                onClick={() => setProjectInfoOpen(false)}
                aria-label="닫기"
              >
                ✕
              </button>
            </div>

            <div className={styles.sharedInfoTable}>
              <div className={styles.sharedInfoRow}>
                <span className={styles.sharedInfoLabel}>프로젝트 이름</span>
                <span className={styles.sharedInfoValue}>{project?.name || '-'}</span>
              </div>

              <div className={styles.sharedInfoRow}>
                <span className={styles.sharedInfoLabel}>프로젝트 설명</span>
                <span className={styles.sharedInfoValue}>{project?.description || '-'}</span>
              </div>

              <div className={styles.sharedInfoRow}>
                <span className={styles.sharedInfoLabel}>프로젝트 인원</span>
                <span className={styles.sharedInfoValue}>
                  {project?.member_count ? `${project.member_count}명` : '-'}
                </span>
              </div>

              <div className={styles.sharedInfoRow}>
                <span className={styles.sharedInfoLabel}>프로젝트 기간</span>
                <span className={styles.sharedInfoValue}>
                  {project?.duration_month === 0
                    ? '기간 없음'
                    : project?.duration_month
                    ? `약 ${project.duration_month}개월`
                    : '-'}
                </span>
              </div>

              <div className={styles.sharedInfoRow}>
                <span className={styles.sharedInfoLabel}>제약 사항</span>
                <span className={styles.sharedInfoValue}>
                  {project?.constraints?.length ? project.constraints.join(', ') : '-'}
                </span>
              </div>
            </div>

            <div className={styles.sharedPromptSection}>
              <p className={styles.sharedPromptLabel}>프로젝트 프롬프트</p>
              <p className={styles.sharedPromptText}>{project?.prompt || '-'}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}