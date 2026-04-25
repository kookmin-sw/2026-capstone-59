"""
Step Tree 테스트용 더미 데이터 19개 생성 스크립트.
필수 Step 3개 포함 (R1 문제/기회 정의, R2 목표 사용자 분석, R3 유사 서비스 분석).

사용법:
    cd backend
    python -m scripts.seed_dummy_steps

트리 구조 (Stage 1 기준):
    R1 문제/기회 정의 (required, ACCEPTED)
    ├── 아이디어 브레인스토밍 (ACCEPTED)
    │   ├── 핵심 문제 도출 (ACCEPTED)
    │   │   ├── 문제 우선순위 정하기 (READY)
    │   │   ├── 이해관계자 인터뷰 (READY)
    │   │   └── 문제 검증 설문 (READY)
    │   ├── 시장 규모 추정 (CANCELED)
    │   └── 사용자 페인포인트 정리 (CANCELED)
    ├── 경쟁사 조사 (CANCELED)
    └── R2 목표 사용자 분석 (required, ACCEPTED)
        ├── 페르소나 작성 (ACCEPTED)
        │   ├── 사용자 여정 맵 (READY)
        │   ├── 사용자 니즈 분류 (READY)
        │   └── R3 유사 서비스 분석 (required, READY)
        ├── 타겟 시장 세분화 (CANCELED)
        └── 사용자 인터뷰 계획 (CANCELED)
"""

import sys
import uuid
from pathlib import Path

# backend/ 를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session

from app.core.config import settings  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.core.enums import StepStatus  # noqa: E402
from app.core.models.project import Project, ProjectStage  # noqa: E402
from app.core.models.required_step import RequiredStep  # noqa: E402
from app.core.models.stage import Stage  # noqa: E402
from app.core.models.step import Step, StepContent, StepTree  # noqa: E402


def _add_closure(db: Session, step_id: uuid.UUID, parent_step_id: uuid.UUID | None) -> None:
    """Closure Table에 자기 자신 + 조상 경로 삽입."""
    db.add(StepTree(ancestor=step_id, descendant=step_id, depth=0))
    if parent_step_id is None:
        return
    ancestors = db.query(StepTree).filter(StepTree.descendant == parent_step_id).all()
    for row in ancestors:
        db.add(StepTree(ancestor=row.ancestor, descendant=step_id, depth=row.depth + 1))


def _make_step(
    db: Session,
    *,
    project_id: uuid.UUID,
    stage_id: uuid.UUID,
    parent_step_id: uuid.UUID | None,
    name: str,
    status: str,
    sort_order: int,
    required_step_id: uuid.UUID | None = None,
    belonging_required_step_id: uuid.UUID | None = None,
    dictionary: str | None = None,
    mentoring: str | None = None,
) -> Step:
    step = Step(
        id=uuid.uuid4(),
        project_id=project_id,
        stage_id=stage_id,
        parent_step_id=parent_step_id,
        required_step_id=required_step_id,
        belonging_required_step_id=belonging_required_step_id,
        name=name,
        status=status,
        sort_order=sort_order,
    )
    db.add(step)
    db.flush()
    _add_closure(db, step.id, parent_step_id)

    if dictionary or mentoring:
        db.add(StepContent(
            step_id=step.id,
            dictionary=dictionary,
            mentoring=mentoring,
        ))

    return step


