```markdown
# Poco Frontend

Vite + React 기반의 SPA 프론트엔드.
React Flow(@xyflow/react)로 Step 트리를 시각화하고, d3-flextree로 tidy tree 레이아웃을 계산하며, Framer Motion으로 전환 애니메이션을 처리한다.
사이드패널 콘텐츠는 백엔드의 비동기 폴링 구조에 맞춰 적응형 폴링 + 점진 렌더링으로 표시한다.

```

## 1. 실행 방법

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 (포트 5173)
npm run dev

# 프로덕션 빌드
npm run build

# 빌드 결과 미리보기
npm run preview
```

개발 서버는
- `/api` → `http://localhost:8000` (Business API)
- `/ai`  → `http://localhost:8001` (AI Orchestrator)
로 프록시 설정이 돼 있어서 두 백엔드를 별도 CORS 설정 없이 연동할 수 있다.


## 2. 디렉토리 구조

```
frontend/
├── index.html
├── vite.config.js                 # Vite 설정 (dev proxy 포함)
├── package.json
│
└── src/
    ├── main.jsx                   # React 진입점 (ReactDOM.createRoot)
    ├── App.jsx                    # 라우터 설정 (react-router-dom)
    │
    ├── api/                       # Axios 기반 API 호출 모듈
    │   ├── auth.js                #   로그인 / OAuth
    │   ├── projects.js            #   Project CRUD / 공유 토큰
    │   ├── stage.js               #   Stage 조회
    │   ├── step.js                #   Step 생성·Accept·Rollback·Keep
    │   │                          #   + createSidePanelStream (적응형 폴링)
    │   └── exports.js             #   Design Export 스트림
    │
    ├── pages/                     # 라우트별 페이지 컴포넌트
    │   ├── LandingPage.jsx        #   서비스 소개 (/)
    │   ├── LoginPage.jsx          #   OAuth 로그인 (/login)
    │   ├── AuthCallbackPage.jsx   #   OAuth 콜백 (/auth/callback)
    │   ├── CreateProjectPage.jsx  #   프로젝트 생성 (/projects/create)
    │   ├── ProjectListPage.jsx    #   프로젝트 목록 (/projects)
    │   ├── TrashPage.jsx          #   휴지통 (/projects/trash)
    │   ├── CanvasPage.jsx         #   메인 캔버스 (/canvas/:projectId)
    │   └── SharedCanvasPage.jsx   #   공유 캔버스 (/shared/:shareToken)
    │
    ├── components/
    │   ├── PrivateRoute.jsx        # 인증 가드
    │   ├── OnboardingTour.jsx      # 첫 진입 가이드 투어
    │   │
    │   └── canvas/                 # 캔버스 페이지 전용 컴포넌트
    │       ├── StepNode.jsx            # 일반 Step 노드 (사각형)
    │       ├── RequiredStepNode.jsx    # 필수 Step 노드 (다이아몬드)
    │       ├── GhostNode.jsx           # 생성 대기용 ghost 노드
    │       ├── GhostEdge.jsx           # ghost 노드용 점선 엣지
    │       ├── NewEdge.jsx             # 새 노드 등장 시 자라나는 엣지
    │       ├── SidePanel.jsx           # Step 클릭 시 우측 패널
    │       ├── StageNavigator.jsx      # 좌측 Stage 목록 패널
    │       ├── ToastAlarm.jsx          # 상단 토스트 알림
    │       ├── MdExportModal.jsx       # 디자인 .md 내보내기 모달
    │       ├── DownloadNotification.jsx # 다운로드 상태 알림
    │       └── onNodeContext.jsx       # 노드 우클릭 컨텍스트 메뉴
    │
    ├── utils/
    │   └── canvasUtils.js          # 트리 레이아웃 (d3-flextree)
    │                               # + ghost 좌표 예측 (predictGhostPositions)
    │
    └── styles/
        └── global.css              # 전역 CSS (reset, 폰트, CSS 변수)
```


## 3. 개발 환경 세팅

### 사전 요구사항
- Node.js 20+
- npm 10+ (Node.js에 포함)

