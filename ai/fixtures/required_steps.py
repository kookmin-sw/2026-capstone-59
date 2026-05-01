"""Stage 1 필수 Step (R1~R4) 시드 데이터.

Poco_Required_Steps_Definition_v1.md §Stage 1 기반.
시뮬레이터/수동 테스트에서 RequiredStepInfo를 즉시 사용할 수 있도록 제공한다.
각 호출은 새 인스턴스를 반환하므로 호출자가 is_completed를 자유롭게 변경해도
다른 호출에 영향을 주지 않는다.
"""

from __future__ import annotations

from ai.schemas.common import RequiredStepInfo

_STAGE_1_DEFINITIONS: list[dict] = [
    {
        "step_id": "1-R1",
        "name": "문제/기회 정의",
        "goal": "프로젝트가 해결하려는 문제 또는 포착한 기회를 명확하게 정의한다.",
        "entry_criteria": "Stage 1의 출발점이므로 별도 선행 맥락 없이 초기 프롬프트만으로 진입 가능하다.",
        "fulfillment_criteria": [
            "문제/기회 자체에 대한 서술·명확화",
            "문제의 중요도·임팩트 (왜 해결할 가치가 있는가)",
            "문제의 발생 배경·상황·맥락",
            "기존 대안의 한계 또는 미해결 지점",
        ],
        "minimum_fulfillment_count": 2,
    },
    {
        "step_id": "1-R2",
        "name": "대상 사용자 파악",
        "goal": "정의된 문제로 불편을 겪는 구체적 사용자군을 식별하고 특성을 그린다.",
        "entry_criteria": "Step 히스토리에 문제/기회에 관한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "1차 타겟 사용자군의 특성 정의 (연령·상황·역할 등)",
            "사용자의 현재 행동·습관·맥락 파악",
            "사용자 페르소나 또는 시나리오 정리",
            "사용자 검증 활동 (인터뷰·관찰·설문 등)",
        ],
        "minimum_fulfillment_count": 2,
    },
    {
        "step_id": "1-R3",
        "name": "핵심 컨셉 정의",
        "goal": "정의된 문제를 어떤 해결책으로 풀지, 그 차별점이 무엇인지 한 단락 수준으로 정리한다.",
        "entry_criteria": "Step 히스토리에 문제 정의와 사용자 이해에 관한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "해결 접근 방식·아이디어 서술",
            "유사/경쟁 서비스 조사 및 비교",
            "차별점 또는 핵심 가치 제안(Value Proposition)",
            "주요 기능의 큰 그림·윤곽",
        ],
        "minimum_fulfillment_count": 2,
    },
    {
        "step_id": "1-R4",
        "name": "실현 가능성 검토",
        "goal": "주어진 기간·인원·기술 수준으로 컨셉을 실제로 만들 수 있는지, 주요 리스크는 무엇인지 판단한다.",
        "entry_criteria": "Step 히스토리에 핵심 컨셉에 대한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "기술적 실현 가능성 검토",
            "기간·자원·인원·비용 관점의 적합성 검토",
            "프로토타입·PoC 등 소규모 검증 활동",
            "주요 리스크·제약사항 식별",
        ],
        "minimum_fulfillment_count": 2,
    },
]


def stage_1_required_steps() -> list[RequiredStepInfo]:
    """Stage 1 R1~R4 4개 RequiredStepInfo 인스턴스 리스트를 반환.

    매 호출 시 새 인스턴스를 만들므로, 시뮬레이터에서 is_completed를
    True로 바꾸는 등 자유롭게 변경할 수 있다.
    """
    return [
        RequiredStepInfo(
            step_id=item["step_id"],
            name=item["name"],
            is_completed=False,
            goal=item["goal"],
            entry_criteria=item["entry_criteria"],
            fulfillment_criteria=list(item["fulfillment_criteria"]),
            minimum_fulfillment_count=item["minimum_fulfillment_count"],
        )
        for item in _STAGE_1_DEFINITIONS
    ]
