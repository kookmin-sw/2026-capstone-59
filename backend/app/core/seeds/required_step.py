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
    },
    {
        "stage_sequence": 1,
        "sequence": 2,
        "name": "목표 사용자 분석",
        "toast_message": "목표 사용자 분석을 완료했습니다! 👥",
        "template_description": "타겟 사용자 그룹과 페르소나를 정의하는 문서입니다. 사용자 특성, 니즈, 페인 포인트를 포함합니다.",
    },
    {
        "stage_sequence": 1,
        "sequence": 3,
        "name": "유사 서비스 분석",
        "toast_message": "유사 서비스 분석을 완료했습니다! 🔍",
        "template_description": "경쟁사 및 유사 서비스를 벤치마킹하는 문서입니다. 강점·약점 비교표와 차별화 포인트를 포함합니다.",
    },
    {
        "stage_sequence": 1,
        "sequence": 4,
        "name": "핵심 개념 정의",
        "toast_message": "핵심 개념 정의를 완료했습니다! 💡",
        "template_description": "프로젝트의 핵심 가치 제안과 차별점을 정의하는 문서입니다. 솔루션 개요, 핵심 기능 아이디어, 기대 가치를 포함합니다.",
    },

    # ── Stage 2: 프로젝트 계획 (Ch5) ──────────────────────────────────────
    {
        "stage_sequence": 2,
        "sequence": 1,
        "name": "프로젝트 범위 정의",
        "toast_message": "프로젝트 범위 정의서를 완성했습니다! 📋",
        "template_description": "In/Out Scope와 WBS를 정의하는 문서입니다. 주요 기능 목록, 제외 항목, 산출물 목록을 포함합니다.",
    },
    {
        "stage_sequence": 2,
        "sequence": 2,
        "name": "일정 계획 수립",
        "toast_message": "일정 계획을 완성했습니다! 📅",
        "template_description": "마일스톤과 세부 일정을 계획하는 문서입니다. Gantt 차트, 스프린트 계획, 주요 마일스톤 일정을 포함합니다.",
    },
    {
        "stage_sequence": 2,
        "sequence": 3,
        "name": "리소스 계획 수립",
        "toast_message": "리소스 계획을 완성했습니다! 👨‍💻",
        "template_description": "팀 구성과 역할 분담을 계획하는 문서입니다. 팀원별 담당 역할, 필요 기술 스택, 협업 도구 계획을 포함합니다.",
    },
    {
        "stage_sequence": 2,
        "sequence": 4,
        "name": "리스크 분석",
        "toast_message": "리스크 분석을 완료했습니다! ⚠️",
        "template_description": "프로젝트 리스크를 식별하고 대응 계획을 수립하는 문서입니다. 리스크 목록, 발생 가능성·영향도 매트릭스, 완화 전략을 포함합니다.",
    },

    # ── Stage 3: 요구사항 정의 (Ch6) ──────────────────────────────────────
    {
        "stage_sequence": 3,
        "sequence": 1,
        "name": "기능 요구사항 정의",
        "toast_message": "기능 요구사항 정의서를 완성했습니다! ✅",
        "template_description": "시스템이 수행해야 할 기능을 명세하는 문서입니다. 기능 목록, 우선순위, 입출력 조건을 포함합니다.",
    },
    {
        "stage_sequence": 3,
        "sequence": 2,
        "name": "비기능 요구사항 정의",
        "toast_message": "비기능 요구사항 정의서를 완성했습니다! 🔧",
        "template_description": "성능·보안·가용성 등 품질 요구사항을 정의하는 문서입니다. 응답시간 목표, 보안 정책, 확장성 요건을 포함합니다.",
    },
    {
        "stage_sequence": 3,
        "sequence": 3,
        "name": "사용자 스토리 작성",
        "toast_message": "사용자 스토리를 완성했습니다! 📖",
        "template_description": "사용자 관점의 기능 시나리오를 정의하는 문서입니다. As-a / I-want / So-that 형식의 스토리 목록과 인수 기준을 포함합니다.",
    },
    {
        "stage_sequence": 3,
        "sequence": 4,
        "name": "요구사항 확정",
        "toast_message": "요구사항 확정을 완료했습니다! 📌",
        "template_description": "이해관계자 검토 후 요구사항 기준선을 확정하는 문서입니다. 검토 의견 반영 내역, 최종 기능 목록, 승인 내역을 포함합니다.",
    },

    # ── Stage 4: 설계 (Ch7) ───────────────────────────────────────────────
    {
        "stage_sequence": 4,
        "sequence": 1,
        "name": "시스템 아키텍처 설계",
        "toast_message": "시스템 아키텍처 설계를 완료했습니다! 🏗️",
        "template_description": "전체 시스템 구조와 컴포넌트를 설계하는 문서입니다. 아키텍처 다이어그램, 기술 스택 선택 근거, 배포 구성을 포함합니다.",
    },
    {
        "stage_sequence": 4,
        "sequence": 2,
        "name": "데이터베이스 설계",
        "toast_message": "데이터베이스 설계를 완료했습니다! 🗄️",
        "template_description": "ERD와 데이터 모델을 설계하는 문서입니다. 엔티티 정의, 관계도, 인덱스 전략을 포함합니다.",
    },
    {
        "stage_sequence": 4,
        "sequence": 3,
        "name": "API 설계",
        "toast_message": "API 설계를 완료했습니다! 🔌",
        "template_description": "RESTful API 명세와 인터페이스를 정의하는 문서입니다. 엔드포인트 목록, 요청/응답 스키마, 인증 방식을 포함합니다.",
    },
    {
        "stage_sequence": 4,
        "sequence": 4,
        "name": "UI/UX 설계",
        "toast_message": "UI/UX 설계를 완료했습니다! 🎨",
        "template_description": "화면 설계와 사용자 인터페이스 프로토타입을 작성하는 문서입니다. 화면 흐름도, 와이어프레임, 인터랙션 가이드를 포함합니다.",
    },

    # ── Stage 5: 개발 (Ch8) ───────────────────────────────────────────────
    {
        "stage_sequence": 5,
        "sequence": 1,
        "name": "개발 환경 구성",
        "toast_message": "개발 환경 구성을 완료했습니다! ⚙️",
        "template_description": "개발 환경 셋업과 CI/CD 파이프라인을 구성하는 문서입니다. 로컬 환경 설정, 브랜치 전략, 자동화 파이프라인 구성을 포함합니다.",
    },
    {
        "stage_sequence": 5,
        "sequence": 2,
        "name": "핵심 기능 개발",
        "toast_message": "핵심 기능 개발을 완료했습니다! 🚀",
        "template_description": "주요 비즈니스 로직 구현 내역을 기록하는 문서입니다. 구현된 기능 목록, 주요 기술 결정 사항, 알려진 제약 사항을 포함합니다.",
    },
    {
        "stage_sequence": 5,
        "sequence": 3,
        "name": "API 구현 및 통합",
        "toast_message": "API 구현 및 통합을 완료했습니다! 🔗",
        "template_description": "Backend API와 Frontend 연동 구현 내역을 기록하는 문서입니다. API 구현 현황, 통합 테스트 결과, 미구현 항목을 포함합니다.",
    },
    {
        "stage_sequence": 5,
        "sequence": 4,
        "name": "코드 리뷰 및 리팩토링",
        "toast_message": "코드 리뷰 및 리팩토링을 완료했습니다! ✨",
        "template_description": "코드 품질 검토와 개선 내역을 기록하는 문서입니다. 리뷰 체크리스트, 발견된 이슈 및 개선 사항, 기술 부채 목록을 포함합니다.",
    },

    # ── Stage 6: 테스트 및 검증 (Ch9) ────────────────────────────────────
    {
        "stage_sequence": 6,
        "sequence": 1,
        "name": "단위 테스트 작성",
        "toast_message": "단위 테스트 작성을 완료했습니다! 🧪",
        "template_description": "각 컴포넌트별 단위 테스트 구현 내역을 기록하는 문서입니다. 테스트 커버리지 목표, 주요 테스트 케이스, 커버리지 측정 결과를 포함합니다.",
    },
    {
        "stage_sequence": 6,
        "sequence": 2,
        "name": "통합 테스트 수행",
        "toast_message": "통합 테스트를 완료했습니다! 🔄",
        "template_description": "시스템 통합 테스트와 결함 수정 내역을 기록하는 문서입니다. 통합 테스트 시나리오, 발견된 결함 목록 및 수정 내역을 포함합니다.",
    },
    {
        "stage_sequence": 6,
        "sequence": 3,
        "name": "사용자 인수 테스트",
        "toast_message": "사용자 인수 테스트를 완료했습니다! 👤",
        "template_description": "실제 사용자 관점에서 시스템을 검증하는 문서입니다. UAT 시나리오, 사용자 피드백, 최종 수정 내역을 포함합니다.",
    },
    {
        "stage_sequence": 6,
        "sequence": 4,
        "name": "배포 및 운영 준비",
        "toast_message": "배포 및 운영 준비를 완료했습니다! 🎉",
        "template_description": "운영 환경 배포와 모니터링 체계를 구축하는 문서입니다. 배포 절차서, 운영 모니터링 구성, 장애 대응 매뉴얼을 포함합니다.",
    },
]


def run(db: Session) -> None:
    """Required Step 시드 데이터 삽입. stage_sequence로 Stage를 조회한 뒤 upsert한다."""
    stage_map: dict[int, object] = {
        s.sequence: s.id
        for s in db.query(Stage).all()
    }

    rows = []
    for item in REQUIRED_STEP_DATA:
        seq = item["stage_sequence"]
        if seq not in stage_map:
            raise ValueError(f"Stage sequence {seq} 를 찾을 수 없습니다. Stage 시드를 먼저 실행하세요.")
        rows.append(
            {
                "stage_id": stage_map[seq],
                "name": item["name"],
                "sequence": item["sequence"],
                "toast_message": item["toast_message"],
                "template_description": item["template_description"],
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
                "template_description": insert(RequiredStep).excluded.template_description,
            },
        )
    )
    db.execute(stmt)
    db.commit()
