import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.services import orchestrator
from app.ai.services.rag import retrieve
from app.core.enums import StepStatus
from app.core.exceptions import StepAlreadyAcceptedError, StepNotFoundError
from app.core.models.project_required_step_status import ProjectRequiredStepStatus
from app.core.models.required_step import RequiredStep as RequiredStepModel
from app.core.models.step import Step as StepModel
from app.core.models.step import StepContent as StepContentModel
from app.core.models.step import StepTree as StepTreeModel
from app.core.schemas.step import (
    AcceptedStepItem,
    AcceptRequest,
    CurrentRequiredStep,
    CurrentStage,
    DecisionHistoryItem,
    GeneratedStep,
    GenerateRequest,
    ProjectInfo,
    RequiredStepStatusItem,
    SidePanelDecisionHistoryItem,
    SidePanelRequest,
    StepAcceptResponse,
    StepDetailResponse,
    StepGenerateResponse,
    TargetStep,
)


def _build_project_info(step: StepModel) -> ProjectInfo:
    """Step에서 ProjectInfo 스키마를 구성."""
    project = step.project
    return ProjectInfo(
        project_id=project.id,
        name=project.name,
        duration_months=project.duration_month,
        member_count=project.member_count,
        description=project.description,
        constraints=project.constraint_text,
        initial_prompt=project.prompt,
    )


def _build_current_stage(step: StepModel) -> CurrentStage:
    """Step에서 CurrentStage 스키마를 구성."""
    stage = step.stage
    return CurrentStage(
        stage_id=stage.id,
        stage_number=stage.sequence,
        name=stage.name,
    )


def _get_fulfilled_required_step_ids(
    db: Session, project_id: uuid.UUID
) -> set[uuid.UUID]:
    """프로젝트에서 이미 충족된 Required Step ID 집합."""
    return {
        row.required_step_id
        for row in db.query(ProjectRequiredStepStatus).filter_by(
            project_id=project_id, is_fulfilled=True
        )
    }


def _get_current_required_step(
    db: Session, stage_id: uuid.UUID, fulfilled_ids: set[uuid.UUID]
) -> CurrentRequiredStep | None:
    """현재 Stage에서 미충족 첫 번째 Required Step을 반환."""
    all_required = (
        db.query(RequiredStepModel)
        .filter(RequiredStepModel.stage_id == stage_id)
        .order_by(RequiredStepModel.sequence)
        .all()
    )
    current_rs = next((rs for rs in all_required if rs.id not in fulfilled_ids), None)
    if current_rs is None:
        return None
    return CurrentRequiredStep(
        step_id=current_rs.id,
        name=current_rs.name,
        is_completed=False,
        goal=current_rs.goal,
        entry_criteria=current_rs.entry_criteria,
        fulfillment_aspects=current_rs.fulfillment_aspects,
        fulfillment_threshold=current_rs.fulfillment_threshold,
    )


def _get_required_steps_status(
    db: Session, stage_id: uuid.UUID, fulfilled_ids: set[uuid.UUID]
) -> list[RequiredStepStatusItem]:
    """Stage의 전체 Required Step 상태 목록."""
    all_required = (
        db.query(RequiredStepModel)
        .filter(RequiredStepModel.stage_id == stage_id)
        .order_by(RequiredStepModel.sequence)
        .all()
    )
    return [
        RequiredStepStatusItem(
            name=rs.name,
            order=rs.sequence,
            is_completed=rs.id in fulfilled_ids,
        )
        for rs in all_required
    ]


def _insert_closure_rows(
    db: Session, step_id: uuid.UUID, parent_step_id: uuid.UUID | None
) -> None:
    db.add(StepTreeModel(ancestor=step_id, descendant=step_id, depth=0))
    if parent_step_id is None:
        return
    parent_ancestors = (
        db.query(StepTreeModel).filter(StepTreeModel.descendant == parent_step_id).all()
    )
    for row in parent_ancestors:
        db.add(
            StepTreeModel(
                ancestor=row.ancestor, descendant=step_id, depth=row.depth + 1
            )
        )


