from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.core.models.required_step import RequiredStep
from app.core.models.stage import Stage

# DOJ SDLC 기반 Required Step 시드 데이터 (24개 = 4 per stage × 6 stages)
# stage_sequence: Stage.sequence 기준
REQUIRED_STEP_DATA: list[dict] = [
    # ── Stage 1: 아이디어 구체화 (Ch3 + Ch4) ──────────────────────────────
    {
        "stage_sequence": 1,
        "sequence": 1,
        "name": "문제/기회 정의",
        "toast_message": "문제/기회 정의서를 완성했습니다! 🎯",
        "template_description": "해결하고자 하는 핵심 문제 또는 기회를 명확히 기술하는 문서입니다. 문제 배경, 현재 상황, 기대 효과를 포함합니다.",
        "goal": "프로젝트가 해결하려는 핵심 문제 또는 기회를 명확히 정의한다.",
        "entry_criteria": "프로젝트 초기 아이디어가 존재하며 사용자가 해결하고 싶은 문제를 인지하고 있다.",
        "fulfillment_criteria": [
            "문제 배경 기술",
            "현재 상황 분석",
            "기대 효과 명시",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch3 - Initiation",
    },
    {
        "stage_sequence": 1,
        "sequence": 2,
        "name": "목표 사용자 분석",
        "toast_message": "목표 사용자 분석을 완료했습니다! 👥",
        "template_description": "타겟 사용자 그룹과 페르소나를 정의하는 문서입니다. 사용자 특성, 니즈, 페인 포인트를 포함합니다.",
        "goal": "프로젝트가 대상으로 하는 사용자 그룹과 페르소나를 구체화한다.",
        "entry_criteria": "문제/기회가 정의되어 있고 잠재 사용자에 대한 가설이 존재한다.",
        "fulfillment_criteria": [
            "타겟 사용자 그룹 정의",
            "페르소나 작성",
            "사용자 니즈/페인 포인트 도출",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch3 - Stakeholder Analysis",
    },
    {
        "stage_sequence": 1,
        "sequence": 3,
        "name": "유사 서비스 분석",
        "toast_message": "유사 서비스 분석을 완료했습니다! 🔍",
        "template_description": "경쟁사 및 유사 서비스를 벤치마킹하는 문서입니다. 강점·약점 비교표와 차별화 포인트를 포함합니다.",
        "goal": "경쟁사 및 유사 서비스를 분석하여 차별화 포인트를 도출한다.",
        "entry_criteria": "타겟 사용자가 정의되어 있고 비교할 만한 유사 서비스가 식별되어 있다.",
        "fulfillment_criteria": [
            "경쟁사 식별",
            "강점·약점 비교",
            "차별화 포인트 도출",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch4 - Market Analysis",
    },
    {
        "stage_sequence": 1,
        "sequence": 4,
        "name": "핵심 개념 정의",
        "toast_message": "핵심 개념 정의를 완료했습니다! 💡",
        "template_description": "프로젝트의 핵심 가치 제안과 차별점을 정의하는 문서입니다. 솔루션 개요, 핵심 기능 아이디어, 기대 가치를 포함합니다.",
        "goal": "프로젝트의 핵심 가치 제안과 솔루션 개념을 구체화한다.",
        "entry_criteria": "유사 서비스 분석이 완료되어 차별화 방향이 정해져 있다.",
        "fulfillment_criteria": [
            "솔루션 개요 작성",
            "핵심 기능 아이디어 도출",
            "기대 가치 명시",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch4 - System Concept Development",
    },
    # ── Stage 2: 프로젝트 계획 (Ch5) ──────────────────────────────────────
    {
        "stage_sequence": 2,
        "sequence": 1,
        "name": "프로젝트 범위 정의",
        "toast_message": "프로젝트 범위 정의서를 완성했습니다! 📋",
        "template_description": "In/Out Scope와 WBS를 정의하는 문서입니다. 주요 기능 목록, 제외 항목, 산출물 목록을 포함합니다.",
        "goal": "프로젝트의 In/Out Scope와 작업 분할 구조(WBS)를 명확히 한다.",
        "entry_criteria": "핵심 개념이 정의되어 있고 주요 기능 후보가 도출되어 있다.",
        "fulfillment_criteria": [
            "In Scope 기능 명시",
            "Out of Scope 명시",
            "WBS 작성",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch5 - Project Planning",
    },
    {
        "stage_sequence": 2,
        "sequence": 2,
        "name": "일정 계획 수립",
        "toast_message": "일정 계획을 완성했습니다! 📅",
        "template_description": "마일스톤과 세부 일정을 계획하는 문서입니다. Gantt 차트, 스프린트 계획, 주요 마일스톤 일정을 포함합니다.",
        "goal": "프로젝트 마일스톤과 세부 일정을 계획한다.",
        "entry_criteria": "프로젝트 범위가 정의되어 있고 주요 산출물이 식별되어 있다.",
        "fulfillment_criteria": [
            "마일스톤 정의",
            "세부 일정 작성",
            "스프린트 계획 수립",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch5 - Schedule Planning",
    },
    {
        "stage_sequence": 2,
        "sequence": 3,
        "name": "리소스 계획 수립",
        "toast_message": "리소스 계획을 완성했습니다! 👨‍💻",
        "template_description": "팀 구성과 역할 분담을 계획하는 문서입니다. 팀원별 담당 역할, 필요 기술 스택, 협업 도구 계획을 포함합니다.",
        "goal": "팀 구성과 역할 분담, 필요 기술 스택을 계획한다.",
        "entry_criteria": "일정이 수립되어 있고 작업 단위가 식별되어 있다.",
        "fulfillment_criteria": [
            "팀원 역할 정의",
            "필요 기술 스택 결정",
            "협업 도구 선정",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch5 - Resource Planning",
    },
    {
        "stage_sequence": 2,
        "sequence": 4,
        "name": "리스크 분석",
        "toast_message": "리스크 분석을 완료했습니다! ⚠️",
        "template_description": "프로젝트 리스크를 식별하고 대응 계획을 수립하는 문서입니다. 리스크 목록, 발생 가능성·영향도 매트릭스, 완화 전략을 포함합니다.",
        "goal": "프로젝트 리스크를 식별하고 대응 전략을 수립한다.",
        "entry_criteria": "일정·리소스 계획이 수립되어 있고 잠재 리스크가 식별 가능한 상태다.",
        "fulfillment_criteria": [
            "리스크 목록 도출",
            "발생 가능성·영향도 평가",
            "완화 전략 수립",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch5 - Risk Management",
    },
    # ── Stage 3: 요구사항 정의 (Ch6) ──────────────────────────────────────
    {
        "stage_sequence": 3,
        "sequence": 1,
        "name": "기능 요구사항 정의",
        "toast_message": "기능 요구사항 정의서를 완성했습니다! ✅",
        "template_description": "시스템이 수행해야 할 기능을 명세하는 문서입니다. 기능 목록, 우선순위, 입출력 조건을 포함합니다.",
        "goal": "시스템이 수행해야 할 기능을 상세히 명세한다.",
        "entry_criteria": "프로젝트 범위가 정의되어 있고 주요 기능 후보가 도출되어 있다.",
        "fulfillment_criteria": [
            "기능 목록 작성",
            "우선순위 부여",
            "입출력 조건 명시",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch6 - Functional Requirements",
    },
    {
        "stage_sequence": 3,
        "sequence": 2,
        "name": "비기능 요구사항 정의",
        "toast_message": "비기능 요구사항 정의서를 완성했습니다! 🔧",
        "template_description": "성능·보안·가용성 등 품질 요구사항을 정의하는 문서입니다. 응답시간 목표, 보안 정책, 확장성 요건을 포함합니다.",
        "goal": "성능·보안·가용성 등 시스템 품질 요구사항을 정의한다.",
        "entry_criteria": "기능 요구사항이 정리되어 있고 시스템 운영 환경 가정이 있다.",
        "fulfillment_criteria": [
            "성능 목표 명시",
            "보안 정책 정의",
            "가용성·확장성 요건 명시",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch6 - Non-Functional Requirements",
    },
    {
        "stage_sequence": 3,
        "sequence": 3,
        "name": "사용자 스토리 작성",
        "toast_message": "사용자 스토리를 완성했습니다! 📖",
        "template_description": "사용자 관점의 기능 시나리오를 정의하는 문서입니다. As-a / I-want / So-that 형식의 스토리 목록과 인수 기준을 포함합니다.",
        "goal": "사용자 관점에서 기능 시나리오와 인수 기준을 명확히 한다.",
        "entry_criteria": "기능 요구사항이 정의되어 있고 페르소나가 식별되어 있다.",
        "fulfillment_criteria": [
            "As-a / I-want / So-that 스토리 작성",
            "인수 기준(Acceptance Criteria) 명시",
            "우선순위 부여",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch6 - User Stories",
    },
    {
        "stage_sequence": 3,
        "sequence": 4,
        "name": "요구사항 확정",
        "toast_message": "요구사항 확정을 완료했습니다! 📌",
        "template_description": "이해관계자 검토 후 요구사항 기준선을 확정하는 문서입니다. 검토 의견 반영 내역, 최종 기능 목록, 승인 내역을 포함합니다.",
        "goal": "이해관계자 검토를 거쳐 요구사항 기준선을 확정한다.",
        "entry_criteria": "기능·비기능·사용자 스토리가 모두 정리되어 있다.",
        "fulfillment_criteria": [
            "이해관계자 검토 의견 반영",
            "최종 기능 목록 확정",
            "기준선 승인",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch6 - Requirements Baseline",
    },
    # ── Stage 4: 설계 (Ch7) ───────────────────────────────────────────────
    {
        "stage_sequence": 4,
        "sequence": 1,
        "name": "시스템 아키텍처 설계",
        "toast_message": "시스템 아키텍처 설계를 완료했습니다! 🏗️",
        "template_description": "전체 시스템 구조와 컴포넌트를 설계하는 문서입니다. 아키텍처 다이어그램, 기술 스택 선택 근거, 배포 구성을 포함합니다.",
        "goal": "시스템의 전체 구조와 컴포넌트, 기술 스택을 결정한다.",
        "entry_criteria": "요구사항 기준선이 확정되어 있다.",
        "fulfillment_criteria": [
            "아키텍처 다이어그램 작성",
            "기술 스택 선택 근거 명시",
            "배포 구성 정의",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch7 - System Architecture",
    },
    {
        "stage_sequence": 4,
        "sequence": 2,
        "name": "데이터베이스 설계",
        "toast_message": "데이터베이스 설계를 완료했습니다! 🗄️",
        "template_description": "ERD와 데이터 모델을 설계하는 문서입니다. 엔티티 정의, 관계도, 인덱스 전략을 포함합니다.",
        "goal": "ERD와 데이터 모델, 인덱스 전략을 설계한다.",
        "entry_criteria": "시스템 아키텍처가 결정되어 있고 핵심 도메인이 식별되어 있다.",
        "fulfillment_criteria": [
            "엔티티 정의",
            "관계 다이어그램(ERD) 작성",
            "인덱스 전략 명시",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch7 - Data Design",
    },
    {
        "stage_sequence": 4,
        "sequence": 3,
        "name": "API 설계",
        "toast_message": "API 설계를 완료했습니다! 🔌",
        "template_description": "RESTful API 명세와 인터페이스를 정의하는 문서입니다. 엔드포인트 목록, 요청/응답 스키마, 인증 방식을 포함합니다.",
        "goal": "외부 인터페이스인 RESTful API 명세를 정의한다.",
        "entry_criteria": "데이터 모델과 시스템 아키텍처가 결정되어 있다.",
        "fulfillment_criteria": [
            "엔드포인트 목록 작성",
            "요청/응답 스키마 정의",
            "인증 방식 결정",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch7 - Interface Design",
    },
    {
        "stage_sequence": 4,
        "sequence": 4,
        "name": "UI/UX 설계",
        "toast_message": "UI/UX 설계를 완료했습니다! 🎨",
        "template_description": "화면 설계와 사용자 인터페이스 프로토타입을 작성하는 문서입니다. 화면 흐름도, 와이어프레임, 인터랙션 가이드를 포함합니다.",
        "goal": "화면 흐름과 인터페이스 프로토타입을 설계한다.",
        "entry_criteria": "사용자 스토리와 API 설계가 완료되어 있다.",
        "fulfillment_criteria": [
            "화면 흐름도 작성",
            "와이어프레임 작성",
            "인터랙션 가이드 명시",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch7 - UI/UX Design",
    },
    # ── Stage 5: 개발 (Ch8) ───────────────────────────────────────────────
    {
        "stage_sequence": 5,
        "sequence": 1,
        "name": "개발 환경 구성",
        "toast_message": "개발 환경 구성을 완료했습니다! ⚙️",
        "template_description": "개발 환경 셋업과 CI/CD 파이프라인을 구성하는 문서입니다. 로컬 환경 설정, 브랜치 전략, 자동화 파이프라인 구성을 포함합니다.",
        "goal": "개발에 필요한 로컬 환경과 CI/CD 파이프라인을 구축한다.",
        "entry_criteria": "기술 스택과 배포 구성이 결정되어 있다.",
        "fulfillment_criteria": [
            "로컬 환경 셋업",
            "브랜치 전략 정의",
            "CI/CD 파이프라인 구성",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch8 - Development Environment",
    },
    {
        "stage_sequence": 5,
        "sequence": 2,
        "name": "핵심 기능 개발",
        "toast_message": "핵심 기능 개발을 완료했습니다! 🚀",
        "template_description": "주요 비즈니스 로직 구현 내역을 기록하는 문서입니다. 구현된 기능 목록, 주요 기술 결정 사항, 알려진 제약 사항을 포함합니다.",
        "goal": "주요 비즈니스 로직과 핵심 기능을 구현한다.",
        "entry_criteria": "개발 환경이 구축되어 있고 설계 문서가 존재한다.",
        "fulfillment_criteria": [
            "핵심 기능 구현 완료",
            "주요 기술 결정 기록",
            "알려진 제약 사항 명시",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch8 - Core Implementation",
    },
    {
        "stage_sequence": 5,
        "sequence": 3,
        "name": "API 구현 및 통합",
        "toast_message": "API 구현 및 통합을 완료했습니다! 🔗",
        "template_description": "Backend API와 Frontend 연동 구현 내역을 기록하는 문서입니다. API 구현 현황, 통합 테스트 결과, 미구현 항목을 포함합니다.",
        "goal": "Backend API와 Frontend 연동을 구현하고 통합한다.",
        "entry_criteria": "API 설계가 완료되어 있고 핵심 기능이 일부 구현되어 있다.",
        "fulfillment_criteria": [
            "API 구현 완료",
            "Frontend 연동 완료",
            "통합 테스트 결과 기록",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch8 - Integration",
    },
    {
        "stage_sequence": 5,
        "sequence": 4,
        "name": "코드 리뷰 및 리팩토링",
        "toast_message": "코드 리뷰 및 리팩토링을 완료했습니다! ✨",
        "template_description": "코드 품질 검토와 개선 내역을 기록하는 문서입니다. 리뷰 체크리스트, 발견된 이슈 및 개선 사항, 기술 부채 목록을 포함합니다.",
        "goal": "코드 품질을 검토하고 개선한다.",
        "entry_criteria": "핵심 기능과 통합이 완료되어 있다.",
        "fulfillment_criteria": [
            "리뷰 체크리스트 작성",
            "발견된 이슈 개선",
            "기술 부채 목록 정리",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch8 - Code Review",
    },
    # ── Stage 6: 테스트 및 검증 (Ch9) ────────────────────────────────────
    {
        "stage_sequence": 6,
        "sequence": 1,
        "name": "단위 테스트 작성",
        "toast_message": "단위 테스트 작성을 완료했습니다! 🧪",
        "template_description": "각 컴포넌트별 단위 테스트 구현 내역을 기록하는 문서입니다. 테스트 커버리지 목표, 주요 테스트 케이스, 커버리지 측정 결과를 포함합니다.",
        "goal": "각 컴포넌트별 단위 테스트를 작성하고 커버리지를 확보한다.",
        "entry_criteria": "핵심 기능이 구현되어 있다.",
        "fulfillment_criteria": [
            "커버리지 목표 명시",
            "주요 테스트 케이스 작성",
            "커버리지 측정 결과 기록",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch9 - Unit Testing",
    },
    {
        "stage_sequence": 6,
        "sequence": 2,
        "name": "통합 테스트 수행",
        "toast_message": "통합 테스트를 완료했습니다! 🔄",
        "template_description": "시스템 통합 테스트와 결함 수정 내역을 기록하는 문서입니다. 통합 테스트 시나리오, 발견된 결함 목록 및 수정 내역을 포함합니다.",
        "goal": "시스템 전반의 통합 테스트를 수행하고 결함을 수정한다.",
        "entry_criteria": "단위 테스트가 통과하고 주요 컴포넌트가 통합되어 있다.",
        "fulfillment_criteria": [
            "통합 테스트 시나리오 작성",
            "결함 목록 정리",
            "수정 내역 기록",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch9 - Integration Testing",
    },
    {
        "stage_sequence": 6,
        "sequence": 3,
        "name": "사용자 인수 테스트",
        "toast_message": "사용자 인수 테스트를 완료했습니다! 👤",
        "template_description": "실제 사용자 관점에서 시스템을 검증하는 문서입니다. UAT 시나리오, 사용자 피드백, 최종 수정 내역을 포함합니다.",
        "goal": "실제 사용자 관점에서 UAT를 수행하고 피드백을 반영한다.",
        "entry_criteria": "통합 테스트가 통과하고 시스템이 안정 동작한다.",
        "fulfillment_criteria": [
            "UAT 시나리오 작성",
            "사용자 피드백 수집",
            "최종 수정 내역 기록",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch9 - User Acceptance Testing",
    },
    {
        "stage_sequence": 6,
        "sequence": 4,
        "name": "배포 및 운영 준비",
        "toast_message": "배포 및 운영 준비를 완료했습니다! 🎉",
        "template_description": "운영 환경 배포와 모니터링 체계를 구축하는 문서입니다. 배포 절차서, 운영 모니터링 구성, 장애 대응 매뉴얼을 포함합니다.",
        "goal": "운영 환경에 배포하고 모니터링·장애 대응 체계를 구축한다.",
        "entry_criteria": "UAT가 완료되어 있고 배포 가능한 상태다.",
        "fulfillment_criteria": [
            "배포 절차서 작성",
            "운영 모니터링 구성",
            "장애 대응 매뉴얼 작성",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch9 - Deployment & Operations",
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
    db.commit()
