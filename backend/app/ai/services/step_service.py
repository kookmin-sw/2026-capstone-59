import json
import uuid

from sqlalchemy.orm import Session

from app.ai.services import orchestrator
from app.ai.services.rag import retrieve
from app.core.enums import StepStatus
from app.core.exceptions import StepAlreadyAcceptedError, StepNotFoundError
from app.core.models.step import Step as StepModel
from app.core.repositories import (
    project as project_repo,
    required_step as required_step_repo,
    stage as stage_repo,
    step as step_repo,
)
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


# ────────────────────────── 스키마 변환 헬퍼 ──────────────────────────


def _build_project_info(step: StepModel) -> ProjectInfo:
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
    stage = step.stage
    return CurrentStage(
        stage_id=stage.id,
        stage_sequence=stage.sequence,
        name=stage.name,
    )


def _to_current_required_step(rs) -> CurrentRequiredStep:
    return CurrentRequiredStep(
        step_id=rs.id,
        name=rs.name,
        is_completed=False,
        goal=rs.goal,
        entry_criteria=rs.entry_criteria,
        fulfillment_criteria=rs.fulfillment_criteria,
        minimum_fulfillment_count=rs.minimum_fulfillment_count,
    )


def _get_current_required_step(
    db: Session, stage_id: uuid.UUID, fulfilled_ids: set[uuid.UUID]
) -> CurrentRequiredStep | None:
    """현재 Stage 에서 미충족 첫 번째 Required Step 반환."""
    all_required = required_step_repo.get_required_steps_in_stage(db, stage_id)
    current_rs = next((rs for rs in all_required if rs.id not in fulfilled_ids), None)
    return _to_current_required_step(current_rs) if current_rs else None


def _get_required_steps_status(
    db: Session, stage_id: uuid.UUID, fulfilled_ids: set[uuid.UUID]
) -> list[RequiredStepStatusItem]:
    return [
        RequiredStepStatusItem(
            name=rs.name,
            order=rs.sequence,
            is_completed=rs.id in fulfilled_ids,
        )
        for rs in required_step_repo.get_required_steps_in_stage(db, stage_id)
    ]


# ────────────────────────────── Accept ──────────────────────────────


async def accept_step(db: Session, step_id: uuid.UUID) -> StepAcceptResponse:
    step = step_repo.get_step(db, step_id)
    if step is None:
        raise StepNotFoundError()
    if step.status == StepStatus.ACCEPTED:
        raise StepAlreadyAcceptedError()

    step.status = StepStatus.ACCEPTED

    # 형제 Step 중 일반 Step 만 CANCELED
    if step.parent_step_id is not None:
        for sibling in step_repo.get_ready_siblings(db, step.parent_step_id, step_id):
            if sibling.required_step_id is None:
                sibling.status = StepStatus.CANCELED

    db.flush()

    # Bedrock 호출 (필수 Step 영역 안에 있을 때만)
    is_completed = False
    if step.belonging_required_step_id is not None:
        existing = project_repo.get_required_step_status(
            db, step.project_id, step.belonging_required_step_id
        )
        if existing and existing.is_fulfilled:
            is_completed = True
        else:
            request = _build_accept_request(db, step)
            result = await orchestrator.call_accept(request)
            is_completed = result.is_current_required_step_completed
            if is_completed:
                project_repo.upsert_required_step_fulfilled(
                    db, step.project_id, step.belonging_required_step_id
                )

    db.commit()

    # Stage 완료 여부 확인 + 다음 Stage 활성화
    is_stage_completed = _check_and_advance_stage(db, step)

    return StepAcceptResponse(
        step_id=step_id,
        status=StepStatus.ACCEPTED,
        is_current_required_step_completed=is_completed,
        is_current_stage_completed=is_stage_completed,
    )


def _check_and_advance_stage(db: Session, step: StepModel) -> bool:
    """현재 Stage 의 모든 Required Step 충족됐으면 다음 Stage 를 활성화한다."""
    all_required = required_step_repo.get_required_steps_in_stage(db, step.stage_id)
    fulfilled_ids = project_repo.get_fulfilled_required_step_ids(db, step.project_id)
    is_completed = bool(all_required) and all(
        rs.id in fulfilled_ids for rs in all_required
    )
    if not is_completed:
        return False

    next_stage = stage_repo.get_stage_by_sequence(db, step.stage.sequence + 1)
    if next_stage is None:
        return True

    next_ps = project_repo.get_project_stage(db, step.project_id, next_stage.id)
    if next_ps is not None:
        next_ps.is_active = True
        db.commit()
    return True