def accept_step(db: Session, step_id: uuid.UUID) -> StepAcceptResponse:
    # ① 조회 및 검증
    step = db.get(StepModel, step_id)
    if step is None:
        raise StepNotFoundError()
    if step.status == StepStatus.ACCEPTED:
        raise StepAlreadyAcceptedError()

    # ② ACCEPTED 처리
    step.status = StepStatus.ACCEPTED

    # ③ 형제 Step CANCELED
    if step.parent_step_id is not None:
        siblings = (
            db.query(StepModel)
            .filter(
                StepModel.parent_step_id == step.parent_step_id,
                StepModel.id != step_id,
                StepModel.status == StepStatus.READY,
            )
            .all()
        )
        for sibling in siblings:
            sibling.status = StepStatus.CANCELED

    db.flush()

    # ④ Bedrock 호출 (필수 Step 영역 안에 있을 때만)
    is_completed = False
    if step.belonging_required_step_id is not None:

        # DB에 이미 완료된 상태면 Bedrock 호출 스킵
        existing = db.get(
            ProjectRequiredStepStatus,
            {
                "project_id": step.project_id,
                "required_step_id": step.belonging_required_step_id,
            },
        )
        if existing and existing.is_fulfilled:
            is_completed = True  # 이미 완료 → Bedrock 호출 안 함
        else:
            request = _build_accept_request(db, step)
            result = orchestrator.call_accept(request)
            is_completed = result.get("is_current_required_step_completed", False)
            if is_completed:
                _upsert_required_step_status(
                    db,
                    project_id=step.project_id,
                    required_step_id=step.belonging_required_step_id,
                )

    db.commit()

    return StepAcceptResponse(
        step_id=step_id,
        status=StepStatus.ACCEPTED,
        is_current_required_step_completed=is_completed,
    )


def _build_accept_request(db: Session, step: StepModel) -> AcceptRequest:
    fulfilled_ids = _get_fulfilled_required_step_ids(db, step.project_id)

    current_rs = db.get(RequiredStepModel, step.belonging_required_step_id)
    current_required_step = None
    if current_rs and current_rs.id not in fulfilled_ids:
        current_required_step = CurrentRequiredStep(
            step_id=current_rs.id,
            name=current_rs.name,
            is_completed=False,
            goal=current_rs.goal,
            entry_criteria=current_rs.entry_criteria,
            fulfillment_aspects=current_rs.fulfillment_aspects,
            fulfillment_threshold=current_rs.fulfillment_threshold,
        )

    accepted_in_required = (
        db.query(StepModel)
        .filter(
            StepModel.project_id == step.project_id,
            StepModel.belonging_required_step_id == step.belonging_required_step_id,
            StepModel.status == StepStatus.ACCEPTED,
        )
        .all()
    )

    rag_results = retrieve(f"{step.stage.name} {step.name}")

    return AcceptRequest(
        project_info=_build_project_info(step),
        current_stage=_build_current_stage(step),
        required_steps_status=_get_required_steps_status(
            db, step.stage_id, fulfilled_ids
        ),
        current_required_step=current_required_step,
        accepted_steps_in_required=[
            AcceptedStepItem(step_id=s.id, name=s.name) for s in accepted_in_required
        ],
        accepted_step=AcceptedStepItem(step_id=step.id, name=step.name),
        rag_context={"results": rag_results},
    )


def _upsert_required_step_status(
    db: Session,
    project_id: uuid.UUID,
    required_step_id: uuid.UUID,
) -> None:
    record = db.get(
        ProjectRequiredStepStatus,
        {"project_id": project_id, "required_step_id": required_step_id},
    )
    if record is None:
        record = ProjectRequiredStepStatus(
            project_id=project_id,
            required_step_id=required_step_id,
        )
        db.add(record)
    record.is_fulfilled = True
    record.fulfilled_at = datetime.now(timezone.utc)


