"""사이드패널 description 첫 문장 위치감 라벨 deterministic 결정.

R 이름 single source: content/required-steps/names.json
변경 시 _STAGE_FIRST_R_NAMES, _STAGE_LAST_R_NAMES dict 동기화 필요.

라벨은 자연어로만 표현 (Stage N, Step 단어 노출 X).
"""

from __future__ import annotations

from typing import Optional

from ai.schemas.common import RequiredStepInfo


_STAGE_FIRST_R_NAMES: dict[int, str] = {
    1: "문제/기회 정의",
    2: "일정 계획 수립",
    3: "요구사항 도출",
    4: "시스템 아키텍처 정의",
    5: "개발 환경 구축",
    6: "테스트 계획 수립",
}

_STAGE_LAST_R_NAMES: dict[int, str] = {
    1: "실현 가능성 검토",
    2: "개발 환경/도구 결정",
    3: "요구사항 검토",
    4: "설계 리뷰",
    5: "코드 리뷰 및 자체 검증",
    6: "최종 검토",
}

_STAGE_NATURAL_NAMES: dict[int, str] = {
    1: "초기 단계",
    2: "기획 단계",
    3: "요구사항 단계",
    4: "설계 단계",
    5: "개발 단계",
    6: "검증 단계",
}


def resolve_position_label(
    stage_sequence: int,
    current_required_step: Optional[RequiredStepInfo],
) -> str:
    """현재 Stage + R 이름 기반 위치감 라벨 deterministic 결정.

    출력 형태: 자연어만 사용 (Stage N, Step 단어 노출 안 함).
    """
    natural = _STAGE_NATURAL_NAMES.get(stage_sequence, "이 단계")

    if current_required_step is None:
        return f"{natural}의 한 자리"

    name = current_required_step.name

    if name == _STAGE_FIRST_R_NAMES.get(stage_sequence):
        if stage_sequence == 1:
            return "프로젝트의 출발점"
        if stage_sequence == 6:
            return "검증의 출발점"
        return f"{natural}의 첫 걸음"

    if name == _STAGE_LAST_R_NAMES.get(stage_sequence):
        if stage_sequence == 6:
            return "프로젝트의 마지막 관문"
        return f"{natural}의 마무리 지점"

    return f"{natural}의 흐름 안"
