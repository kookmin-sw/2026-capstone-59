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
    data: {
      label: '결과 분석 및 결함 기록',
      status: 'ACCEPTED',
      stageNumber: 1,
      is_required: true,
      mentoring: `### 📖 Step 설명

이 Step에서는 프로젝트가 해결하려는 **문제** 또는 포착하려는 **기회**를 명확하게 정의합니다.

중요한 것은 단순히 “이런 서비스가 있으면 좋겠다”가 아니라, **무엇이 문제인지**, **누가 어떤 상황에서 불편을 겪는지**, **왜 이 문제가 중요한지**를 분명하게 정리하는 것입니다.

이 Step은 이후 사용자 분석, 컨셉 정의, 요구사항 정리의 출발점이 되므로, 문제를 가능한 한 구체적인 문장으로 설명할 수 있어야 합니다.

---

### 👀 생각해보면 좋은 관점

- 해결하려는 문제 또는 기회를 한두 문장으로 설명할 수 있는가?
- 이 문제가 왜 중요한지 설명할 수 있는가?
- 이 문제가 주로 어떤 상황이나 맥락에서 발생하는지 알고 있는가?
- 현재 사람들이 사용하는 방식이나 기존 대안에는 어떤 한계가 있는가?

---

### 🎯 이 Step의 목표

- [ ]  문제/기회를 구체적으로 설명할 수 있다.
- [ ]  문제의 중요도 또는 해결 가치를 말할 수 있다.
- [ ]  문제의 발생 배경이나 상황을 설명할 수 있다.
- [ ]  기존 대안의 한계 또는 미해결 지점을 정리할 수 있다.

---

### ⚠️ 자주 하는 실수 ⚠️

#### 1. 문제를 너무 넓게 쓰기

- ❌ “프로젝트 관리가 어렵다”
- ✅ “프로젝트 경험이 없는 대학생 팀은 초기 기획 단계에서 무엇부터 해야 할지 몰라 많은 시간을 낭비한다”

문제는 가능한 한 **대상과 상황이 드러나게** 적는 것이 좋습니다.

#### 2. 해결책을 먼저 정해두기

이 Step은 “무엇을 만들까?”보다 먼저, “왜 이것이 필요한가?”를 분명히 하는 단계입니다.

#### 3. 문제의 중요도를 설명하지 않기

문제가 있다는 사실만으로는 부족합니다. 왜 해결할 가치가 있는지 함께 설명해야 설득력이 생깁니다.

#### 4. 현재 방식의 한계를 놓치기

이미 사람들이 다른 방식으로 문제를 해결하고 있을 수 있습니다. 그 방식이 왜 충분하지 않은지도 함께 봐야 합니다.

---

### ✅ 한 줄 팁

이 Step에서는 해결책을 서두르기보다, **문제 자체를 선명하게 설명하는 것**에 집중해보세요.`,
      terms: `**TAM / SAM / SOM**\n\n전체 시장 규모(TAM), 접근 가능한 시장(SAM), 실제 목표 시장(SOM).\n\n---\n\n**페인 포인트 (Pain Point)**\n\n사용자가 현재 겪고 있는 불편함이나 해결되지 않은 문제.`,
      artifact: {
        description: "아이디어 목록 및 선정 근거 문서",
        notion_template_url: "https://notion.so"
      },
    },
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
    data: {
      label: '브레인 스토밍 수행',
      status: 'ACCEPTED',
      stageNumber: 1,
      keep: true },
  },
  {
    id: 'step-3',
    type: 'stepNode',
    position: { x: 280, y: 270 },
    data: {
      label: '시장 조사 분석',
      status: 'READY',
      stageNumber: 1,
      is_required: false,
      mentoring: `### 📖 Step 설명

이 Step에서는 현재 시장에 어떤 서비스, 제품, 방식이 있는지 조사하고, 기존 대안이 어떤 점에서는 잘 작동하고 어떤 점에서는 부족한지 파악합니다.

중요한 것은 단순히 경쟁사를 나열하는 것이 아니라, **기존 대안의 빈틈**과 **우리 아이디어가 들어갈 수 있는 기회**를 찾는 것입니다.

---

### 🔥 추천 방법

#### 1. 경쟁 서비스 찾아보기

비슷한 문제를 해결하는 서비스나 제품을 3~5개 정도 찾아보세요.

이때 중요한 것은 “있다/없다”가 아니라, 각 서비스가 **누구를 위한 것인지, 무슨 기능을 제공하는지, 무엇을 강점으로 내세우는지** 를 정리하는 것입니다.

#### 2. 사용자 리뷰 찾아보기

앱스토어 리뷰, 커뮤니티 글, 블로그 후기, 유튜브 댓글 등을 보면 실제 사용자가 **무엇을 좋아하고 무엇을 불편해하는지** 알 수 있습니다.

리뷰를 볼 때는 그냥 읽고 넘기지 말고, 반복적으로 나오는 내용을 모아보세요.

반복되는 불만은 **시장의 빈틈**일 가능성이 큽니다.

#### 3. 현재의 대안 찾아보기

경쟁 앱뿐 아니라 노션, 엑셀, 카톡처럼 사람들이 지금 실제로 어떤 방식으로 문제를 해결하고 있는지도 보세요.

이런 방식은 **“경쟁 서비스”** 는 아닐 수 있지만, 실제로는 **가장 강력한 현재 대안**일 수 있습니다.

#### 4. 차별점 한 줄로 정리하기

조사 후에는 **“기존 방식은 ~하지만, 우리는 ~를 제공한다”** 형식으로 차별점을 정리해보세요.

이 한 줄이 이후 핵심 컨셉 정의로 자연스럽게 이어집니다.

---

### ⚠️ 자주 하는 실수

#### 1. 서비스 이름만 모으고 끝내기

경쟁사를 찾는 것 자체가 목적이 아닙니다. 각 서비스가 무엇을 잘하고, 무엇이 부족한지까지 봐야 의미가 있습니다.

#### 2. 기능만 보고 사용자 반응은 안 보기

겉으로 보기엔 좋아 보여도 실제 사용자는 불편할 수 있습니다. 리뷰나 후기에서 반복되는 문제를 꼭 확인해보세요.

#### 3. 차별점을 막연하게 쓰기

- ❌ “우리는 더 편리하다”
- ✅ “기존 서비스는 초보자를 위한 단계별 안내가 부족하지만, 우리는 단계별 AI 멘토링을 제공한다”

#### 4. 조사 결과를 문제 정의와 연결하지 않기

시장 조사는 따로 노는 작업이 아니라, 우리가 정의한 문제를 더 분명하게 만들기 위한 과정입니다.

---

### ✅ 한 줄 팁

시장 조사의 핵심은 경쟁사 존재 여부가 아니라, **기존 대안이 놓치고 있는 문제와 우리가 들어갈 수 있는 틈을 찾는 것**입니다.`,
      terms: `**TAM / SAM / SOM**\n\n전체 시장 규모(TAM), 접근 가능한 시장(SAM), 실제 목표 시장(SOM).\n\n---\n\n**페인 포인트 (Pain Point)**\n\n사용자가 현재 겪고 있는 불편함이나 해결되지 않은 문제.`,
    },
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

    
        <SidePanel
          step={selectedStep}
          isOpen={!!selectedStep}
          onClose={() => setSelectedStep(null)}
          onAccept={() => setSelectedStep(null)}
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