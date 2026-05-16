"""design-export 렌더러 — .md 골격 렌더링."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))

from ai.schemas.design_export import DesignExportInput, DesignExportOutput, RSQuestions

_STAGE_SEQ_TO_NAME: dict[int, str] = {
    1: "아이디어 구체화",
    2: "프로젝트 계획",
    3: "요구사항 정의",
    4: "설계",
    5: "개발",
    6: "테스트 및 검증",
}


def render(
    input_data: DesignExportInput,
    ai_output: DesignExportOutput,
) -> str:
    ctx = input_data.project_context
    constraints_str = (
        ", ".join(ctx.constraints) if ctx.constraints else "(미입력)"
    )

    rs_q_map: dict[str, RSQuestions] = {
        rs_q.required_step_id: rs_q
        for rs_q in ai_output.questions_per_rs
    }

    seen_stage_seqs: list[int] = []
    stage_rs_map: dict[int, list] = {}
    for rs in input_data.selected_required_steps:
        seq = int(rs.required_step_id.split("-")[0])
        if seq not in seen_stage_seqs:
            seen_stage_seqs.append(seq)
            stage_rs_map[seq] = []
        stage_rs_map[seq].append(rs)

    lines: list[str] = []

    lines.append(f"# {ctx.name or '(이름 미설정)'} — 사고 궤적 문서")
    lines.append("")
    lines.append("> **이 문서는 Poco가 생성한 What·Why 사고 궤적 문서입니다.**")
    lines.append(">")
    lines.append("> Poco는 검증된 소프트웨어 개발 방법론(미국 법무부 SDLC 기반)을 따라")
    lines.append("> 사용자가 *\"무엇을·왜 만들지\"* 를 단계별로 결정하도록 돕는 AI 멘토링 도구입니다.")
    lines.append("> 사용자는 6단계 흐름(아이디어 구체화 → 프로젝트 계획 → 요구사항 정의 → 설계 → 개발 → 테스트 및 검증)으로 사고를 진행합니다.")
    lines.append(">")
    lines.append("> **이 문서의 활용 방법**:")
    lines.append("> 이 문서를 컨텍스트로 삼아 사용자가 요청하는 다음 작업(구현·작성·검토 등 How)을 진행해주세요.")
    lines.append("> 사용자는 What·Why를 거쳐 여기에 도착한 상태입니다.")
    lines.append("> 사용자가 *\"답을 적어둔 상태\"* 가 아니라 *\"질문을 인지한 상태\"* 일 수 있으니,")
    lines.append("> 답 디테일이 필요하면 사용자에게 직접 보충 질문해주세요.")
    lines.append(">")
    lines.append("> **답변을 마무리할 때**: *\"어느 쪽을 원하시나요?\"*, *\"더 깊게 파고들고 싶은 게 있으신가요?\"* 같이")
    lines.append("> 사용자에게 다시 공을 넘기는 막연한 질문으로 끝내지 마세요.")
    lines.append("> 대신 이 문서의 What·Why 맥락에 비춰 사용자가 의도한 다음 한 걸음을")
    lines.append("> *\"이 맥락에서는 ~를 ~ 방식으로 시작/구현해보면 어떨까요?\"* 형태로 **구체적이고 개인 맞춤형으로 제안**해주세요.")
    lines.append("> 제안한 방향이 사용자 의도와 맞는지는 한 줄로 확인하되, 그 자체가 답변의 마무리가 되어서는 안 됩니다.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 프로젝트 컨텍스트")
    lines.append("")
    lines.append(f"- 프로젝트 이름: {ctx.name or '(미입력)'}")
    lines.append(f"- 인원·기간: {ctx.member_count}명 / {ctx.duration_months}개월")
    lines.append(f"- 제약사항: {constraints_str}")
    lines.append(f"- 초기 아이디어: {ctx.initial_prompt}")
    lines.append("")
    lines.append("## 사용자가 거쳐온 사고 궤적")
    lines.append("")

    for stage_seq in seen_stage_seqs:
        stage_name = _STAGE_SEQ_TO_NAME.get(stage_seq, "")
        lines.append(f"### Stage {stage_seq} — {stage_name}")
        lines.append("")
        for rs in stage_rs_map[stage_seq]:
            lines.append(f"#### {rs.required_step_id} {rs.required_step_name}")
            lines.append("")
            lines.append(f"**목표**: {rs.goal}")
            lines.append("")
            lines.append("**충족 기준**:")
            for criterion in rs.fulfillment_criteria:
                lines.append(f"- {criterion}")
            lines.append("")
            lines.append("**진행한 결정** (사용자 클릭 순서):")
            if rs.accepted_general_steps:
                for i, step in enumerate(rs.accepted_general_steps, start=1):
                    lines.append(f"{i}. {step.name}")
            else:
                lines.append("(아직 없음)")
            lines.append("")
            lines.append("**이 단계에서 인지한 What·Why 질문**:")
            rs_q = rs_q_map.get(rs.required_step_id)
            if rs_q:
                for q in rs_q.questions:
                    lines.append(f"- {q}")
            else:
                lines.append("- (질문 생성 실패)")
            lines.append("")

    lines.append("## 핵심 What·Why 정리")
    lines.append("")
    for item in ai_output.core_summary:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("---")
    lines.append("")
    generated_at = datetime.now(KST)
    lines.append(f"생성: {generated_at:%Y-%m-%d %H:%M} (KST) / 도구: Poco")

    return "\n".join(lines)
