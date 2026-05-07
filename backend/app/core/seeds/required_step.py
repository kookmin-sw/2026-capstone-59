from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.core.models.required_step import RequiredStep
from app.core.models.stage import Stage

# DOJ SDLC 기반 Required Step 시드 데이터 (24개 = 4 per stage × 6 stages)
# - 4개 측면 R: 21개 / 5개 측면 R: 3개 (4-R1, 4-R4, 6-R1)
# - 모든 R 공통 충족 기준: minimum_fulfillment_count = 2
REQUIRED_STEP_DATA: list[dict] = [
    # ── Stage 1: 아이디어 구체화 ──────────────────────────────────────────
    {
        "stage_sequence": 1,
        "sequence": 1,
        "name": "문제/기회 정의",
        "toast_message": "문제/기회 정의를 완료했습니다! 🎯",
        "template_description": "프로젝트가 해결하려는 문제 또는 포착한 기회를 명확하게 정의하는 문서입니다. 문제의 배경, 중요도, 기존 대안의 한계 등을 정리합니다.",
        "goal": "프로젝트가 해결하려는 문제 또는 포착한 기회를 명확하게 정의한다.",
        "entry_criteria": "Stage 1의 출발점이므로 별도 선행 맥락 없이 초기 프롬프트만으로 진입 가능하다.",
        "fulfillment_criteria": [
            "문제/기회 자체에 대한 서술·명확화",
            "문제의 중요도·임팩트 (왜 해결할 가치가 있는가)",
            "문제의 발생 배경·상황·맥락",
            "기존 대안의 한계 또는 미해결 지점",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch3 - Initiation",
    },
    {
        "stage_sequence": 1,
        "sequence": 2,
        "name": "대상 사용자 파악",
        "toast_message": "대상 사용자 파악을 완료했습니다! 👥",
        "template_description": "정의된 문제로 불편을 겪는 구체적 사용자군을 식별하고 특성을 정리하는 문서입니다. 페르소나, 사용 맥락, 검증 활동 등을 포함합니다.",
        "goal": "정의된 문제로 불편을 겪는 구체적 사용자군을 식별하고 특성을 그린다.",
        "entry_criteria": "Step 히스토리에 문제/기회에 관한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "1차 타겟 사용자군의 특성 정의 (연령·상황·역할 등)",
            "사용자의 현재 행동·습관·맥락 파악",
            "사용자 페르소나 또는 시나리오 정리",
            "사용자 검증 활동 (인터뷰·관찰·설문 등)",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch3 - Stakeholder Analysis",
    },
    {
        "stage_sequence": 1,
        "sequence": 3,
        "name": "핵심 컨셉 정의",
        "toast_message": "핵심 컨셉 정의를 완료했습니다! 💡",
        "template_description": "문제를 어떤 해결책으로 풀지, 그 차별점이 무엇인지 한 단락 수준으로 정리하는 문서입니다. 유사 서비스 비교와 핵심 가치 제안을 포함합니다.",
        "goal": "정의된 문제를 어떤 해결책으로 풀지, 그 차별점이 무엇인지 한 단락 수준으로 정리한다.",
        "entry_criteria": "Step 히스토리에 문제 정의와 사용자 이해에 관한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "해결 접근 방식·아이디어 서술",
            "유사/경쟁 서비스 조사 및 비교",
            "차별점 또는 핵심 가치 제안(Value Proposition)",
            "주요 기능의 큰 그림·윤곽",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch4 - System Concept Development",
    },
    {
        "stage_sequence": 1,
        "sequence": 4,
        "name": "실현 가능성 검토",
        "toast_message": "실현 가능성 검토를 완료했습니다! 🔬",
        "template_description": "주어진 기간·인원·기술 수준으로 컨셉을 실제로 만들 수 있는지 판단하는 문서입니다. 기술/자원 적합성, 검증 활동, 리스크를 포함합니다.",
        "goal": "주어진 기간·인원·기술 수준으로 컨셉을 실제로 만들 수 있는지, 주요 리스크는 무엇인지 판단한다.",
        "entry_criteria": "Step 히스토리에 핵심 컨셉에 대한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "기술적 실현 가능성 검토",
            "기간·자원·인원·비용 관점의 적합성 검토",
            "프로토타입·PoC 등 소규모 검증 활동",
            "주요 리스크·제약사항 식별",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch4 - Feasibility Study",
    },
    # ── Stage 2: 프로젝트 계획 ────────────────────────────────────────────
    {
        "stage_sequence": 2,
        "sequence": 1,
        "name": "일정 계획 수립",
        "toast_message": "일정 계획 수립을 완료했습니다! 📅",
        "template_description": "프로젝트 전체 기간을 Stage/마일스톤 단위로 배분하는 일정 뼈대를 정의하는 문서입니다. 마일스톤, 공수 추정, 일정 도구를 포함합니다.",
        "goal": "프로젝트 전체 기간을 Stage/마일스톤 단위로 배분하는 일정 뼈대를 만든다.",
        "entry_criteria": "Step 히스토리에 \"무엇을 얼마나 만들 것인지\"에 대한 컨셉·실현 가능성 맥락이 존재한다.",
        "fulfillment_criteria": [
            "전체 일정을 Stage/구간으로 분할",
            "주요 마일스톤 또는 데드라인 설정",
            "Step/작업 단위의 공수·난이도 추정",
            "일정 관리 방식·도구 선정",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch5 - Schedule Planning",
    },
    {
        "stage_sequence": 2,
        "sequence": 2,
        "name": "역할 분담",
        "toast_message": "역할 분담을 완료했습니다! 👨‍👩‍👧",
        "template_description": "팀원 각자의 담당 영역과 책임 범위를 명시하는 문서입니다. 1인 프로젝트인 경우 본인의 역할들을 명시적으로 구분합니다.",
        "goal": "팀원 각자의 담당 영역을 정하고, 1인 프로젝트인 경우 본인이 맡을 역할들을 명시적으로 구분한다.",
        "entry_criteria": "Step 히스토리에 프로젝트의 범위·일정에 대한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "팀원별 주 담당 영역 또는 역할 정의",
            "역할 간 경계와 책임 범위 명시",
            "의사결정·리뷰 주체 결정",
            "협업·커뮤니케이션 규칙 수립",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch5 - Resource Planning",
    },
    {
        "stage_sequence": 2,
        "sequence": 3,
        "name": "위험 식별",
        "toast_message": "위험 식별을 완료했습니다! ⚠️",
        "template_description": "프로젝트 진행을 방해할 수 있는 주요 리스크를 미리 식별하고 대응 방향을 정하는 문서입니다.",
        "goal": "프로젝트 진행을 방해할 수 있는 주요 리스크를 미리 식별하고 대응 방향을 정한다.",
        "entry_criteria": "Step 히스토리에 일정·역할·기술 선택 등 \"깨질 수 있는 계획\"이 존재한다.",
        "fulfillment_criteria": [
            "기술 리스크 식별 (난이도·학습 곡선 등)",
            "일정 리스크 식별 (딜레이 요인·병목)",
            "팀 리스크 식별 (이탈·역량·커뮤니케이션)",
            "각 리스크별 대응·완화 방안",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch5 - Risk Management",
    },
    {
        "stage_sequence": 2,
        "sequence": 4,
        "name": "개발 환경/도구 결정",
        "toast_message": "개발 환경/도구 결정을 완료했습니다! 🛠️",
        "template_description": "프로젝트에서 공통으로 사용할 기술 스택과 협업 도구를 확정하는 문서입니다.",
        "goal": "프로젝트에서 공통으로 사용할 기술 스택과 협업 도구를 확정한다.",
        "entry_criteria": "Step 히스토리에 컨셉·실현 가능성 맥락이 존재하여 어떤 기술 영역이 필요할지 판단 가능하다.",
        "fulfillment_criteria": [
            "개발 언어·프레임워크 선정",
            "형상관리·브랜치 전략 (Git 등)",
            "협업·이슈 관리 도구 선정",
            "개발·배포 환경 구성 방향",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch5 - Tool Selection",
    },
    # ── Stage 3: 요구사항 정의 ────────────────────────────────────────────
    {
        "stage_sequence": 3,
        "sequence": 1,
        "name": "요구사항 도출",
        "toast_message": "요구사항 도출을 완료했습니다! 📥",
        "template_description": "시스템이 수행해야 할 일들을 사용자와 팀의 관점에서 자유롭게 모으는 문서입니다. 인터뷰·브레인스토밍 등 도출 활동 결과를 포함합니다.",
        "goal": "시스템이 수행해야 할 일들을 사용자와 팀의 관점에서 자유롭게 모은다.",
        "entry_criteria": "Step 히스토리에 대상 사용자와 핵심 컨셉에 대한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "사용자 관점의 필요(user needs) 수집",
            "도출 기법 적용 (인터뷰·브레인스토밍·유스케이스 등)",
            "유사 서비스·경쟁 분석을 통한 요구사항 추출",
            "초기 요구사항 후보 목록 정리",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch6 - Requirements Elicitation",
    },
    {
        "stage_sequence": 3,
        "sequence": 2,
        "name": "기능 요구사항 정의",
        "toast_message": "기능 요구사항 정의를 완료했습니다! ✅",
        "template_description": "시스템이 제공해야 할 기능들을 구체적이고 검증 가능한 형태로 정의하는 문서입니다.",
        "goal": "시스템이 제공해야 할 기능들을 구체적이고 검증 가능한 형태로 정의한다.",
        "entry_criteria": "Step 히스토리에 요구사항 도출 활동과 그 결과 맥락이 존재한다.",
        "fulfillment_criteria": [
            "핵심 기능의 명세화",
            "기능을 유스케이스·유저스토리 등으로 기술",
            "기능 간 관계·의존성 정리",
            "입력·출력·동작 조건 명시",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch6 - Functional Requirements",
    },
    {
        "stage_sequence": 3,
        "sequence": 3,
        "name": "비기능 요구사항 정의",
        "toast_message": "비기능 요구사항 정의를 완료했습니다! 🔧",
        "template_description": "성능·보안·사용성 등 기능 외적으로 시스템이 갖춰야 할 품질 속성을 정의하는 문서입니다.",
        "goal": "성능·보안·사용성 등 기능 외적으로 시스템이 갖춰야 할 품질 속성을 정의한다.",
        "entry_criteria": "Step 히스토리에 기능 요구사항에 대한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "성능·응답 시간·처리량 관련 요구사항",
            "보안·인증·데이터 보호 요구사항",
            "사용성·접근성 요구사항",
            "호환성·확장성·유지보수성 요구사항",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch6 - Non-Functional Requirements",
    },
    {
        "stage_sequence": 3,
        "sequence": 4,
        "name": "요구사항 검토",
        "toast_message": "요구사항 검토를 완료했습니다! 📌",
        "template_description": "도출된 요구사항의 일관성·실현 가능성·우선순위를 팀이 함께 점검하고 확정하는 문서입니다.",
        "goal": "도출된 요구사항의 일관성·실현 가능성·우선순위를 팀이 함께 점검하고 확정한다.",
        "entry_criteria": "Step 히스토리에 기능·비기능 요구사항이 모두 논의된 맥락이 존재한다.",
        "fulfillment_criteria": [
            "요구사항 간 중복·충돌 정리",
            "우선순위 부여 (Must/Should/Could 또는 MVP 포함 여부)",
            "요구사항 실현 가능성 재점검",
            "요구사항 추적 체계 수립 (매트릭스 등)",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch6 - Requirements Review",
    },
    # ── Stage 4: 설계 ────────────────────────────────────────────────────
    {
        "stage_sequence": 4,
        "sequence": 1,
        "name": "시스템 아키텍처 정의",
        "toast_message": "시스템 아키텍처 정의를 완료했습니다! 🏗️",
        "template_description": "시스템을 구성할 주요 컴포넌트와 상호 관계를 큰 그림 수준으로 그리는 문서입니다. 컴포넌트 식별, 통신 관계, 아키텍처 패턴, 요구사항 매핑, 배포 구조를 포함합니다.",
        "goal": "시스템을 구성할 주요 컴포넌트와 상호 관계를 큰 그림 수준으로 그린다.",
        "entry_criteria": "Step 히스토리에 확정된 요구사항에 대한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "주요 구성요소 식별 (프론트·백·DB·외부 서비스 등)",
            "구성요소 간 통신·의존 관계",
            "아키텍처 패턴·스타일 선택 (모놀리식/3-tier 등)",
            "요구사항의 구성요소 배분·매핑 (requirement allocation)",
            "배포·인프라 구조의 큰 그림",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch7 - System Architecture",
    },
    {
        "stage_sequence": 4,
        "sequence": 2,
        "name": "데이터 모델 설계",
        "toast_message": "데이터 모델 설계를 완료했습니다! 🗄️",
        "template_description": "시스템이 다룰 핵심 데이터 엔티티와 관계를 정의하는 문서입니다. ERD, 속성, 제약조건을 포함합니다.",
        "goal": "시스템이 다룰 핵심 데이터 엔티티와 관계를 정의한다.",
        "entry_criteria": "Step 히스토리에 기능 요구사항과 아키텍처 맥락이 존재한다.",
        "fulfillment_criteria": [
            "핵심 엔티티·속성 식별",
            "엔티티 간 관계(1:N, N:M 등) 정의",
            "데이터 타입·제약조건 정리",
            "저장소 선택 및 스키마 구조화 (ERD 등)",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch7 - Data Design",
    },
    {
        "stage_sequence": 4,
        "sequence": 3,
        "name": "인터페이스 설계",
        "toast_message": "인터페이스 설계를 완료했습니다! 🔌",
        "template_description": "외부(UI·외부 API)와 내부(컴포넌트 간) 주요 인터페이스의 모습을 정의하는 문서입니다.",
        "goal": "외부(UI·외부 API)와 내부(컴포넌트 간) 주요 인터페이스의 모습을 정의한다.",
        "entry_criteria": "Step 히스토리에 아키텍처·데이터 모델 맥락이 존재한다.",
        "fulfillment_criteria": [
            "사용자 UI 구성 (와이어프레임·화면 구조 등)",
            "API 엔드포인트·입출력 스펙",
            "컴포넌트 간 내부 인터페이스",
            "외부 서비스 연동 인터페이스",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch7 - Interface Design",
    },
    {
        "stage_sequence": 4,
        "sequence": 4,
        "name": "설계 리뷰",
        "toast_message": "설계 리뷰를 완료했습니다! 🔍",
        "template_description": "설계물이 요구사항을 충족하는지, 팀이 같은 그림을 공유하는지 점검하는 문서입니다. 매핑 점검, 누락 점검, 결정 사항 검토, 수정 방향을 포함합니다.",
        "goal": "설계물이 요구사항을 충족하는지, 팀이 같은 그림을 공유하는지 점검한다.",
        "entry_criteria": "Step 히스토리에 아키텍처·데이터 모델·인터페이스 설계 맥락이 모두 존재한다.",
        "fulfillment_criteria": [
            "요구사항과 설계 간의 매핑 점검",
            "설계 간 불일치·누락 점검",
            "성능·보안·확장성 관점의 설계 점검",
            "설계 결정 사항의 적절성 점검 (기술·프레임워크 선택, 프로토타입 결과 반영, 외부 컴포넌트 활용)",
            "리뷰 결과 반영·수정 방향 정리",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch7 - Design Review",
    },
    # ── Stage 5: 개발 ────────────────────────────────────────────────────
    {
        "stage_sequence": 5,
        "sequence": 1,
        "name": "개발 환경 구축",
        "toast_message": "개발 환경 구축을 완료했습니다! ⚙️",
        "template_description": "팀원이 동일한 환경에서 개발·빌드·실행할 수 있도록 기본 환경과 저장소를 구성하는 문서입니다.",
        "goal": "팀원이 동일한 환경에서 개발·빌드·실행할 수 있도록 기본 환경과 저장소를 구성한다.",
        "entry_criteria": "Step 히스토리에 기술 스택 결정과 설계 맥락이 존재한다.",
        "fulfillment_criteria": [
            "코드 저장소·브랜치 전략 구성",
            "로컬 개발 환경·의존성 세팅",
            "프로젝트 스캐폴드·초기 구조 수립",
            "빌드·실행·배포 스크립트 기초 구성",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch8 - Development Environment",
    },
    {
        "stage_sequence": 5,
        "sequence": 2,
        "name": "핵심 기능 구현",
        "toast_message": "핵심 기능 구현을 완료했습니다! 🚀",
        "template_description": "MVP 핵심 기능을 설계에 따라 구현하는 문서입니다. 기능별 구현, 공통 모듈, 비즈니스 로직, 진입점 구현을 포함합니다.",
        "goal": "MVP 핵심 기능을 설계에 따라 구현한다.",
        "entry_criteria": "Step 히스토리에 개발 환경 구축과 설계 맥락이 존재한다.",
        "fulfillment_criteria": [
            "핵심 기능별 구현 작업",
            "공통 모듈·유틸리티 구현",
            "데이터 처리·비즈니스 로직 구현",
            "UI 또는 진입점(엔드포인트) 구현",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch8 - Core Implementation",
    },
    {
        "stage_sequence": 5,
        "sequence": 3,
        "name": "코드 통합",
        "toast_message": "코드 통합을 완료했습니다! 🔗",
        "template_description": "개별 모듈을 하나의 실행 가능한 시스템으로 통합하는 문서입니다.",
        "goal": "개별 모듈을 하나의 실행 가능한 시스템으로 통합한다.",
        "entry_criteria": "Step 히스토리에 개별 기능·모듈 구현에 대한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "모듈 간 연결 작업 (프론트-백-DB 등)",
            "엔드투엔드 시나리오 연결",
            "통합 과정의 충돌·에러 해결",
            "통합 빌드·실행 검증",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch8 - Integration",
    },
    {
        "stage_sequence": 5,
        "sequence": 4,
        "name": "코드 리뷰 및 자체 검증",
        "toast_message": "코드 리뷰 및 자체 검증을 완료했습니다! ✨",
        "template_description": "작성된 코드를 팀원(또는 본인)이 읽어보며 결함·나쁜 패턴·누락을 발견하고 개선하는 문서입니다.",
        "goal": "작성된 코드를 팀원(또는 본인)이 읽어보며 결함·나쁜 패턴·누락을 발견하고 개선한다.",
        "entry_criteria": "Step 히스토리에 핵심 기능 구현과 통합에 대한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "코드 리뷰·피어 리뷰 활동",
            "코딩 컨벤션·품질 점검",
            "단위 테스트·개발자 자체 검증",
            "발견된 결함의 수정·개선",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch8 - Code Review",
    },
    # ── Stage 6: 테스트 및 검증 ──────────────────────────────────────────
    {
        "stage_sequence": 6,
        "sequence": 1,
        "name": "테스트 계획 수립",
        "toast_message": "테스트 계획 수립을 완료했습니다! 📋",
        "template_description": "Stage 3 요구사항을 어떻게 검증할지 테스트 전략과 범위를 결정하는 문서입니다. 대상·범위, 유형, 시나리오, 데이터 준비, 환경·도구를 포함합니다.",
        "goal": "Stage 3 요구사항을 어떻게 검증할지 테스트 전략과 범위를 결정한다.",
        "entry_criteria": "Step 히스토리에 통합된 시스템과 요구사항 맥락이 존재한다.",
        "fulfillment_criteria": [
            "테스트 대상·범위 정의",
            "테스트 유형 선택 (기능/통합/성능/보안 등)",
            "테스트 시나리오·케이스 설계",
            "테스트 데이터·입력값 준비 (test database 생성·샘플 데이터셋)",
            "테스트 환경·도구 준비",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch9 - Test Planning",
    },
    {
        "stage_sequence": 6,
        "sequence": 2,
        "name": "테스트 수행",
        "toast_message": "테스트 수행을 완료했습니다! 🧪",
        "template_description": "수립한 계획에 따라 테스트를 실제로 실행하여 시스템 동작을 확인하는 문서입니다.",
        "goal": "수립한 계획에 따라 테스트를 실제로 실행하여 시스템 동작을 확인한다.",
        "entry_criteria": "Step 히스토리에 테스트 계획에 대한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "기능 테스트 수행",
            "통합·시나리오 테스트 수행",
            "비기능 테스트 수행 (성능·보안·사용성 등)",
            "테스트 결과 기록·수집",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch9 - Test Execution",
    },
    {
        "stage_sequence": 6,
        "sequence": 3,
        "name": "결과 분석 및 결함 기록",
        "toast_message": "결과 분석 및 결함 기록을 완료했습니다! 📝",
        "template_description": "테스트 중 발견한 결함을 구조화된 형태로 기록하고 원인·심각도를 정리하는 문서입니다.",
        "goal": "테스트 중 발견한 결함을 구조화된 형태로 기록하고 원인·심각도를 정리한다.",
        "entry_criteria": "Step 히스토리에 테스트 수행과 결과 맥락이 존재한다.",
        "fulfillment_criteria": [
            "결함 목록화·분류",
            "결함 재현 방법·원인 분석",
            "심각도·우선순위 부여",
            "결함 수정·재테스트 계획",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch9 - Defect Analysis",
    },
    {
        "stage_sequence": 6,
        "sequence": 4,
        "name": "수용 테스트/최종 검토",
        "toast_message": "수용 테스트/최종 검토를 완료했습니다! 🎉",
        "template_description": "초기 문제/기회와 요구사항이 실제로 해결되었는지, 프로젝트 목표 달성 여부를 판단하는 문서입니다.",
        "goal": "초기 문제/기회와 요구사항이 실제로 해결되었는지, 프로젝트 목표 달성 여부를 판단한다.",
        "entry_criteria": "Step 히스토리에 결함 기록과 주요 결함 처리에 대한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "Stage 1 문제/기회 해결 여부 점검",
            "Stage 3 핵심 요구사항 충족 여부 점검",
            "사용자 관점의 수용 테스트·시연",
            "프로젝트 종료 판단·회고·향후 방향",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch9 - Acceptance & Final Review",
    },
]


def run(db: Session) -> None:
    """Required Step 시드 데이터 삽입. stage_sequence로 Stage를 조회한 뒤 upsert한다."""
    stage_map: dict[int, object] = {s.sequence: s.id for s in db.query(Stage).all()}

    rows = []
    for item in REQUIRED_STEP_DATA:
        seq = item["stage_sequence"]
        if seq not in stage_map:
            raise ValueError(
                f"Stage sequence {seq} 를 찾을 수 없습니다. Stage 시드를 먼저 실행하세요."
            )
        rows.append(
            {
                "stage_id": stage_map[seq],
                "name": item["name"],
                "sequence": item["sequence"],
                "toast_message": item["toast_message"],
                "template_description": item["template_description"],
                "goal": item["goal"],
                "entry_criteria": item["entry_criteria"],
                "fulfillment_criteria": item["fulfillment_criteria"],
                "minimum_fulfillment_count": item["minimum_fulfillment_count"],
                "doj_reference": item["doj_reference"],
            }
        )

    stmt = (
        insert(RequiredStep)
        .values(rows)
        .on_conflict_do_update(
            index_elements=["stage_id", "sequence"],
            set_={
                "name": insert(RequiredStep).excluded.name,
                "toast_message": insert(RequiredStep).excluded.toast_message,
                "template_description": insert(
                    RequiredStep
                ).excluded.template_description,
                "goal": insert(RequiredStep).excluded.goal,
                "entry_criteria": insert(RequiredStep).excluded.entry_criteria,
                "fulfillment_criteria": insert(
                    RequiredStep
                ).excluded.fulfillment_criteria,
                "minimum_fulfillment_count": insert(
                    RequiredStep
                ).excluded.minimum_fulfillment_count,
                "doj_reference": insert(RequiredStep).excluded.doj_reference,
            },
        )
    )
    db.execute(stmt)