def generate_steps(db: Session, parent_step_id: uuid.UUID) -> StepGenerateResponse:
    parent_step = db.get(StepModel, parent_step_id)
    if parent_step is None:
        raise StepNotFoundError(f"Parent Step을 찾을 수 없습니다: {parent_step_id}")

    # ① Bedrock으로 일반 Step 이름 3개 생성
    request = _build_generate_request(db, parent_step)
    result = orchestrator.call_generate(request)
    generated: list[dict] = result.get("generated_steps", [])

    # ② 부모가 필수 Step 영역에 속하면 자식도 같은 영역에 속함
    belonging_rs_id = (
        parent_step.belonging_required_step_id or parent_step.required_step_id
    )

    steps: list[StepModel] = []

    # ③ 필수 Step 노드 포함 여부 판단 + 생성/재사용
    _attach_or_create_required_step_node(db, parent_step, steps)

    # ④ 일반 Step 생성
    _create_generated_step_nodes(db, parent_step, generated, belonging_rs_id, steps)

    db.commit()
    for step in steps:
        db.refresh(step)

    return StepGenerateResponse(
        generated_steps=[
            GeneratedStep(
                step_id=s.id,
                name=s.name,
                status=s.status,
                is_required=s.required_step_id is not None,
                parent_step_id=s.parent_step_id,
            )
            for s in steps
        ]
    )


def _attach_or_create_required_step_node(
    db: Session, parent_step: StepModel, steps: list[StepModel]
) -> None:
    """다음 미충족 필수 Step 노드를 재사용하거나 새로 생성하여 steps에 추가."""
    next_rs_id = _get_next_unfulfilled_required_step_id(db, parent_step)
    if next_rs_id is None:
        return

    already_inside = (
        parent_step.belonging_required_step_id == next_rs_id
        or parent_step.required_step_id == next_rs_id
    )
    if already_inside:
        return

    # 기존 READY 필수 Step 노드 재사용
    existing_pending = (
        db.query(StepModel)
        .filter(
            StepModel.project_id == parent_step.project_id,
            StepModel.stage_id == parent_step.stage_id,
            StepModel.required_step_id == next_rs_id,
            StepModel.status == StepStatus.READY,
        )
        .first()
    )

    if existing_pending:
        existing_pending.parent_step_id = parent_step.id
        existing_pending.sort_order = 0
        db.query(StepTreeModel).filter(
            StepTreeModel.descendant == existing_pending.id
        ).delete()
        db.flush()
        _insert_closure_rows(db, existing_pending.id, parent_step.id)
        db.flush()
        steps.append(existing_pending)
    else:
        next_rs = db.get(RequiredStepModel, next_rs_id)
        req_step = StepModel(
            id=uuid.uuid4(),
            project_id=parent_step.project_id,
            stage_id=parent_step.stage_id,
            parent_step_id=parent_step.id,
            required_step_id=next_rs_id,
            belonging_required_step_id=None,
            name=next_rs.name,
            status=StepStatus.READY,
            sort_order=0,
        )
        db.add(req_step)
        db.flush()
        _insert_closure_rows(db, req_step.id, parent_step.id)
        steps.append(req_step)


def _create_generated_step_nodes(
    db: Session,
    parent_step: StepModel,
    generated: list[dict],
    belonging_rs_id: uuid.UUID | None,
    steps: list[StepModel],
) -> None:
    """AI가 생성한 일반 Step 이름들로 Step 노드를 생성하여 steps에 추가."""
    for i, item in enumerate(generated, start=1):
        step = StepModel(
            id=uuid.uuid4(),
            project_id=parent_step.project_id,
            stage_id=parent_step.stage_id,
            parent_step_id=parent_step.id,
            required_step_id=None,
            belonging_required_step_id=belonging_rs_id,
            name=item["name"],
            status=StepStatus.READY,
            sort_order=i,
        )
        db.add(step)
        db.flush()
        _insert_closure_rows(db, step.id, parent_step.id)
        steps.append(step)


