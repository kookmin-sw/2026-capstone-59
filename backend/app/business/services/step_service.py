import uuid

from sqlalchemy.orm import Session

from app.core.enums import StepStatus
from app.core.models.step import Step


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
