import random
import uuid

from sqlalchemy.orm import Session

from app.core.enums import StepStatus
from app.core.exceptions import NotFoundError
from app.core.models.step import Step, StepTree

_EXAMPLE_STEP_NAMES = [
    "사용자 인터뷰 진행",
    "경쟁사 분석",
    "페르소나 정의",
    "핵심 문제 도출",
    "솔루션 브레인스토밍",
    "유사 서비스 벤치마킹",
    "사용자 여정 맵 작성",
    "문제-솔루션 핏 검증",
    "핵심 가치 제안 정의",
    "초기 아이디어 스케치",
]


def _insert_closure_rows(db: Session, step_id: uuid.UUID, parent_step_id: uuid.UUID | None) -> None:
    db.add(StepTree(ancestor=step_id, descendant=step_id, depth=0))
    if parent_step_id is None:
        return
    parent_ancestors = db.query(StepTree).filter(StepTree.descendant == parent_step_id).all()
    for row in parent_ancestors:
        db.add(StepTree(ancestor=row.ancestor, descendant=step_id, depth=row.depth + 1))


def generate_steps(db: Session, parent_step_id: uuid.UUID) -> list[Step]:
    parent_step = db.get(Step, parent_step_id)
    if parent_step is None:
        raise NotFoundError(f"Parent Step을 찾을 수 없습니다: {parent_step_id}")

    # TODO(AI): Bedrock Claude + RAG 기반 Step 후보 생성
    # context = {
    #     "project_id": parent_step.project_id,
    #     "stage_id": parent_step.stage_id,
    #     "parent_step_name": parent_step.name,
    #     "step_history": <closure table 기반 현재 경로>,
    # }
    # candidates = bedrock_client.invoke(model_id=settings.BEDROCK_MODEL_ID, context=context)
    # → Claude가 3개의 regular step + optional 1 required step 후보를 JSON으로 반환

    chosen_names = random.sample(_EXAMPLE_STEP_NAMES, 3)  # 임시

    steps: list[Step] = []
    for i, name in enumerate(chosen_names):
        step = Step(
            id=uuid.uuid4(),
            project_id=parent_step.project_id,
            stage_id=parent_step.stage_id,
            parent_step_id=parent_step_id,
            required_step_id=None,
            name=name,
            status=StepStatus.READY,
            sort_order=i + 1,
        )
        db.add(step)
        db.flush()
        _insert_closure_rows(db, step.id, parent_step_id)
        steps.append(step)

    db.commit()
    for step in steps:
        db.refresh(step)
    return steps


def get_step_tree(
    db: Session,
    project_id: uuid.UUID,
    stage_id: uuid.UUID,
) -> tuple[list[uuid.UUID], list[Step]]:
    """(current_path, all_steps) 반환. current_path는 ACCEPTED 경로의 step_id 순서 (루트→말단)."""
    steps = (
        db.query(Step)
        .filter(Step.project_id == project_id, Step.stage_id == stage_id)
        .order_by(Step.sort_order)
        .all()
    )

    accepted_ids = {s.id for s in steps if s.status == StepStatus.ACCEPTED}

    current_path: list[uuid.UUID] = []
    # ACCEPTED 경로의 루트: parent가 없거나 parent가 ACCEPTED가 아닌 노드
    current = next(
        (s for s in steps
         if s.id in accepted_ids
         and (s.parent_step_id is None or s.parent_step_id not in accepted_ids)),
        None,
    )
    while current is not None:
        current_path.append(current.id)
        current = next(
            (s for s in steps if s.parent_step_id == current.id and s.id in accepted_ids),
            None,
        )

    return current_path, steps
