import random
import uuid

from sqlalchemy.orm import Session

from app.core.enums import StepStatus
from app.core.exceptions import StepNotFoundError
from app.core.models.step import Step as StepModel
from app.core.models.step import StepTree as StepTreeModel
from app.core.schemas.step import StepGenerateResponse, GeneratedStep
from app.core.schemas.bedrock import (
    AcceptPayload,
    AcceptedStepItem,
    CurrentRequiredStep,
    CurrentStage,
    ProjectInfo,
    RequiredStepStatusItem,
)
from datetime import datetime, timezone
from app.ai.services import orchestrator
from app.core.exceptions import StepAlreadyAcceptedError
from app.core.models.project_required_step_status import ProjectRequiredStepStatus
from app.core.models.required_step import RequiredStep as RequiredStepModel
from app.ai.services.rag import retrieve


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


def generate_steps(db: Session, parent_step_id: uuid.UUID) -> StepGenerateResponse:
    parent_step = db.get(StepModel, parent_step_id)
    if parent_step is None:
        raise StepNotFoundError(f"Parent Step을 찾을 수 없습니다: {parent_step_id}")

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

    # 부모가 필수 Step 영역에 속하면 자식도 같은 영역에 속함
    belonging_rs_id = (
        parent_step.belonging_required_step_id or parent_step.required_step_id
    )

    steps: list[StepModel] = []
    for i, name in enumerate(chosen_names):
        step = StepModel(
            id=uuid.uuid4(),
            project_id=parent_step.project_id,
            stage_id=parent_step.stage_id,
            parent_step_id=parent_step_id,
            required_step_id=None,
            belonging_required_step_id=belonging_rs_id,
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





def accept_step(db: Session, step_id: uuid.UUID) -> dict:
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
            {"project_id": step.project_id, "required_step_id": step.belonging_required_step_id},
        )
        if existing and existing.is_fulfilled:
            is_completed = True  # 이미 완료 → Bedrock 호출 안 함
        else:
            payload = _build_accept_payload(db, step)
            result = orchestrator.call_accept(payload)
            is_completed = result.get("is_current_required_step_completed", False)
            if is_completed:
                _upsert_required_step_status(
                    db,
                    project_id=step.project_id,
                    required_step_id=step.belonging_required_step_id,
                )

    db.commit()

    return {
        "step_id": step_id,
        "status": StepStatus.ACCEPTED,
        "is_current_required_step_completed": is_completed,
    }


def _build_accept_payload(db: Session, step: StepModel) -> AcceptPayload:
    project = step.project
    stage = step.stage

    all_required = (
        db.query(RequiredStepModel)
        .filter(RequiredStepModel.stage_id == stage.id)
        .order_by(RequiredStepModel.sequence)
        .all()
    )
    fulfilled_ids = {
        row.required_step_id
        for row in db.query(ProjectRequiredStepStatus).filter_by(
            project_id=project.id, is_fulfilled=True
        )
    }

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
            StepModel.project_id == project.id,
            StepModel.belonging_required_step_id == step.belonging_required_step_id,
            StepModel.status == StepStatus.ACCEPTED,
        )
        .all()
    )
    # rag_context: 현재 Stage + Step 이름으로 KB 검색
    rag_results = retrieve(f"{stage.name} {step.name}")


    return AcceptPayload(
        project_info=ProjectInfo(
            project_id=project.id,
            name=project.name,
            duration_months=project.duration_month,
            member_count=project.member_count,
            description=project.description,
            constraints=project.constraint_text,
            initial_prompt=project.prompt,
        ),
        current_stage=CurrentStage(
            stage_id=stage.id,
            stage_number=stage.sequence,
            name=stage.name,
        ),
        required_steps_status=[
            RequiredStepStatusItem(
                name=rs.name,
                order=rs.sequence,
                is_completed=rs.id in fulfilled_ids,
            )
            for rs in all_required
        ],
        current_required_step=current_required_step,
        accepted_steps_in_required=[
            AcceptedStepItem(step_id=s.id, name=s.name)
            for s in accepted_in_required
        ],
        accepted_step=AcceptedStepItem(
            step_id=step.id,
            name=step.name,
        ),
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