def _build_accept_request(db: Session, step: StepModel) -> AcceptRequest:
    fulfilled_ids = project_repo.get_fulfilled_required_step_ids(db, step.project_id)

    current_rs = required_step_repo.get_required_step(
        db, step.belonging_required_step_id
    )
    current_required_step = (
        _to_current_required_step(current_rs)
        if current_rs and current_rs.id not in fulfilled_ids
        else None
    )

    accepted_in_required = step_repo.get_accepted_steps_in_required(
        db, step.project_id, step.belonging_required_step_id
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


# ────────────────────────────── Generate ──────────────────────────────


async def generate_steps(
    db: Session, parent_step_id: uuid.UUID
) -> StepGenerateResponse:
    parent_step = step_repo.get_step(db, parent_step_id)
    if parent_step is None:
        raise StepNotFoundError(f"Parent Step을 찾을 수 없습니다: {parent_step_id}")

    request = _build_generate_request(db, parent_step)
    result = await orchestrator.call_generate(request)
    generated = result.generated_steps

    belonging_rs_id = (
        parent_step.belonging_required_step_id or parent_step.required_step_id
    )

    steps: list[StepModel] = []
    _attach_or_create_required_step_node(db, parent_step, steps)
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
    next_rs_id = _get_next_unfulfilled_required_step_id(db, parent_step)
    if next_rs_id is None:
        return

    already_inside = (
        parent_step.belonging_required_step_id == next_rs_id
        or parent_step.required_step_id == next_rs_id
    )
    if already_inside:
        return

    existing_pending = step_repo.get_existing_pending_required_step(
        db, parent_step.project_id, parent_step.stage_id, next_rs_id
    )

    if existing_pending:
        existing_pending.parent_step_id = parent_step.id
        existing_pending.sort_order = 0
        step_repo.delete_closure_for_descendant(db, existing_pending.id)
        db.flush()
        step_repo.insert_closure_with_parent(db, existing_pending.id, parent_step.id)
        db.flush()
        steps.append(existing_pending)
    else:
        next_rs = required_step_repo.get_required_step(db, next_rs_id)
        req_step = step_repo.add_step(
            db,
            project_id=parent_step.project_id,
            stage_id=parent_step.stage_id,
            parent_step_id=parent_step.id,
            required_step_id=next_rs_id,
            belonging_required_step_id=None,
            name=next_rs.name,
            status=StepStatus.READY,
            sort_order=0,
        )
        step_repo.insert_closure_with_parent(db, req_step.id, parent_step.id)
        steps.append(req_step)


def _create_generated_step_nodes(
    db: Session,
    parent_step: StepModel,
    generated: list,
    belonging_rs_id: uuid.UUID | None,
    steps: list[StepModel],
) -> None:
    for i, item in enumerate(generated, start=1):
        step = step_repo.add_step(
            db,
            project_id=parent_step.project_id,
            stage_id=parent_step.stage_id,
            parent_step_id=parent_step.id,
            required_step_id=None,
            belonging_required_step_id=belonging_rs_id,
            name=item.name,
            status=StepStatus.READY,
            sort_order=i,
        )
        step_repo.insert_closure_with_parent(db, step.id, parent_step.id)
        steps.append(step)


def _build_generate_request(db: Session, parent_step: StepModel) -> GenerateRequest:
    fulfilled_ids = project_repo.get_fulfilled_required_step_ids(
        db, parent_step.project_id
    )
    accepted_steps = step_repo.get_accepted_steps_in_stage(
        db, parent_step.project_id, parent_step.stage_id
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
    fulfilled_ids = project_repo.get_fulfilled_required_step_ids(db, step.project_id)
    all_rs = required_step_repo.get_required_steps_in_stage(db, step.stage_id)
    next_rs = next((rs for rs in all_rs if rs.id not in fulfilled_ids), None)
    return next_rs.id if next_rs else None


# ──────────────────────────── 사이드 패널 ────────────────────────────


async def get_step_detail(db: Session, step_id: uuid.UUID) -> StepDetailResponse:
    step = step_repo.get_step(db, step_id)
    if step is None:
        raise StepNotFoundError()

    # 필수 Step → DB 캐시 또는 RequiredStep 기본값으로 lazy 생성
    if step.required_step_id is not None:
        content = step.content
        if content is None:
            content = _create_default_step_content(db, step)
            db.commit()
        return StepDetailResponse(
            is_required=True,
            step_id=step.id,
            name=step.name,
            mentoring=_loads_or_none(content.mentoring if content else None),
            dictionary=_loads_or_none(content.dictionary if content else None),
            template_url=content.template_url if content else None,
        )

    # 일반 Step → DB 캐시 확인 후 없으면 AI 호출
    content = step.content
    if content and content.mentoring:
        return StepDetailResponse(
            is_required=False,
            step_id=step.id,
            name=step.name,
            mentoring=_loads_or_none(content.mentoring),
            dictionary=_loads_or_none(content.dictionary),
        )

    request = _build_side_panel_request(db, step)
    result = await orchestrator.call_side_panel(request)

    if content is None:
        content = step_repo.add_step_content(db, step.id)

    content.mentoring = json.dumps(result.mentoring.model_dump(), ensure_ascii=False)
    content.dictionary = json.dumps(
        [d.model_dump() for d in result.dictionary], ensure_ascii=False
    )
    db.commit()

    return StepDetailResponse(
        is_required=False,
        step_id=step.id,
        name=step.name,
        mentoring=result.mentoring.model_dump(),
        dictionary=[d.model_dump() for d in result.dictionary],
    )


def _create_default_step_content(db: Session, step: StepModel):
    """RequiredStep 의 default_mentoring/dictionary 를 StepContent 로 복사."""
    rs = required_step_repo.get_required_step(db, step.required_step_id)
    mentoring = (
        json.dumps(rs.default_mentoring, ensure_ascii=False)
        if rs and rs.default_mentoring
        else None
    )
    dictionary = (
        json.dumps(rs.default_dictionary, ensure_ascii=False)
        if rs and rs.default_dictionary
        else None
    )
    return step_repo.add_step_content(
        db, step.id, mentoring=mentoring, dictionary=dictionary
    )


def _loads_or_none(value: str | None):
    return json.loads(value) if value else None


def _build_side_panel_request(db: Session, step: StepModel) -> SidePanelRequest:
    fulfilled_ids = project_repo.get_fulfilled_required_step_ids(db, step.project_id)
    stage = step.stage

    accepted_steps = step_repo.get_accepted_steps_in_stage(
        db, step.project_id, step.stage_id
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
                stage_sequence=stage.sequence,
            )
            for s in accepted_steps
        ],
        current_required_step=_get_current_required_step(
            db, step.stage_id, fulfilled_ids
        ),
        rag_context={"results": rag_results},
    )