### 설치

```bash
cd frontend
npm install
```

### 환경 변수 파일
루트에 `.env` 파일 생성 (`.env.example` 참고):

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_AI_BASE_URL=http://localhost:8001
```

개발 서버에서는 `vite.config.js`의 proxy 설정으로 `/api`, `/ai` 경로가 자동 전달되기 때문에 환경 변수 없이도 로컬 개발이 가능.


## 4. 주요 라이브러리

| 라이브러리          | 버전 | 용도 |
|---|---|---|
| `react`            | 19  | UI 렌더링 |
| `react-router-dom` | 7   | SPA 라우팅 |
| `@xyflow/react`    | 12  | Step 트리 캔버스 |
| `d3-flextree`      | 2   | Walker tidy tree 레이아웃 |
| `framer-motion`    | 12  | 전환 애니메이션 |
| `axios`            | 1   | HTTP API 호출 |
| `react-markdown`   | 10  | 마크다운 렌더링 |
| `react-icons`      | 5   | 아이콘 |


## 5. 주요 페이지·컴포넌트 상세

### CanvasPage

메인 작업 화면. 핵심 상태와 로직이 집중돼 있다.

#### 주요 상태

| 상태/Ref | 역할 |
|---|---|
| `nodes` / `edges` | React Flow 노드·엣지 배열 |
| `selectedStep` | 현재 클릭된 노드 |
| `streamBuffers` (ref) | 노드 ID별 폴링 버퍼 Map (text · isDone · stream) |
| `ghostPositionsRef` | ghost 노드 예측 좌표 |
| `movedPositionsRef` | 기존 노드의 새 레이아웃 좌표 (ghost 단계에서 이동시킨 위치) |
| `requiredSlotRef` / `siblingRequiredIdRef` | 필수 Step 슬롯 좌표 · reparent 대상 추적 |
| `lastToastByStageRef` | Stage별 마지막 토스트 메모리 |
| `currentRequiredStepName` (ref) | 현재 진행 중인 필수 Step 이름 |

#### Step 선택 흐름
1. 노드 클릭 → `handleNodeClick`
2. `streamBuffers` 확인
   - `isDone` 이면 → DB(`getStepDetail`)에서 상세 로드
   - 폴링 중이면 → 기존 버퍼에 `onUpdate` / `onComplete` 콜백 연결
   - 없으면 → DB 로드

#### Step Accept 흐름 (ghost 노드 시스템)
1. Accept 클릭 → `executeAccept`
2. `predictGhostPositions` 로 d3-flextree를 미리 실행 → 새 자식 슬롯 4개(일반 3 + 필수 1) 좌표 계산
3. ghost 노드 3개 + 점선 엣지 즉시 표시, 기존 노드들도 4-slot 기준 새 위치로 이동
4. `acceptStep` API 호출 (백엔드에서 새 Step 3개 생성, 필요 시 필수 Step reparent)
5. `fetchAndRenderTree` 로 새 트리 받아 ghost → 실제 노드로 교체
6. ghost edge는 0.4초 fade out, 새 edge(`NewEdge`)는 `pathLength` 애니메이션으로 자라남

### SidePanel

Step 클릭 시 우측 패널.

#### 탭 구성

| Step 종류 | 탭 구성 |
|---|---|
| 일반 Step | AI Mentoring / Dictionary |
| 필수 Step | AI Mentoring / Dictionary / Template |

#### 콘텐츠 수신 — 비동기 폴링 (`createSidePanelStream`)
백엔드가 SSE → 비동기 폴링으로 전환됨에 따라 클라이언트도 폴링 기반으로 재구현되었다.

```
1. POST /steps/{id}/sidepanel-start    (fire-and-forget, 응답 안 기다림)
2. GET  /steps/{id}/sidepanel-content  (적응형 폴링)
3. is_complete=true 응답 시 onDone, 4xx/5xx 누적 시 onError
```

- **적응형 주기**: 새 chunk 도착 시 1초(`MIN_POLL_MS`), 변경 없음 2회 누적 시 1.5x씩 백오프 → 최대 4초(`MAX_POLL_MS`). 새 chunk 도착하면 다시 1초로 리셋.
- **에러 처리**: 4xx는 종료 신호로 즉시 중단, 5xx/네트워크 오류는 최대 5회 재시도.
- **서버 응답은 누적된 전체 content**(delta 아님) → 새로고침 후 폴링 재시작해도 중복 누적 없이 이어 받음.
- **abort()는 클라이언트 폴링만 중단** → 백엔드 작업은 끝까지 실행되어 RDS에 저장됨. 같은 Step 다시 클릭 시 끊김 없이 복원.

#### 점진 렌더링 — Typing Queue
폴링 주기가 1~4초로 비교적 길고 chunk 크기가 일정하지 않아, 받은 텍스트를 그대로 렌더링하면 "툭툭" 끊기는 인상을 준다. 이를 보완하기 위해 typing queue 레이어를 한 번 더 거치도록 했다.

- `typingQueueRef`에 신규 chunk 누적
- `setInterval`이 16ms마다 2글자씩 출력 → 일정한 타이핑 리듬 보장
- 폴링이 `is_complete`로 종료돼도 큐 비워질 때까지 대기 후 정적 뷰 전환 (`typingDrainCallbackRef`)

#### MentoringContent 렌더링 우선순위
1. `isLoading && !streamingText`
   - `isStreamMode` → `AllSkeleton`
   - 아니면 → `LoadingSpinner`
2. `streamingText` 있음
   → `StreamingStructuredView` (`TypewriterText`)
3. 로드 완료
   → 구조화된 정적 뷰


## 6. 캔버스 레이아웃 (canvasUtils.js)

d3-flextree 기반 Walker tidy tree 알고리즘으로 트리 좌표를 계산한다.

- **자식 순서 자동 보존** — Dagre와 달리 입력 순서대로 배치
- **노드 타입별 실제 높이** — `STEP_H=90`, `REQUIRED_H=130`을 `nodeSize`로 전달해 겹침 방지
- **4-slot phantom padding** — 모든 부모 노드의 자식 슬롯을 항상 4개(일반 3 + 필수 1)로 패딩해, 새 자식 생성 시 기존 노드 위치가 흔들리지 않게 함
- **`predictGhostPositions`** — accept 직후 d3-flextree를 미리 한 번 더 돌려 ghost 좌표를 결정론적으로 계산. ghost → 실제 노드 전환 시 점프 없음을 보장


## 7. 토스트 알림 (ToastAlarm)

| 트리거 | 메시지 |
|---|---|
| 필수 Step 진입 | `📌 X이/가 시작됐어요!` (5.5초 timed) + `🤔 X을/를 진행 중이에요!` (persistent) |
| 필수 Step 완료 | `🎉 X이/가 종료됐어요!` (3초) → `다음 단계 Y로 이동할 수 있어요!` (persistent) |
| Stage 완료 | `🎉 Stage가 종료됐어요!` (persistent) |
| Stage 간 롤백 | `📌 {Stage} 중 {RS}로 돌아왔어요!` |
| 같은 Stage 내 다른 RS 분기 이동 | `📌 {RS}로 돌아왔어요!` |

- **Stage별 토스트 메모리** — `lastToastByStageRef`에 stage별 마지막 persistent 토스트를 저장, 재진입 시 토글 버튼으로 복원 가능
- **RS 추적 기준** — `selectedStep`의 소속 RS를 `findRequiredStep`으로 직접 찾아 비교(`prevRSName` vs 새 RS)


## 8. 디버깅

### 백엔드 헬스 체크
```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
```

### ESLint / 빌드 확인
```bash
npm run lint
npm run build
```

### VS Code 디버거 (launch.json)
```json
{
  "name": "Frontend Dev Server",
  "type": "node",
  "request": "launch",
  "runtimeExecutable": "npm",
  "runtimeArgs": ["run", "dev"],
  "cwd": "${workspaceFolder}/frontend",
  "console": "integratedTerminal"
}
```