def _build_generate_request(db: Session, parent_step: StepModel) -> GenerateRequest:
    fulfilled_ids = _get_fulfilled_required_step_ids(db, parent_step.project_id)

    accepted_steps = (
        db.query(StepModel)
        .filter(
            StepModel.project_id == parent_step.project_id,
            StepModel.stage_id == parent_step.stage_id,
            StepModel.status == StepStatus.ACCEPTED,
        )
        .all()
    )

    rag_results = retrieve(f"{parent_step.stage.name} {parent_step.name}")

    return GenerateRequest(
        project_info=_build_project_info(parent_step),
        current_stage=_build_current_stage(parent_step),
        current_required_step=_get_current_required_step(
            db, parent_step.stage_id, fulfilled_ids
        ),
        decision_history=[
            DecisionHistoryItem(step_id=s.id, name=s.name, status=s.status)
            for s in accepted_steps
        ],
        current_step=AcceptedStepItem(step_id=parent_step.id, name=parent_step.name),
        rag_context={"results": rag_results},
    )


def _get_next_unfulfilled_required_step_id(
    db: Session, step: StepModel
) -> uuid.UUID | None:
    fulfilled_ids = _get_fulfilled_required_step_ids(db, step.project_id)
    query = db.query(RequiredStepModel).filter(
        RequiredStepModel.stage_id == step.stage_id
    )
    if fulfilled_ids:
        query = query.filter(RequiredStepModel.id.not_in(fulfilled_ids))
    next_rs = query.order_by(RequiredStepModel.sequence).first()
    return next_rs.id if next_rs else None


# 사이드 패널
def get_step_detail(db: Session, step_id: uuid.UUID) -> StepDetailResponse:
    step = db.get(StepModel, step_id)
    if step is None:
        raise StepNotFoundError()

    # 필수 Step → DB에서 반환
    if step.required_step_id is not None:
        content = step.content
        return StepDetailResponse(
            is_required=True,
            step_id=step.id,
            name=step.name,
            mentoring=json.loads(content.mentoring) if content.mentoring else None,
            dictionary=(json.loads(content.dictionary) if content.dictionary else None),
            template_url=content.template_url if content else None,
        )

    # 일반 Step → DB 캐시 확인 후 없으면 AI 호출
    content = step.content
    if content and content.mentoring:
        return StepDetailResponse(
            is_required=False,
            step_id=step.id,
            name=step.name,
            mentoring=json.loads(content.mentoring) if content.mentoring else None,
            dictionary=(json.loads(content.dictionary) if content.dictionary else None),
        )

    # AI 호출
    request = _build_side_panel_request(db, step)
    result = orchestrator.call_side_panel(request)

    # StepContent에 저장
    if content is None:
        content = StepContentModel(step_id=step.id)
        db.add(content)

    content.mentoring = json.dumps(result.get("mentoring"), ensure_ascii=False)
    content.dictionary = json.dumps(result.get("dictionary"), ensure_ascii=False)
    db.commit()

    return StepDetailResponse(
        is_required=False,
        step_id=step.id,
        name=step.name,
        mentoring=result.get("mentoring"),
        dictionary=result.get("dictionary"),
    )


def _build_side_panel_request(db: Session, step: StepModel) -> SidePanelRequest:
    fulfilled_ids = _get_fulfilled_required_step_ids(db, step.project_id)
    stage = step.stage

    accepted_steps = (
        db.query(StepModel)
        .filter(
            StepModel.project_id == step.project_id,
            StepModel.stage_id == step.stage_id,
            StepModel.status == StepStatus.ACCEPTED,
        )
        .all()
    )

    rag_results = retrieve(f"{stage.name} {step.name}")

    return SidePanelRequest(
        project_info=_build_project_info(step),
        current_stage=_build_current_stage(step),
        target_step=TargetStep(step_id=step.id, name=step.name),
        decision_history=[
            SidePanelDecisionHistoryItem(
                step_id=s.id,
                name=s.name,
                status=s.status,
                stage_number=stage.sequence,
            )
            for s in accepted_steps
        ],
        current_required_step=_get_current_required_step(
            db, step.stage_id, fulfilled_ids
        ),
        rag_context={"results": rag_results},
    )