def run() -> None:
    db = SessionLocal()
    try:
        # 1) 첫 번째 프로젝트 가져오기 (없으면 에러)
        project = db.query(Project).filter(Project.is_deleted == False).first()  # noqa: E712
        if not project:
            print("❌ 프로젝트가 없습니다. 먼저 프로젝트를 생성하세요.")
            return

        # 2) Stage 1 가져오기
        stage1 = db.query(Stage).filter(Stage.sequence == 1).first()
        if not stage1:
            print("❌ Stage 시드 데이터가 없습니다.")
            return

        # 3) Stage 1의 Required Step 가져오기 (sequence 1, 2, 3)
        rs_list = (
            db.query(RequiredStep)
            .filter(RequiredStep.stage_id == stage1.id)
            .order_by(RequiredStep.sequence)
            .all()
        )
        if len(rs_list) < 3:
            print("❌ Required Step 시드 데이터가 부족합니다.")
            return

        rs1, rs2, rs3 = rs_list[0], rs_list[1], rs_list[2]
        pid = project.id
        sid = stage1.id

        # 4) 기존 Step 데이터 삭제 (해당 프로젝트 + Stage)
        existing = db.query(Step).filter(Step.project_id == pid, Step.stage_id == sid).all()
        if existing:
            ids = [s.id for s in existing]
            db.query(StepTree).filter(
                (StepTree.ancestor.in_(ids)) | (StepTree.descendant.in_(ids))
            ).delete(synchronize_session=False)
            db.query(StepContent).filter(StepContent.step_id.in_(ids)).delete(synchronize_session=False)
            db.query(Step).filter(Step.id.in_(ids)).delete(synchronize_session=False)
            db.flush()

        # ── 트리 생성 (19개) ──────────────────────────────────────────
        # 규칙: 한 부모의 자식 중 ACCEPTED는 최대 1개 (단일 경로)
        #
        # current_path: s1 → s2 → s5 → s4(R2) → s8 → s14
        #
        # R1 문제/기회 정의 ◆ (ACCEPTED)
        # ├── 아이디어 브레인스토밍 (ACCEPTED) ← 유일한 ACCEPTED
        # │   ├── 핵심 문제 도출 (ACCEPTED) ← 유일한 ACCEPTED
        # │   │   ├── R2 목표 사용자 분석 ◆ (ACCEPTED) ← 유일한 ACCEPTED
        # │   │   │   ├── 페르소나 작성 (ACCEPTED) ← 유일한 ACCEPTED
        # │   │   │   │   ├── 사용자 여정 맵 (ACCEPTED) ← 유일한 ACCEPTED
        # │   │   │   │   │   ├── 터치포인트별 개선 기회 도출 (READY)
        # │   │   │   │   │   ├── R3 유사 서비스 분석 ◆ (READY)
        # │   │   │   │   │   └── 사용자 감정 곡선 작성 (READY)
        # │   │   │   │   ├── 사용자 니즈 분류 (CANCELED)
        # │   │   │   │   └── 사용자 세그먼트 정의 (CANCELED)
        # │   │   │   ├── 타겟 시장 세분화 (CANCELED)
        # │   │   │   └── 사용자 인터뷰 계획 (CANCELED)
        # │   │   ├── 문제 우선순위 정하기 (CANCELED)
        # │   │   └── 문제 검증 설문 (CANCELED)
        # │   ├── 시장 규모 추정 (CANCELED)
        # │   └── 사용자 페인포인트 정리 (CANCELED)
        # └── 경쟁사 조사 (CANCELED)

        # Level 0: R1 문제/기회 정의 (required, ACCEPTED)
        s1 = _make_step(db, project_id=pid, stage_id=sid, parent_step_id=None,
                        name="문제/기회 정의", status=StepStatus.ACCEPTED, sort_order=1,
                        required_step_id=rs1.id, belonging_required_step_id=rs1.id,
                        dictionary="문제 정의: 해결하고자 하는 핵심 문제를 명확히 기술하는 활동",
                        mentoring="좋은 문제 정의가 좋은 솔루션의 시작입니다.")

        # Level 1: R1의 자식 2개 (ACCEPTED 1개만)
        s2 = _make_step(db, project_id=pid, stage_id=sid, parent_step_id=s1.id,
                        name="아이디어 브레인스토밍", status=StepStatus.ACCEPTED, sort_order=1,
                        belonging_required_step_id=rs1.id,
                        dictionary="브레인스토밍: 판단 없이 아이디어를 최대한 많이 생성하는 기법",
                        mentoring="양을 먼저 확보하세요. 판단은 나중에!")

        s3 = _make_step(db, project_id=pid, stage_id=sid, parent_step_id=s1.id,
                        name="경쟁사 조사", status=StepStatus.CANCELED, sort_order=2,
                        belonging_required_step_id=rs1.id)

        # Level 2: s2(브레인스토밍)의 자식 3개 (ACCEPTED 1개만)
        s5 = _make_step(db, project_id=pid, stage_id=sid, parent_step_id=s2.id,
                        name="핵심 문제 도출", status=StepStatus.ACCEPTED, sort_order=1,
                        belonging_required_step_id=rs1.id,
                        mentoring="브레인스토밍 결과에서 가장 임팩트 있는 문제를 선별하세요.")

        s6 = _make_step(db, project_id=pid, stage_id=sid, parent_step_id=s2.id,
                        name="시장 규모 추정", status=StepStatus.CANCELED, sort_order=2,
                        belonging_required_step_id=rs1.id)

        s7 = _make_step(db, project_id=pid, stage_id=sid, parent_step_id=s2.id,
                        name="사용자 페인포인트 정리", status=StepStatus.CANCELED, sort_order=3,
                        belonging_required_step_id=rs1.id)

        # Level 3: s5(핵심 문제 도출)의 자식 3개 (ACCEPTED 1개만 = R2)
        s4 = _make_step(db, project_id=pid, stage_id=sid, parent_step_id=s5.id,
                        name="목표 사용자 분석", status=StepStatus.ACCEPTED, sort_order=1,
                        required_step_id=rs2.id, belonging_required_step_id=rs2.id,
                        dictionary="페르소나: 타겟 사용자를 대표하는 가상의 인물 프로필",
                        mentoring="사용자를 깊이 이해하면 제품의 방향이 명확해집니다.")

        s11 = _make_step(db, project_id=pid, stage_id=sid, parent_step_id=s5.id,
                         name="문제 우선순위 정하기", status=StepStatus.CANCELED, sort_order=2,
                         belonging_required_step_id=rs1.id)

        s13 = _make_step(db, project_id=pid, stage_id=sid, parent_step_id=s5.id,
                         name="문제 검증 설문", status=StepStatus.CANCELED, sort_order=3,
                         belonging_required_step_id=rs1.id)

        # Level 4: s4(R2 목표 사용자 분석)의 자식 3개 (ACCEPTED 1개만)
        s8 = _make_step(db, project_id=pid, stage_id=sid, parent_step_id=s4.id,
                        name="페르소나 작성", status=StepStatus.ACCEPTED, sort_order=1,
                        belonging_required_step_id=rs2.id,
                        dictionary="페르소나: 이름, 나이, 직업, 목표, 불편함 등을 구체적으로 설정",
                        mentoring="최소 2개 이상의 페르소나를 만들어보세요.")

        s9 = _make_step(db, project_id=pid, stage_id=sid, parent_step_id=s4.id,
                        name="타겟 시장 세분화", status=StepStatus.CANCELED, sort_order=2,
                        belonging_required_step_id=rs2.id)

        s10 = _make_step(db, project_id=pid, stage_id=sid, parent_step_id=s4.id,
                         name="사용자 인터뷰 계획", status=StepStatus.CANCELED, sort_order=3,
                         belonging_required_step_id=rs2.id)

        # Level 5: s8(페르소나 작성)의 자식 3개 (ACCEPTED 1개만)
        s14 = _make_step(db, project_id=pid, stage_id=sid, parent_step_id=s8.id,
                         name="사용자 여정 맵", status=StepStatus.ACCEPTED, sort_order=1,
                         belonging_required_step_id=rs2.id,
                         dictionary="사용자 여정 맵: 사용자가 서비스를 이용하는 전체 과정을 시각화",
                         mentoring="터치포인트별 감정 변화를 함께 기록하세요.")

        s15 = _make_step(db, project_id=pid, stage_id=sid, parent_step_id=s8.id,
                         name="사용자 니즈 분류", status=StepStatus.CANCELED, sort_order=2,
                         belonging_required_step_id=rs2.id)

        s18 = _make_step(db, project_id=pid, stage_id=sid, parent_step_id=s8.id,
                         name="사용자 세그먼트 정의", status=StepStatus.CANCELED, sort_order=3,
                         belonging_required_step_id=rs2.id)

        # Level 6: s14(사용자 여정 맵)의 자식 3개 (모두 READY = 현재 선택 대기)
        s19 = _make_step(db, project_id=pid, stage_id=sid, parent_step_id=s14.id,
                         name="터치포인트별 개선 기회 도출", status=StepStatus.READY, sort_order=1,
                         belonging_required_step_id=rs2.id)

        s16 = _make_step(db, project_id=pid, stage_id=sid, parent_step_id=s14.id,
                         name="유사 서비스 분석", status=StepStatus.READY, sort_order=2,
                         required_step_id=rs3.id, belonging_required_step_id=rs3.id,
                         dictionary="벤치마킹: 경쟁사 및 유사 서비스의 강점·약점을 비교 분석",
                         mentoring="최소 3개 이상의 유사 서비스를 분석해보세요.")

        s17 = _make_step(db, project_id=pid, stage_id=sid, parent_step_id=s14.id,
                         name="사용자 감정 곡선 작성", status=StepStatus.READY, sort_order=3,
                         belonging_required_step_id=rs2.id)

        db.commit()

        print(f"✅ 더미 Step 19개 생성 완료!")
        print(f"   Project: {project.name} ({pid})")
        print(f"   Stage: {stage1.name} ({sid})")
        print(f"   Required Steps: R1={rs1.name}, R2={rs2.name}, R3={rs3.name}")
        print(f"   ACCEPTED: 6개, CANCELED: 10개, READY: 3개")
        print(f"   current_path: R1 → 브레인스토밍 → 핵심문제도출 → R2 → 페르소나 → 여정맵")

    finally:
        db.close()


if __name__ == "__main__":
    run()
