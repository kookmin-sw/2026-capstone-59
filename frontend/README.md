# Poco Frontend

Vite + React 기반의 SPA 프론트엔드.
React Flow(@xyflow/react)로 Step 트리를 시각화하고, Framer Motion으로 전환 애니메이션을 처리한다.

---

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
/api → http://localhost:8000
/ai → http://localhost:8001
로 프록시 설정이 돼 있어서 백엔드(Business API)와 AI Orchestrator를 별도 CORS 설정 없이 연동할 수 있다.


## 2. 디렉토리 구조

```
frontend/
├── index.html
├── vite.config.js                 #  Vite 설정 (dev proxy 포함)
├── package.json
│
└── src/
    ├── main.jsx                   #  React 진입점 (ReactDOM.createRoot)
    ├── App.jsx                    #  라우터 설정 (react-router-dom)
    │
    ├── api/                       #  Axios 기반 API 호출 모듈
    │   ├── auth.js                #  로그인 / OAuth 관련
    │   ├── projects.js            #  Project CRUD
    │   ├── stage.js               #  Stage 조회·이동
    │   ├── step.js                #  Step 생성·Accept·조회
    │   └── shared.js              #  공유 캔버스 조회
    │
    ├── pages/                     #  라우트별 페이지 컴포넌트
    │   ├── LandingPage.jsx        #  서비스 소개 (/)
    │   ├── LoginPage.jsx          #  OAuth 로그인 (/login)
    │   ├── AuthCallbackPage.jsx   #  OAuth 콜백 처리 (/auth/callback)
    │   ├── CreateProjectPage.jsx  #  프로젝트 생성 (/projects/new)
    │   ├── ProjectListPage.jsx    #  프로젝트 목록 (/projects)
    │   ├── CanvasPage.jsx         #  메인 캔버스 (/projects/:id)
    │   └── SharedCanvasPage.jsx   #  공유 캔버스 (읽기 전용)
    │
    ├── components/
    │   ├── PrivateRoute.jsx       # 인증 가드 (미로그인 시 /login 리다이렉트)
    │   │
    │   └── canvas/                # 캔버스 페이지 전용 컴포넌트
    │       ├── StepNode.jsx           #  일반 Step 노드 (사각형)
    │       ├── RequiredStepNode.jsx   #  필수 Step 노드 (다이아몬드)
    │       ├── SidePanel.jsx          #  Step 클릭 시 열리는 우측 패널
    │       ├── StageNavigator.jsx     #  좌측 Stage 목록 패널
    │       ├── ToastAlarm.jsx         #  필수 Step 진입 시 상단 토스트
    │       └── onNodeContext.jsx      #  노드 우클릭 컨텍스트 메뉴
    │
    ├── utils/
    │   └── canvasUtils.js       # React Flow 노드·엣지 레이아웃 유틸
    │
    └── styles/
        └── global.css           # 전역 CSS (reset, 폰트, CSS 변수)
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

# 환경 변수 파일
루트에 .env 파일 생성(.env.example 참고):

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_AI_BASE_URL=http://localhost:8001
```

개발 서버에서는 vite.config.js의 proxy 설정으로 /api, /ai 경로가 자동 전달되기 때문에
환경 변수 없이도 로컬 개발이 가능.

## 4. 주요 라이브러리
라이브러리	      버전	용도
react	            19	  UI 렌더링
react-router-dom	7	    SPA 라우팅
@xyflow/react	    12	  Step 트리 캔버스
framer-motion   	12 	 전환 애니메이션
axios	            1	    HTTP API 호출
react-markdown	  10 	 마크다운 렌더링
react-icons	      5	   아이콘

## 5. 주요 페이지·컴포넌트 상세

### CanvasPage
메인 작업 화면. 핵심 상태와 로직이 집중돼 있다.

### 주요 상태

| 상태                | 역할                       |
| ------------------- | ------------------------- |
| nodes / edges       | React Flow 노드·엣지 배열  |
| selectedNode        | 현재 클릭된 노드           |
| streamBuffers (ref) | 노드 ID별 스트리밍 버퍼 Map |
| isStreamMode        | 스트리밍 진행 여부          |


### Step 선택 흐름:
1. 노드 클릭 → handleNodeClick
2. streamBuffers 확인
  - isDone이면 → DB에서 상세 로드
  - 스트리밍 중이면 → 기존 스트림에 콜백 연결
  - 없으면 → DB 로드

### SidePanel
Step 클릭 시 우측 패널.

탭 구성
Step 종류	  탭 구성
일반 Step	  AI Mentoring / Dictionary
필수 Step	  AI Mentoring / Dictionary / Template


### MentoringContent 렌더링 우선순위:

1. isLoading && !streamingText
  - isStreamMode → AllSkeleton
  - 아니면 → LoadingSpinner
2. streamingText 있음
  → StreamingStructuredView (TypewriterText)
3. 로드 완료
  → 구조화된 정적 뷰

## 6. 디버깅

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