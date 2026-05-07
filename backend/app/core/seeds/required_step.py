from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.core.models.required_step import RequiredStep
from app.core.models.stage import Stage

# DOJ SDLC 기반 Required Step 시드 데이터 (24개 = 4 per stage × 6 stages)
# - 4개 측면 R: 21개 / 5개 측면 R: 3개 (4-R1, 4-R4, 6-R1)
# - 모든 R 공통 충족 기준: minimum_fulfillment_count = 2
REQUIRED_STEP_DATA: list[dict] = [
    # ── Stage 1: 아이디어 구체화 ──────────────────────────────────────────
    {
        "stage_sequence": 1,
        "sequence": 1,
        "name": "문제/기회 정의",
        "toast_message": "문제/기회 정의를 완료했습니다! 🎯",
        "template_description": "프로젝트가 해결하려는 문제 또는 포착한 기회를 명확하게 정의하는 문서입니다. 문제의 배경, 중요도, 기존 대안의 한계 등을 정리합니다.",
        "goal": "프로젝트가 해결하려는 문제 또는 포착한 기회를 명확하게 정의한다.",
        "entry_criteria": "Stage 1의 출발점이므로 별도 선행 맥락 없이 초기 프롬프트만으로 진입 가능하다.",
        "fulfillment_criteria": [
            "문제/기회 자체에 대한 서술·명확화",
            "문제의 중요도·임팩트 (왜 해결할 가치가 있는가)",
            "문제의 발생 배경·상황·맥락",
            "기존 대안의 한계 또는 미해결 지점",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch3 - Initiation",
        "default_mentoring": {
            "description": "좋은 프로젝트는 '무엇을 만들까'가 아니라 '어떤 문제를 풀까'에서 시작합니다. 문제를 선명하게 정의할수록 이후 설계·개발 단계에서 방향을 잃지 않을 수 있습니다. 이 Step에서는 문제 자체를 깊이 들여다보고, 왜 지금 이 문제가 중요한지를 설득력 있게 기술해 보세요.",
            "recommended_methods": [
                {
                    "title": "5 Whys 기법",
                    "content": "'왜?'를 다섯 번 반복해 문제의 근본 원인을 파고드는 기법입니다. 표면적 증상이 아닌 진짜 원인을 찾는 데 효과적입니다."
                },
                {
                    "title": "Problem Statement 작성",
                    "content": "\"[대상]은 [상황]에서 [문제]를 겪고 있으며, 이로 인해 [임팩트]가 발생한다\" 형식으로 한 문장에 문제를 압축합니다."
                },
                {
                    "title": "경쟁 분석 (Competitive Analysis)",
                    "content": "기존에 이 문제를 해결하려 한 제품·서비스를 조사하고, 그것이 왜 충분하지 않은지 분석합니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "솔루션을 먼저 떠올리고 문제를 역으로 끼워 맞춤",
                    "bad_example": "\"우리는 AI 챗봇을 만들 것이다. 문제는 고객 응대가 느리다는 것이다.\"",
                    "good_example": "\"고객이 야간에 문의할 창구가 없어 구매를 포기하는 경우가 하루 평균 XX건 발생한다.\""
                },
                {
                    "mistake": "문제를 너무 광범위하게 정의",
                    "bad_example": "\"사람들이 건강 관리를 잘 못한다.\"",
                    "good_example": "\"직장인이 점심시간에 빠르게 영양 균형 잡힌 식단을 선택할 정보가 부족하다.\""
                }
            ],
            "one_line_tip": "문제 정의가 흔들리면 모든 설계가 흔들립니다. 팀이 동의할 수 있는 한 문장으로 먼저 합의하세요."
        },
        "default_dictionary": [
            {"term": "Problem Statement", "definition": "해결하려는 문제를 구체적·측정 가능하게 서술한 한두 문장의 선언문"},
            {"term": "근본 원인 (Root Cause)", "definition": "표면적 증상 뒤에 있는 실제 문제의 원인"},
            {"term": "5 Whys", "definition": "'왜?'를 반복해 문제의 핵심 원인까지 파고드는 분석 기법"},
            {"term": "Pain Point", "definition": "사용자가 현재 경험하는 불편·불만족 지점"},
        ],
    },
    {
        "stage_sequence": 1,
        "sequence": 2,
        "name": "대상 사용자 파악",
        "toast_message": "대상 사용자 파악을 완료했습니다! 👥",
        "template_description": "정의된 문제로 불편을 겪는 구체적 사용자군을 식별하고 특성을 정리하는 문서입니다. 페르소나, 사용 맥락, 검증 활동 등을 포함합니다.",
        "goal": "정의된 문제로 불편을 겪는 구체적 사용자군을 식별하고 특성을 그린다.",
        "entry_criteria": "Step 히스토리에 문제/기회에 관한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "1차 타겟 사용자군의 특성 정의 (연령·상황·역할 등)",
            "사용자의 현재 행동·습관·맥락 파악",
            "사용자 페르소나 또는 시나리오 정리",
            "사용자 검증 활동 (인터뷰·관찰·설문 등)",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch3 - Stakeholder Analysis",
        "default_mentoring": {
            "description": "아무리 훌륭한 아이디어라도 실제 사용자가 원하지 않으면 의미가 없습니다. 이 Step에서는 '누구를 위한 서비스인가'를 구체적으로 그려봄으로써, 이후 기능 정의와 UX 설계의 기준점을 만듭니다.",
            "recommended_methods": [
                {
                    "title": "사용자 인터뷰",
                    "content": "타겟 사용자 3~5명과 30분 내외 인터뷰를 진행합니다. '현재 어떻게 하고 있나요?'처럼 행동 중심 질문이 효과적입니다."
                },
                {
                    "title": "페르소나 작성",
                    "content": "이름·나이·직업·목표·불편함을 담은 가상 사용자 카드를 만듭니다. 팀 전체가 동일한 사용자 이미지를 공유하는 데 도움이 됩니다."
                },
                {
                    "title": "공감 지도 (Empathy Map)",
                    "content": "사용자가 무엇을 보고·듣고·생각하고·느끼는지 4분면으로 정리해 깊은 이해를 이끌어냅니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "타겟을 너무 넓게 설정",
                    "bad_example": "\"20~50대 스마트폰 사용자\"",
                    "good_example": "\"주 3회 이상 헬스장을 다니는 25~35세 직장인\""
                },
                {
                    "mistake": "가정만으로 페르소나를 작성하고 실제 검증을 생략",
                    "bad_example": "팀원끼리 브레인스토밍으로 페르소나 완성",
                    "good_example": "최소 3명 인터뷰 후 공통 패턴을 페르소나에 반영"
                }
            ],
            "one_line_tip": "페르소나는 실제 인터뷰 데이터를 기반으로 만들어야 팀의 의사결정 기준이 될 수 있습니다."
        },
        "default_dictionary": [
            {"term": "페르소나 (Persona)", "definition": "타겟 사용자를 대표하는 가상 인물 프로필"},
            {"term": "공감 지도 (Empathy Map)", "definition": "사용자의 생각·감정·행동을 시각화한 프레임워크"},
            {"term": "사용자 세그먼트", "definition": "공통된 특성이나 필요를 가진 사용자 집단"},
            {"term": "사용자 검증 (User Validation)", "definition": "가설로 만든 페르소나를 실제 사용자와의 접촉으로 확인하는 활동"},
        ],
    },
    {
        "stage_sequence": 1,
        "sequence": 3,
        "name": "핵심 컨셉 정의",
        "toast_message": "핵심 컨셉 정의를 완료했습니다! 💡",
        "template_description": "문제를 어떤 해결책으로 풀지, 그 차별점이 무엇인지 한 단락 수준으로 정리하는 문서입니다. 유사 서비스 비교와 핵심 가치 제안을 포함합니다.",
        "goal": "정의된 문제를 어떤 해결책으로 풀지, 그 차별점이 무엇인지 한 단락 수준으로 정리한다.",
        "entry_criteria": "Step 히스토리에 문제 정의와 사용자 이해에 관한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "해결 접근 방식·아이디어 서술",
            "유사/경쟁 서비스 조사 및 비교",
            "차별점 또는 핵심 가치 제안(Value Proposition)",
            "주요 기능의 큰 그림·윤곽",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch4 - System Concept Development",
        "default_mentoring": {
            "description": "문제와 사용자를 파악했다면 이제 '어떻게 풀 것인가'를 명확히 할 차례입니다. 컨셉은 구체적인 기능 목록이 아니라, 제품의 핵심 가치와 차별점을 한눈에 보여주는 방향타입니다.",
            "recommended_methods": [
                {
                    "title": "엘리베이터 피치",
                    "content": "30초 안에 서비스를 설명할 수 있어야 합니다. \"[타겟]을 위한 [제품]으로, [핵심 가치]를 제공합니다. 기존 [경쟁 대안]과 달리 [차별점]이 있습니다.\" 형식을 활용하세요."
                },
                {
                    "title": "경쟁사 비교표 (Competitive Matrix)",
                    "content": "주요 경쟁 서비스를 나열하고 핵심 기능·가격·타겟별로 비교해 빈 포지션(Blue Ocean)을 찾습니다."
                },
                {
                    "title": "MVP 범위 설정",
                    "content": "핵심 가치를 검증하기 위한 최소한의 기능 집합을 정의합니다. \"없으면 서비스가 성립하지 않는 기능\"만 MVP에 포함합니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "차별점 없이 기존 서비스를 단순 모방",
                    "bad_example": "\"카카오톡과 비슷하지만 UI가 더 예쁨\"",
                    "good_example": "\"특정 직군(간호사)의 교대근무 특성에 맞춘 일정 공유 기능 제공\""
                },
                {
                    "mistake": "기능을 너무 많이 나열해 핵심이 흐려짐",
                    "bad_example": "20가지 기능 목록",
                    "good_example": "핵심 가치 1~2개 + 그것을 가능하게 하는 3~5개 기능"
                }
            ],
            "one_line_tip": "\"우리 서비스가 없어지면 사용자가 가장 아쉬워할 것 하나\"가 핵심 가치입니다."
        },
        "default_dictionary": [
            {"term": "가치 제안 (Value Proposition)", "definition": "제품·서비스가 사용자에게 제공하는 핵심 혜택과 차별점"},
            {"term": "MVP (Minimum Viable Product)", "definition": "핵심 가치를 검증하기 위한 최소 기능만 갖춘 초기 제품"},
            {"term": "Blue Ocean", "definition": "경쟁이 없거나 미개척된 새로운 시장 공간"},
            {"term": "엘리베이터 피치", "definition": "30~60초 안에 아이디어를 설득력 있게 전달하는 짧은 발표"},
        ],
    },
    {
        "stage_sequence": 1,
        "sequence": 4,
        "name": "실현 가능성 검토",
        "toast_message": "실현 가능성 검토를 완료했습니다! 🔬",
        "template_description": "주어진 기간·인원·기술 수준으로 컨셉을 실제로 만들 수 있는지 판단하는 문서입니다. 기술/자원 적합성, 검증 활동, 리스크를 포함합니다.",
        "goal": "주어진 기간·인원·기술 수준으로 컨셉을 실제로 만들 수 있는지, 주요 리스크는 무엇인지 판단한다.",
        "entry_criteria": "Step 히스토리에 핵심 컨셉에 대한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "기술적 실현 가능성 검토",
            "기간·자원·인원·비용 관점의 적합성 검토",
            "프로토타입·PoC 등 소규모 검증 활동",
            "주요 리스크·제약사항 식별",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch4 - Feasibility Study",
        "default_mentoring": {
            "description": "멋진 아이디어도 주어진 시간·팀 역량 안에서 만들 수 없다면 의미가 없습니다. 이 Step은 '할 수 있는가'를 솔직하게 점검하는 시간입니다. 과욕을 걸러내고 현실적인 범위를 확정하는 데 집중하세요.",
            "recommended_methods": [
                {
                    "title": "기술 스파이크 (Technical Spike)",
                    "content": "불확실한 기술 요소를 1~2일 내 빠르게 프로토타이핑해 구현 가능 여부를 확인합니다. 예: AI API 연동 샘플 코드 작성."
                },
                {
                    "title": "SWOT 분석",
                    "content": "강점(S)·약점(W)·기회(O)·위협(T) 관점에서 프로젝트 가능성을 점검합니다."
                },
                {
                    "title": "Work Breakdown Structure (WBS)",
                    "content": "전체 작업을 세부 단위로 쪼개어 각각의 난이도와 소요 시간을 추정합니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "기술 학습 시간을 일정에 반영하지 않음",
                    "bad_example": "처음 써보는 기술 스택으로 4주 내 완성 계획",
                    "good_example": "1주 학습·PoC → 3주 개발 일정으로 분리"
                },
                {
                    "mistake": "리스크를 낙관적으로 무시",
                    "bad_example": "\"외부 API는 아마 잘 될 것이다\"",
                    "good_example": "\"외부 API 장애 시 캐시로 대체\" 대응책 수립"
                }
            ],
            "one_line_tip": "\"이 기능을 구현해본 적 있는가?\" — 없다면 반드시 PoC를 먼저 해보세요."
        },
        "default_dictionary": [
            {"term": "PoC (Proof of Concept)", "definition": "아이디어나 기술의 실현 가능성을 검증하기 위한 소규모 시험 구현"},
            {"term": "기술 스파이크 (Technical Spike)", "definition": "불확실한 기술 요소를 탐색·검증하는 짧은 실험적 개발 작업"},
            {"term": "WBS (Work Breakdown Structure)", "definition": "프로젝트 전체 작업을 계층적으로 세분화한 구조"},
            {"term": "SWOT 분석", "definition": "강점·약점·기회·위협을 분석해 전략을 도출하는 프레임워크"},
        ],
    },
    # ── Stage 2: 프로젝트 계획 ────────────────────────────────────────────
    {
        "stage_sequence": 2,
        "sequence": 1,
        "name": "일정 계획 수립",
        "toast_message": "일정 계획 수립을 완료했습니다! 📅",
        "template_description": "프로젝트 전체 기간을 Stage/마일스톤 단위로 배분하는 일정 뼈대를 정의하는 문서입니다. 마일스톤, 공수 추정, 일정 도구를 포함합니다.",
        "goal": "프로젝트 전체 기간을 Stage/마일스톤 단위로 배분하는 일정 뼈대를 만든다.",
        "entry_criteria": "Step 히스토리에 \"무엇을 얼마나 만들 것인지\"에 대한 컨셉·실현 가능성 맥락이 존재한다.",
        "fulfillment_criteria": [
            "전체 일정을 Stage/구간으로 분할",
            "주요 마일스톤 또는 데드라인 설정",
            "Step/작업 단위의 공수·난이도 추정",
            "일정 관리 방식·도구 선정",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch5 - Schedule Planning",
        "default_mentoring": {
            "description": "일정 계획은 단순한 달력 채우기가 아닙니다. 팀이 무엇을 언제까지 해야 하는지 합의하고, 예상치 못한 상황에 대응할 여유를 미리 확보하는 작업입니다.",
            "recommended_methods": [
                {
                    "title": "간트 차트 (Gantt Chart)",
                    "content": "작업별 시작일·종료일을 막대 그래프로 시각화합니다. Notion, Google Sheets, Jira 등으로 간편하게 작성할 수 있습니다."
                },
                {
                    "title": "스프린트 계획 (Sprint Planning)",
                    "content": "2주 단위로 목표를 설정하고 달성 여부를 점검합니다. 짧은 사이클이 계획 대비 실제 진행을 빠르게 가시화합니다."
                },
                {
                    "title": "버퍼 추가 (Buffer Time)",
                    "content": "각 마일스톤에 10~20% 여유 시간을 추가합니다. 실제 개발에서 예상보다 시간이 오래 걸리는 경우가 매우 흔합니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "버퍼 없이 빡빡하게 일정을 짬",
                    "bad_example": "매주 기능 N개 완성으로 꽉 채운 일정",
                    "good_example": "마지막 2주를 통합·테스트·버퍼로 남겨둠"
                },
                {
                    "mistake": "의존 관계 고려 없이 작업 나열",
                    "bad_example": "DB 설계 전에 프론트엔드 구현 시작",
                    "good_example": "API 명세 → 백엔드 → 프론트엔드 순서로 의존성 반영"
                }
            ],
            "one_line_tip": "일정은 한 번 세우면 끝이 아닙니다. 매 스프린트마다 재조정하는 것이 정상입니다."
        },
        "default_dictionary": [
            {"term": "마일스톤 (Milestone)", "definition": "프로젝트의 주요 완료 지점을 나타내는 기준점"},
            {"term": "간트 차트 (Gantt Chart)", "definition": "작업의 일정과 진행 상황을 시각화한 막대형 차트"},
            {"term": "스프린트 (Sprint)", "definition": "애자일 방법론에서 2주 내외의 짧은 개발 사이클"},
            {"term": "공수 추정 (Effort Estimation)", "definition": "작업 완료에 필요한 시간·인력을 사전에 예측하는 활동"},
        ],
    },
    {
        "stage_sequence": 2,
        "sequence": 2,
        "name": "역할 분담",
        "toast_message": "역할 분담을 완료했습니다! 👨‍👩‍👧",
        "template_description": "팀원 각자의 담당 영역과 책임 범위를 명시하는 문서입니다. 1인 프로젝트인 경우 본인의 역할들을 명시적으로 구분합니다.",
        "goal": "팀원 각자의 담당 영역을 정하고, 1인 프로젝트인 경우 본인이 맡을 역할들을 명시적으로 구분한다.",
        "entry_criteria": "Step 히스토리에 프로젝트의 범위·일정에 대한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "팀원별 주 담당 영역 또는 역할 정의",
            "역할 간 경계와 책임 범위 명시",
            "의사결정·리뷰 주체 결정",
            "협업·커뮤니케이션 규칙 수립",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch5 - Resource Planning",
        "default_mentoring": {
            "description": "\"다 같이 한다\"는 말은 종종 \"아무도 책임지지 않는다\"로 이어집니다. 역할을 명확히 정해두면 의사결정 속도가 빨라지고, 문제가 생겼을 때 누가 해결해야 하는지 분명해집니다.",
            "recommended_methods": [
                {
                    "title": "RACI 매트릭스",
                    "content": "각 작업에 대해 Responsible(실행)·Accountable(책임)·Consulted(협의)·Informed(공유) 역할을 표로 정리합니다."
                },
                {
                    "title": "역할 카드 작성",
                    "content": "각자의 역할명·주요 책임·결정 권한·인터페이스(누구와 협업하는가)를 한 장으로 정리합니다."
                },
                {
                    "title": "온보딩 문서 (팀 규칙)",
                    "content": "회의 주기·코드 리뷰 규칙·PR 승인 방식 등 협업 규칙을 문서화해 팀원 모두가 볼 수 있게 공유합니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "역할 경계가 모호해 중복·공백 발생",
                    "bad_example": "\"백엔드는 A, 나머지는 같이\"",
                    "good_example": "\"인증/API는 A, DB 설계는 B, 프론트엔드 전체는 C, 배포는 A+B 공동\""
                },
                {
                    "mistake": "의사결정 프로세스 미정",
                    "bad_example": "의견 충돌 시 해결 방법 없음",
                    "good_example": "\"기술 결정은 다수결, 최종 컨펌은 팀장\" 규칙 수립"
                }
            ],
            "one_line_tip": "역할 분담 문서는 누군가 빠졌을 때 빠르게 대응할 수 있는 비상 계획이기도 합니다."
        },
        "default_dictionary": [
            {"term": "RACI 매트릭스", "definition": "작업별 역할(실행·책임·협의·공유)을 명확히 정의한 책임 분담 표"},
            {"term": "오너십 (Ownership)", "definition": "특정 기능·영역에 대한 책임과 결정 권한을 갖는 것"},
            {"term": "스크럼 마스터", "definition": "팀의 애자일 프로세스를 촉진·관리하는 역할"},
            {"term": "코드 오너 (Code Owner)", "definition": "특정 코드 영역의 변경을 검토·승인할 책임이 있는 사람"},
        ],
    },
    {
        "stage_sequence": 2,
        "sequence": 3,
        "name": "위험 식별",
        "toast_message": "위험 식별을 완료했습니다! ⚠️",
        "template_description": "프로젝트 진행을 방해할 수 있는 주요 리스크를 미리 식별하고 대응 방향을 정하는 문서입니다.",
        "goal": "프로젝트 진행을 방해할 수 있는 주요 리스크를 미리 식별하고 대응 방향을 정한다.",
        "entry_criteria": "Step 히스토리에 일정·역할·기술 선택 등 \"깨질 수 있는 계획\"이 존재한다.",
        "fulfillment_criteria": [
            "기술 리스크 식별 (난이도·학습 곡선 등)",
            "일정 리스크 식별 (딜레이 요인·병목)",
            "팀 리스크 식별 (이탈·역량·커뮤니케이션)",
            "각 리스크별 대응·완화 방안",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch5 - Risk Management",
        "default_mentoring": {
            "description": "리스크 관리는 불안을 없애는 게 아니라, 불안을 관리 가능한 항목으로 만드는 것입니다. 미리 식별된 리스크는 발생해도 당황하지 않고 대응할 수 있습니다.",
            "recommended_methods": [
                {
                    "title": "리스크 매트릭스 (Risk Matrix)",
                    "content": "각 리스크를 '발생 가능성'과 '영향도' 두 축으로 평가해 우선순위를 정합니다. 고가능성·고영향 리스크부터 집중 관리합니다."
                },
                {
                    "title": "브레인스토밍으로 리스크 목록 작성",
                    "content": "팀원 각자가 \"무엇이 잘못될 수 있나?\"를 적고 공유합니다. 기술·일정·팀·외부 요인 4가지 카테고리로 분류하면 빠짐없이 정리됩니다."
                },
                {
                    "title": "Pre-mortem 기법",
                    "content": "\"프로젝트가 실패했다고 가정하고, 왜 실패했는지\" 거꾸로 생각해 잠재 원인을 발굴합니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "리스크를 식별만 하고 대응책을 세우지 않음",
                    "bad_example": "\"API 제한이 리스크\" (끝)",
                    "good_example": "\"API 제한 → 무료 플랜 한도 확인 후 캐싱 전략 적용, 초과 시 유료 전환 검토\""
                },
                {
                    "mistake": "기술 리스크만 보고 팀 리스크를 무시",
                    "bad_example": "기술 스택 리스크만 5개 나열",
                    "good_example": "팀원 이탈·시험 기간 겹침 등 팀 리스크도 포함"
                }
            ],
            "one_line_tip": "리스크는 발생하기 전이 아니라, 발생 직후에 대응 계획이 있어야 실제로 도움이 됩니다."
        },
        "default_dictionary": [
            {"term": "리스크 (Risk)", "definition": "프로젝트 목표 달성에 부정적 영향을 줄 수 있는 불확실한 사건"},
            {"term": "리스크 매트릭스", "definition": "리스크를 발생 가능성과 영향도로 평가해 우선순위를 정하는 도구"},
            {"term": "완화 전략 (Mitigation Strategy)", "definition": "리스크가 발생할 가능성을 줄이거나 영향을 최소화하는 방안"},
            {"term": "Pre-mortem", "definition": "프로젝트 실패를 미리 가정해 잠재 문제를 사전에 발굴하는 기법"},
        ],
    },
    {
        "stage_sequence": 2,
        "sequence": 4,
        "name": "개발 환경/도구 결정",
        "toast_message": "개발 환경/도구 결정을 완료했습니다! 🛠️",
        "template_description": "프로젝트에서 공통으로 사용할 기술 스택과 협업 도구를 확정하는 문서입니다.",
        "goal": "프로젝트에서 공통으로 사용할 기술 스택과 협업 도구를 확정한다.",
        "entry_criteria": "Step 히스토리에 컨셉·실현 가능성 맥락이 존재하여 어떤 기술 영역이 필요할지 판단 가능하다.",
        "fulfillment_criteria": [
            "개발 언어·프레임워크 선정",
            "형상관리·브랜치 전략 (Git 등)",
            "협업·이슈 관리 도구 선정",
            "개발·배포 환경 구성 방향",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch5 - Tool Selection",
        "default_mentoring": {
            "description": "기술 스택은 한 번 결정하면 바꾸기 어렵습니다. 팀의 현재 역량, 커뮤니티 지원, 프로젝트 요구사항을 종합적으로 고려해 결정하세요.",
            "recommended_methods": [
                {
                    "title": "기술 스택 결정 기준 수립",
                    "content": "팀 숙련도·생태계 성숙도·성능 요구사항·학습 비용 4가지 기준으로 후보 기술을 비교합니다."
                },
                {
                    "title": "Git 브랜치 전략 선택",
                    "content": "GitHub Flow(메인+피처 브랜치)는 소규모 팀에 적합합니다. Git Flow는 릴리즈 관리가 중요한 대규모 프로젝트에 적합합니다."
                },
                {
                    "title": "README + 개발 환경 설정 문서화",
                    "content": "신규 팀원이 30분 내에 개발 환경을 구축할 수 있도록 설치 가이드를 작성합니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "트렌디한 기술을 팀 역량 고려 없이 선택",
                    "bad_example": "팀원 모두 처음 써보는 Rust로 백엔드 개발",
                    "good_example": "팀 평균 숙련도가 높은 Python/FastAPI 선택 후 일부만 새 기술 시도"
                },
                {
                    "mistake": "브랜치 전략 없이 모두 main에 직접 Push",
                    "bad_example": "git push origin main",
                    "good_example": "feature/기능명 브랜치 → PR → 리뷰 → merge 워크플로 수립"
                }
            ],
            "one_line_tip": "\"최고의 기술\"보다 \"팀이 잘 쓸 수 있는 기술\"이 프로젝트를 살립니다."
        },
        "default_dictionary": [
            {"term": "기술 스택 (Tech Stack)", "definition": "프로젝트에서 사용하는 언어·프레임워크·인프라의 조합"},
            {"term": "GitHub Flow", "definition": "메인 브랜치와 피처 브랜치만 사용하는 단순한 Git 협업 전략"},
            {"term": "CI/CD", "definition": "코드 변경을 자동으로 빌드·테스트·배포하는 지속적 통합/배포 파이프라인"},
            {"term": "컨테이너 (Container)", "definition": "애플리케이션과 실행 환경을 패키징해 어디서나 동일하게 실행하는 기술 (Docker 등)"},
        ],
    },
    # ── Stage 3: 요구사항 정의 ────────────────────────────────────────────
    {
        "stage_sequence": 3,
        "sequence": 1,
        "name": "요구사항 도출",
        "toast_message": "요구사항 도출을 완료했습니다! 📥",
        "template_description": "시스템이 수행해야 할 일들을 사용자와 팀의 관점에서 자유롭게 모으는 문서입니다. 인터뷰·브레인스토밍 등 도출 활동 결과를 포함합니다.",
        "goal": "시스템이 수행해야 할 일들을 사용자와 팀의 관점에서 자유롭게 모은다.",
        "entry_criteria": "Step 히스토리에 대상 사용자와 핵심 컨셉에 대한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "사용자 관점의 필요(user needs) 수집",
            "도출 기법 적용 (인터뷰·브레인스토밍·유스케이스 등)",
            "유사 서비스·경쟁 분석을 통한 요구사항 추출",
            "초기 요구사항 후보 목록 정리",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch6 - Requirements Elicitation",
        "default_mentoring": {
            "description": "요구사항 도출은 '만들어야 할 것 목록'을 만드는 과정이 아닙니다. 사용자가 실제로 필요한 것을 발견하는 탐색 과정입니다. 이 단계에서는 판단을 미루고 최대한 많이 수집하세요.",
            "recommended_methods": [
                {
                    "title": "사용자 스토리 (User Story)",
                    "content": "\"나는 [역할]로서, [목적]을 위해 [기능]을 원한다\" 형식으로 작성합니다. 기능 중심이 아닌 사용자 가치 중심으로 요구사항을 표현합니다."
                },
                {
                    "title": "유스케이스 다이어그램",
                    "content": "시스템과 사용자(Actor) 간의 상호작용을 도식화합니다. 기능의 범위와 경계를 시각적으로 파악하는 데 효과적입니다."
                },
                {
                    "title": "KJ법 (친화도 분석)",
                    "content": "개별 요구사항을 포스트잇에 적고 유사한 것끼리 묶어 카테고리를 만듭니다. 산발적인 아이디어를 구조화하는 데 유용합니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "요구사항과 솔루션(구현 방법)을 혼동",
                    "bad_example": "\"React로 대시보드를 만든다\" (솔루션)",
                    "good_example": "\"사용자는 프로젝트 현황을 한 화면에서 파악할 수 있어야 한다\" (요구사항)"
                },
                {
                    "mistake": "개발팀 관점으로만 요구사항을 도출",
                    "bad_example": "팀원끼리 기능 목록 나열",
                    "good_example": "사용자 인터뷰 또는 설문으로 실제 필요 수집"
                }
            ],
            "one_line_tip": "요구사항 도출 단계에서는 \"왜?\"를 자주 물어보세요. 기능 뒤에 숨은 진짜 필요를 찾아낼 수 있습니다."
        },
        "default_dictionary": [
            {"term": "요구사항 (Requirement)", "definition": "시스템이 갖춰야 할 기능·조건·특성에 대한 명세"},
            {"term": "사용자 스토리 (User Story)", "definition": "사용자 관점에서 원하는 기능을 서술한 짧은 문장"},
            {"term": "유스케이스 (Use Case)", "definition": "사용자와 시스템 간의 상호작용 시나리오를 구조화한 명세"},
            {"term": "이해관계자 (Stakeholder)", "definition": "프로젝트 결과에 영향을 받거나 영향을 주는 모든 사람"},
        ],
    },
    {
        "stage_sequence": 3,
        "sequence": 2,
        "name": "기능 요구사항 정의",
        "toast_message": "기능 요구사항 정의를 완료했습니다! ✅",
        "template_description": "시스템이 제공해야 할 기능들을 구체적이고 검증 가능한 형태로 정의하는 문서입니다.",
        "goal": "시스템이 제공해야 할 기능들을 구체적이고 검증 가능한 형태로 정의한다.",
        "entry_criteria": "Step 히스토리에 요구사항 도출 활동과 그 결과 맥락이 존재한다.",
        "fulfillment_criteria": [
            "핵심 기능의 명세화",
            "기능을 유스케이스·유저스토리 등으로 기술",
            "기능 간 관계·의존성 정리",
            "입력·출력·동작 조건 명시",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch6 - Functional Requirements",
        "default_mentoring": {
            "description": "기능 요구사항은 \"시스템이 무엇을 해야 하는가\"를 명확하게 정의합니다. 모호한 요구사항은 개발 중 끝없는 재작업의 원인이 됩니다. 각 요구사항은 테스트 가능한 수준으로 구체적이어야 합니다.",
            "recommended_methods": [
                {
                    "title": "요구사항 명세서 (SRS) 작성",
                    "content": "각 기능을 ID·이름·설명·입력·출력·전제조건·후조건으로 구조화해 문서화합니다."
                },
                {
                    "title": "인수 기준 (Acceptance Criteria) 정의",
                    "content": "\"Given-When-Then\" 형식으로 각 기능의 완료 조건을 명시합니다. 예: Given 로그인 상태, When 게시글 작성 버튼 클릭, Then 에디터 화면이 표시된다."
                },
                {
                    "title": "기능 트리 (Feature Tree)",
                    "content": "기능을 계층 구조로 시각화해 전체 범위를 한눈에 파악하고 누락된 기능을 찾습니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "요구사항을 모호하게 작성",
                    "bad_example": "\"빠른 검색을 제공한다\"",
                    "good_example": "\"검색 결과는 쿼리 입력 후 1초 내에 표시되어야 한다\""
                },
                {
                    "mistake": "예외 상황·에러 케이스 누락",
                    "bad_example": "로그인 성공 케이스만 명세",
                    "good_example": "로그인 실패·계정 잠금·비밀번호 오류 케이스도 명세"
                }
            ],
            "one_line_tip": "\"이 요구사항을 어떻게 테스트할 것인가?\"를 물어보면 모호한 요구사항을 즉시 발견할 수 있습니다."
        },
        "default_dictionary": [
            {"term": "기능 요구사항 (Functional Requirement)", "definition": "시스템이 수행해야 하는 특정 기능이나 서비스에 대한 명세"},
            {"term": "인수 기준 (Acceptance Criteria)", "definition": "기능이 완료됐다고 판단하는 조건"},
            {"term": "SRS (Software Requirements Specification)", "definition": "소프트웨어 시스템의 요구사항을 체계적으로 기술한 문서"},
            {"term": "Given-When-Then", "definition": "테스트 시나리오를 전제조건-행동-기대결과 형식으로 기술하는 패턴"},
        ],
    },
    {
        "stage_sequence": 3,
        "sequence": 3,
        "name": "비기능 요구사항 정의",
        "toast_message": "비기능 요구사항 정의를 완료했습니다! 🔧",
        "template_description": "성능·보안·사용성 등 기능 외적으로 시스템이 갖춰야 할 품질 속성을 정의하는 문서입니다.",
        "goal": "성능·보안·사용성 등 기능 외적으로 시스템이 갖춰야 할 품질 속성을 정의한다.",
        "entry_criteria": "Step 히스토리에 기능 요구사항에 대한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "성능·응답 시간·처리량 관련 요구사항",
            "보안·인증·데이터 보호 요구사항",
            "사용성·접근성 요구사항",
            "호환성·확장성·유지보수성 요구사항",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch6 - Non-Functional Requirements",
        "default_mentoring": {
            "description": "기능이 동작해도 느리거나, 보안이 취약하거나, 쓰기 불편하다면 사용자는 떠납니다. 비기능 요구사항은 '어떻게 동작해야 하는가'를 정의하며, 후반부에 추가하면 매우 비싼 대가를 치릅니다.",
            "recommended_methods": [
                {
                    "title": "FURPS+ 모델 활용",
                    "content": "기능성(Functionality)·사용성(Usability)·신뢰성(Reliability)·성능(Performance)·지원성(Supportability)으로 분류해 빠짐없이 정의합니다."
                },
                {
                    "title": "성능 목표 수치화",
                    "content": "\"빠르다\"가 아닌 \"API 응답 시간 95th 퍼센타일 기준 500ms 이내\"처럼 측정 가능한 기준을 설정합니다."
                },
                {
                    "title": "보안 체크리스트 활용",
                    "content": "OWASP Top 10을 기준으로 SQL Injection·XSS·인증·권한 관련 요구사항을 점검합니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "비기능 요구사항을 아예 빠뜨림",
                    "bad_example": "기능 요구사항 목록만 작성",
                    "good_example": "성능·보안·사용성 각각 최소 1~2개 요구사항 정의"
                },
                {
                    "mistake": "수치 없이 모호하게 작성",
                    "bad_example": "\"시스템은 안정적이어야 한다\"",
                    "good_example": "\"시스템 가용성은 99.5% 이상을 목표로 한다\""
                }
            ],
            "one_line_tip": "비기능 요구사항은 아키텍처 결정에 직접 영향을 줍니다. 설계 전에 반드시 확정하세요."
        },
        "default_dictionary": [
            {"term": "비기능 요구사항 (Non-Functional Requirement)", "definition": "기능 외의 품질 속성 — 성능·보안·사용성·확장성 등"},
            {"term": "가용성 (Availability)", "definition": "시스템이 정상적으로 사용 가능한 시간의 비율"},
            {"term": "OWASP Top 10", "definition": "웹 애플리케이션의 주요 보안 취약점 10가지를 정리한 표준 목록"},
            {"term": "SLA (Service Level Agreement)", "definition": "서비스 제공자와 사용자 간에 합의된 서비스 품질 기준"},
        ],
    },
    {
        "stage_sequence": 3,
        "sequence": 4,
        "name": "요구사항 검토",
        "toast_message": "요구사항 검토를 완료했습니다! 📌",
        "template_description": "도출된 요구사항의 일관성·실현 가능성·우선순위를 팀이 함께 점검하고 확정하는 문서입니다.",
        "goal": "도출된 요구사항의 일관성·실현 가능성·우선순위를 팀이 함께 점검하고 확정한다.",
        "entry_criteria": "Step 히스토리에 기능·비기능 요구사항이 모두 논의된 맥락이 존재한다.",
        "fulfillment_criteria": [
            "요구사항 간 중복·충돌 정리",
            "우선순위 부여 (Must/Should/Could 또는 MVP 포함 여부)",
            "요구사항 실현 가능성 재점검",
            "요구사항 추적 체계 수립 (매트릭스 등)",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch6 - Requirements Review",
        "default_mentoring": {
            "description": "요구사항 목록을 작성했다면 이제 '이것들이 정말 옳은가'를 검토할 차례입니다. 이 단계에서 발견한 문제는 설계·개발 단계보다 10~100배 저렴하게 수정할 수 있습니다.",
            "recommended_methods": [
                {
                    "title": "MoSCoW 우선순위 기법",
                    "content": "Must Have(필수)·Should Have(중요)·Could Have(있으면 좋음)·Won't Have(제외)로 분류합니다. Must Have가 너무 많다면 범위를 재조정해야 합니다."
                },
                {
                    "title": "요구사항 추적 매트릭스 (RTM)",
                    "content": "각 요구사항이 어떤 설계 요소·테스트 케이스와 연결되는지 표로 정리합니다. 개발 완료 후 누락된 요구사항을 찾는 데 필수적입니다."
                },
                {
                    "title": "인스펙션 (Inspection)",
                    "content": "팀원이 요구사항 문서를 읽고 모호함·충돌·누락을 지적하는 구조적 검토를 진행합니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "모든 요구사항을 Must Have로 분류",
                    "bad_example": "20개 기능 전부 MVP 필수",
                    "good_example": "핵심 가치와 직결된 5~7개만 Must Have로 설정"
                },
                {
                    "mistake": "요구사항 변경 이력을 관리하지 않음",
                    "bad_example": "수정 때마다 덮어씀",
                    "good_example": "버전 번호·변경일·변경 이유를 기록"
                }
            ],
            "one_line_tip": "\"이 요구사항이 없어도 서비스가 성립하는가?\"를 물어보면 Must Have와 Nice-to-Have를 구분할 수 있습니다."
        },
        "default_dictionary": [
            {"term": "MoSCoW 기법", "definition": "요구사항을 Must/Should/Could/Won't 4단계 우선순위로 분류하는 방법"},
            {"term": "RTM (Requirements Traceability Matrix)", "definition": "요구사항과 설계·구현·테스트를 연결해 추적하는 표"},
            {"term": "범위 크리프 (Scope Creep)", "definition": "통제되지 않은 요구사항 추가로 프로젝트 범위가 점차 확장되는 현상"},
            {"term": "기준선 (Baseline)", "definition": "공식적으로 합의·확정된 요구사항 버전"},
        ],
    },
    # ── Stage 4: 설계 ────────────────────────────────────────────────────
    {
        "stage_sequence": 4,
        "sequence": 1,
        "name": "시스템 아키텍처 정의",
        "toast_message": "시스템 아키텍처 정의를 완료했습니다! 🏗️",
        "template_description": "시스템을 구성할 주요 컴포넌트와 상호 관계를 큰 그림 수준으로 그리는 문서입니다. 컴포넌트 식별, 통신 관계, 아키텍처 패턴, 요구사항 매핑, 배포 구조를 포함합니다.",
        "goal": "시스템을 구성할 주요 컴포넌트와 상호 관계를 큰 그림 수준으로 그린다.",
        "entry_criteria": "Step 히스토리에 확정된 요구사항에 대한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "주요 구성요소 식별 (프론트·백·DB·외부 서비스 등)",
            "구성요소 간 통신·의존 관계",
            "아키텍처 패턴·스타일 선택 (모놀리식/3-tier 등)",
            "요구사항의 구성요소 배분·매핑 (requirement allocation)",
            "배포·인프라 구조의 큰 그림",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch7 - System Architecture",
        "default_mentoring": {
            "description": "아키텍처는 나중에 바꾸기 가장 어려운 결정들의 집합입니다. 지금 잘못된 구조를 선택하면 개발 중후반에 전체를 다시 뜯어야 할 수 있습니다. 단순하게 시작해 필요할 때 복잡하게 만드는 것이 원칙입니다.",
            "recommended_methods": [
                {
                    "title": "C4 모델",
                    "content": "Context(전체 그림)→Container(애플리케이션/DB)→Component(모듈)→Code(클래스) 4단계로 아키텍처를 문서화합니다. 청중에 맞는 단계를 선택해 커뮤니케이션하세요."
                },
                {
                    "title": "ADR (Architecture Decision Record)",
                    "content": "주요 아키텍처 결정을 \"문제·선택지·결정·이유\" 형식으로 기록합니다. 나중에 왜 그런 결정을 했는지 추적할 수 있습니다."
                },
                {
                    "title": "트레이드오프 분석",
                    "content": "모놀리식 vs 마이크로서비스, REST vs GraphQL 등 주요 선택지의 장단점을 팀이 함께 비교합니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "처음부터 과도하게 복잡한 아키텍처 선택",
                    "bad_example": "사용자 10명 서비스에 MSA + Kubernetes 도입",
                    "good_example": "모놀리식으로 시작, 확장 필요 시 분리"
                },
                {
                    "mistake": "배포 환경을 고려하지 않은 설계",
                    "bad_example": "로컬에서만 동작하는 설계",
                    "good_example": "AWS/GCP 등 배포 환경의 제약사항을 설계에 반영"
                }
            ],
            "one_line_tip": "좋은 아키텍처는 변화에 열려 있어야 합니다. 지금 모든 걸 완벽하게 설계하려 하지 마세요."
        },
        "default_dictionary": [
            {"term": "아키텍처 (Architecture)", "definition": "시스템의 주요 구성요소와 그 관계·원칙을 정의한 구조적 설계"},
            {"term": "3-Tier 아키텍처", "definition": "프레젠테이션·비즈니스 로직·데이터 계층으로 분리된 전통적 아키텍처"},
            {"term": "C4 모델", "definition": "Context·Container·Component·Code 4단계로 소프트웨어 아키텍처를 시각화하는 방법"},
            {"term": "ADR (Architecture Decision Record)", "definition": "아키텍처 결정 사항과 그 이유를 기록한 문서"},
        ],
    },
    {
        "stage_sequence": 4,
        "sequence": 2,
        "name": "데이터 모델 설계",
        "toast_message": "데이터 모델 설계를 완료했습니다! 🗄️",
        "template_description": "시스템이 다룰 핵심 데이터 엔티티와 관계를 정의하는 문서입니다. ERD, 속성, 제약조건을 포함합니다.",
        "goal": "시스템이 다룰 핵심 데이터 엔티티와 관계를 정의한다.",
        "entry_criteria": "Step 히스토리에 기능 요구사항과 아키텍처 맥락이 존재한다.",
        "fulfillment_criteria": [
            "핵심 엔티티·속성 식별",
            "엔티티 간 관계(1:N, N:M 등) 정의",
            "데이터 타입·제약조건 정리",
            "저장소 선택 및 스키마 구조화 (ERD 등)",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch7 - Data Design",
        "default_mentoring": {
            "description": "데이터 모델은 시스템의 뼈대입니다. 잘못된 데이터 모델은 개발 후반에 대규모 마이그레이션을 요구합니다. 핵심 엔티티와 관계를 충분히 고민한 뒤 ERD를 작성하세요.",
            "recommended_methods": [
                {
                    "title": "ERD (Entity-Relationship Diagram)",
                    "content": "엔티티·속성·관계를 시각화한 다이어그램입니다. DBDiagram.io, draw.io 등으로 간편하게 작성할 수 있습니다."
                },
                {
                    "title": "정규화 (Normalization)",
                    "content": "1NF→2NF→3NF 단계로 데이터 중복을 제거하고 일관성을 확보합니다. 단, 성능을 위해 의도적 비정규화도 고려합니다."
                },
                {
                    "title": "인덱스 전략 수립",
                    "content": "자주 조회되는 컬럼에 인덱스를 미리 설계합니다. FK 컬럼과 WHERE 절에 자주 등장하는 컬럼이 주요 후보입니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "관계 설정 없이 모든 데이터를 하나의 테이블에 몰아넣음",
                    "bad_example": "user 테이블에 주문·상품 정보까지 컬럼으로 추가",
                    "good_example": "user / order / product 테이블 분리 후 FK 관계 설정"
                },
                {
                    "mistake": "N:M 관계를 중간 테이블 없이 설계",
                    "bad_example": "user 테이블에 tags 컬럼을 콤마 구분 텍스트로",
                    "good_example": "user_tags 중간 테이블로 N:M 관계 표현"
                }
            ],
            "one_line_tip": "데이터 모델을 팀원 모두가 이해할 수 있어야 합니다. ERD 한 장으로 30초 안에 설명할 수 있으면 잘 설계된 것입니다."
        },
        "default_dictionary": [
            {"term": "ERD (Entity-Relationship Diagram)", "definition": "데이터 엔티티와 그 관계를 시각화한 다이어그램"},
            {"term": "정규화 (Normalization)", "definition": "데이터 중복을 제거하고 일관성을 확보하기 위해 테이블을 분리하는 과정"},
            {"term": "외래키 (Foreign Key)", "definition": "다른 테이블의 기본키를 참조해 테이블 간 관계를 설정하는 컬럼"},
            {"term": "인덱스 (Index)", "definition": "데이터 검색 속도를 높이기 위해 특정 컬럼에 생성하는 자료구조"},
        ],
    },
    {
        "stage_sequence": 4,
        "sequence": 3,
        "name": "인터페이스 설계",
        "toast_message": "인터페이스 설계를 완료했습니다! 🔌",
        "template_description": "외부(UI·외부 API)와 내부(컴포넌트 간) 주요 인터페이스의 모습을 정의하는 문서입니다.",
        "goal": "외부(UI·외부 API)와 내부(컴포넌트 간) 주요 인터페이스의 모습을 정의한다.",
        "entry_criteria": "Step 히스토리에 아키텍처·데이터 모델 맥락이 존재한다.",
        "fulfillment_criteria": [
            "사용자 UI 구성 (와이어프레임·화면 구조 등)",
            "API 엔드포인트·입출력 스펙",
            "컴포넌트 간 내부 인터페이스",
            "외부 서비스 연동 인터페이스",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch7 - Interface Design",
        "default_mentoring": {
            "description": "인터페이스 설계는 프론트엔드와 백엔드, 팀원과 팀원 사이의 계약서입니다. API 명세가 확정돼야 병렬 개발이 가능하고, 와이어프레임이 있어야 불필요한 재작업을 줄일 수 있습니다.",
            "recommended_methods": [
                {
                    "title": "API First 설계",
                    "content": "구현 전 OpenAPI(Swagger) 스펙을 먼저 작성합니다. 프론트엔드는 Mock 서버로 개발을 병렬 진행할 수 있습니다."
                },
                {
                    "title": "와이어프레임 (Wireframe)",
                    "content": "Figma·Balsamiq 등으로 화면 레이아웃을 스케치합니다. 색상·디자인보다 정보 구조와 흐름에 집중하세요."
                },
                {
                    "title": "사용자 플로우 (User Flow)",
                    "content": "사용자가 목표를 달성하기까지 거치는 화면 순서를 다이어그램으로 그립니다. 빠진 화면이나 엣지 케이스를 미리 발견할 수 있습니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "API 명세 없이 프론트엔드와 백엔드가 각자 개발",
                    "bad_example": "개발 완료 후 연동 시 필드명·타입 불일치 발생",
                    "good_example": "사전에 OpenAPI 스펙 합의 후 각자 개발"
                },
                {
                    "mistake": "와이어프레임 없이 바로 UI 개발",
                    "bad_example": "개발 후 레이아웃 전면 수정",
                    "good_example": "로우파이 와이어프레임 → 팀 리뷰 → 개발"
                }
            ],
            "one_line_tip": "API 명세는 프론트엔드와 백엔드의 언어입니다. 구현 전에 합의하면 연동 버그가 절반으로 줄어듭니다."
        },
        "default_dictionary": [
            {"term": "REST API", "definition": "HTTP 메서드(GET/POST/PUT/DELETE)로 자원을 다루는 웹 인터페이스 설계 원칙"},
            {"term": "와이어프레임 (Wireframe)", "definition": "화면의 정보 구조와 레이아웃을 간단하게 표현한 UI 스케치"},
            {"term": "OpenAPI (Swagger)", "definition": "REST API의 엔드포인트·파라미터·응답을 표준 형식으로 문서화하는 명세"},
            {"term": "목 서버 (Mock Server)", "definition": "실제 API 없이 정의된 스펙에 따라 가짜 응답을 반환하는 개발용 서버"},
        ],
    },
    {
        "stage_sequence": 4,
        "sequence": 4,
        "name": "설계 리뷰",
        "toast_message": "설계 리뷰를 완료했습니다! 🔍",
        "template_description": "설계물이 요구사항을 충족하는지, 팀이 같은 그림을 공유하는지 점검하는 문서입니다. 매핑 점검, 누락 점검, 결정 사항 검토, 수정 방향을 포함합니다.",
        "goal": "설계물이 요구사항을 충족하는지, 팀이 같은 그림을 공유하는지 점검한다.",
        "entry_criteria": "Step 히스토리에 아키텍처·데이터 모델·인터페이스 설계 맥락이 모두 존재한다.",
        "fulfillment_criteria": [
            "요구사항과 설계 간의 매핑 점검",
            "설계 간 불일치·누락 점검",
            "성능·보안·확장성 관점의 설계 점검",
            "설계 결정 사항의 적절성 점검 (기술·프레임워크 선택, 프로토타입 결과 반영, 외부 컴포넌트 활용)",
            "리뷰 결과 반영·수정 방향 정리",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch7 - Design Review",
        "default_mentoring": {
            "description": "설계 리뷰는 개발 전 마지막 안전망입니다. 코드를 작성하기 전에 설계의 허점을 발견하는 것이 수백 배 저렴합니다. 팀원 각자가 다른 관점(성능·보안·확장성)에서 검토하면 더 많은 문제를 발견할 수 있습니다.",
            "recommended_methods": [
                {
                    "title": "설계 워크스루 (Design Walkthrough)",
                    "content": "설계자가 팀에게 설계 내용을 순서대로 설명하고, 팀원은 질문과 의견을 제시합니다. 설계자가 설명하면서 스스로 문제를 발견하는 경우도 많습니다."
                },
                {
                    "title": "요구사항-설계 매핑 체크",
                    "content": "RTM을 활용해 각 요구사항이 설계의 어느 부분에 반영됐는지 확인합니다. 매핑되지 않은 요구사항은 설계에서 누락된 것입니다."
                },
                {
                    "title": "보안·성능 체크리스트",
                    "content": "인증·권한·입력 검증(보안), DB 쿼리 최적화·캐싱 전략(성능) 관점에서 설계를 점검합니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "리뷰를 형식적으로만 진행",
                    "bad_example": "\"다들 괜찮아 보여요\" → 리뷰 종료",
                    "good_example": "각자 사전에 설계 문서를 읽고 질문 목록을 준비해 참석"
                },
                {
                    "mistake": "리뷰 결과를 문서에 반영하지 않음",
                    "bad_example": "구두로 수정 사항 공유 후 끝",
                    "good_example": "설계 문서에 변경사항 반영 후 재배포"
                }
            ],
            "one_line_tip": "\"이 설계대로 개발하면 3개월 후에 유지보수할 수 있는가?\"를 스스로에게 물어보세요."
        },
        "default_dictionary": [
            {"term": "설계 리뷰 (Design Review)", "definition": "개발 전 설계의 정확성·완전성·일관성을 검토하는 공식 점검 활동"},
            {"term": "워크스루 (Walkthrough)", "definition": "작성자가 문서·코드를 팀에게 설명하며 피드백을 받는 비공식 검토"},
            {"term": "기술 부채 (Technical Debt)", "definition": "빠른 개발을 위해 지름길을 선택할 때 나중에 갚아야 할 추가 작업"},
            {"term": "확장성 (Scalability)", "definition": "사용자·데이터 증가에 따라 시스템 성능을 유지하는 능력"},
        ],
    },
    # ── Stage 5: 개발 ────────────────────────────────────────────────────
    {
        "stage_sequence": 5,
        "sequence": 1,
        "name": "개발 환경 구축",
        "toast_message": "개발 환경 구축을 완료했습니다! ⚙️",
        "template_description": "팀원이 동일한 환경에서 개발·빌드·실행할 수 있도록 기본 환경과 저장소를 구성하는 문서입니다.",
        "goal": "팀원이 동일한 환경에서 개발·빌드·실행할 수 있도록 기본 환경과 저장소를 구성한다.",
        "entry_criteria": "Step 히스토리에 기술 스택 결정과 설계 맥락이 존재한다.",
        "fulfillment_criteria": [
            "코드 저장소·브랜치 전략 구성",
            "로컬 개발 환경·의존성 세팅",
            "프로젝트 스캐폴드·초기 구조 수립",
            "빌드·실행·배포 스크립트 기초 구성",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch8 - Development Environment",
        "default_mentoring": {
            "description": "\"내 컴퓨터에서는 됩니다\"는 팀 프로젝트에서 가장 위험한 말입니다. 개발 환경을 표준화하면 이 문제를 원천 차단하고, 새 팀원의 온보딩 시간도 크게 줄일 수 있습니다.",
            "recommended_methods": [
                {
                    "title": "Docker Compose로 환경 표준화",
                    "content": "DB·캐시 등 인프라를 Docker Compose로 정의하면 팀원 누구나 동일한 환경을 한 명령으로 구축할 수 있습니다."
                },
                {
                    "title": ".env.example 파일 관리",
                    "content": "환경변수 목록을 .env.example에 키만 정의하고 Git에 커밋합니다. 실제 값이 담긴 .env는 .gitignore에 추가해 유출을 방지합니다."
                },
                {
                    "title": "Makefile 또는 npm scripts",
                    "content": "자주 사용하는 명령(실행·빌드·테스트·마이그레이션)을 단축 명령으로 등록합니다. README에서 안내해 팀원이 쉽게 사용할 수 있게 합니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "환경 설정 방법을 문서화하지 않음",
                    "bad_example": "구두로 설명",
                    "good_example": "README에 단계별 설치 가이드 작성"
                },
                {
                    "mistake": "시크릿 키·API 키를 코드에 하드코딩",
                    "bad_example": "코드에 SECRET_KEY = 'abc123'",
                    "good_example": "환경변수로 관리, .env는 .gitignore에 추가"
                }
            ],
            "one_line_tip": "개발 환경 설정 문서는 6개월 뒤 본인을 위한 것이기도 합니다. 상세하게 작성하세요."
        },
        "default_dictionary": [
            {"term": "Docker Compose", "definition": "여러 컨테이너로 구성된 애플리케이션을 하나의 YAML 파일로 정의·실행하는 도구"},
            {"term": ".env 파일", "definition": "환경변수를 파일로 관리하는 방식. DB 접속 정보·API 키 등을 코드에서 분리"},
            {"term": "스캐폴드 (Scaffold)", "definition": "프로젝트의 기본 디렉토리 구조와 설정 파일을 자동 생성하는 초기 뼈대"},
            {"term": ".gitignore", "definition": "Git이 추적하지 않을 파일·디렉토리를 지정하는 설정 파일"},
        ],
    },
    {
        "stage_sequence": 5,
        "sequence": 2,
        "name": "핵심 기능 구현",
        "toast_message": "핵심 기능 구현을 완료했습니다! 🚀",
        "template_description": "MVP 핵심 기능을 설계에 따라 구현하는 문서입니다. 기능별 구현, 공통 모듈, 비즈니스 로직, 진입점 구현을 포함합니다.",
        "goal": "MVP 핵심 기능을 설계에 따라 구현한다.",
        "entry_criteria": "Step 히스토리에 개발 환경 구축과 설계 맥락이 존재한다.",
        "fulfillment_criteria": [
            "핵심 기능별 구현 작업",
            "공통 모듈·유틸리티 구현",
            "데이터 처리·비즈니스 로직 구현",
            "UI 또는 진입점(엔드포인트) 구현",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch8 - Core Implementation",
        "default_mentoring": {
            "description": "핵심 기능 구현은 프로젝트의 심장부입니다. 설계 문서를 자주 참고하면서 구현하되, 설계와 현실 사이의 간극이 보이면 즉시 팀과 논의하세요. 혼자 해결하려다 엉뚱한 방향으로 가는 경우가 많습니다.",
            "recommended_methods": [
                {
                    "title": "TDD (Test Driven Development)",
                    "content": "테스트를 먼저 작성하고 구현합니다. 요구사항을 코드로 표현하는 과정에서 명세의 모호함을 조기에 발견할 수 있습니다."
                },
                {
                    "title": "작은 단위로 커밋 (Atomic Commit)",
                    "content": "하나의 커밋은 하나의 논리적 변경만 포함합니다. 문제 발생 시 특정 커밋으로 되돌리기 쉬워집니다."
                },
                {
                    "title": "페어 프로그래밍",
                    "content": "복잡한 로직은 두 명이 함께 작업하면 버그를 즉시 잡고 지식을 공유할 수 있습니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "설계 없이 코딩부터 시작",
                    "bad_example": "\"일단 만들어보고 나중에 리팩토링\"",
                    "good_example": "인터페이스 정의 → 테스트 작성 → 구현 순서"
                },
                {
                    "mistake": "너무 오래 커밋하지 않음",
                    "bad_example": "3일 동안 작업 후 한 번에 커밋",
                    "good_example": "하루 2~3번 의미 있는 단위로 커밋"
                }
            ],
            "one_line_tip": "\"이 코드를 6개월 뒤의 내가 이해할 수 있는가?\"를 기준으로 작성하세요."
        },
        "default_dictionary": [
            {"term": "TDD (Test Driven Development)", "definition": "테스트를 먼저 작성하고 그 테스트를 통과하는 코드를 구현하는 개발 방식"},
            {"term": "비즈니스 로직", "definition": "애플리케이션의 핵심 규칙·처리 과정을 구현한 코드"},
            {"term": "Atomic Commit", "definition": "하나의 논리적 변경만 포함하는 최소 단위 커밋"},
            {"term": "리팩토링 (Refactoring)", "definition": "외부 동작을 바꾸지 않고 코드 내부 구조를 개선하는 활동"},
        ],
    },
    {
        "stage_sequence": 5,
        "sequence": 3,
        "name": "코드 통합",
        "toast_message": "코드 통합을 완료했습니다! 🔗",
        "template_description": "개별 모듈을 하나의 실행 가능한 시스템으로 통합하는 문서입니다.",
        "goal": "개별 모듈을 하나의 실행 가능한 시스템으로 통합한다.",
        "entry_criteria": "Step 히스토리에 개별 기능·모듈 구현에 대한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "모듈 간 연결 작업 (프론트-백-DB 등)",
            "엔드투엔드 시나리오 연결",
            "통합 과정의 충돌·에러 해결",
            "통합 빌드·실행 검증",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch8 - Integration",
        "default_mentoring": {
            "description": "각각은 잘 동작해도 붙이면 안 되는 경우가 흔합니다. 통합은 일찍, 자주 할수록 문제를 작은 단위로 발견할 수 있습니다. CI를 활용하면 통합 문제를 자동으로 감지할 수 있습니다.",
            "recommended_methods": [
                {
                    "title": "지속적 통합 (CI) 설정",
                    "content": "GitHub Actions 등으로 PR마다 빌드·테스트를 자동 실행합니다. 통합 오류를 코드 머지 전에 발견할 수 있습니다."
                },
                {
                    "title": "Contract Testing",
                    "content": "프론트엔드와 백엔드 간 API 계약을 테스트로 검증합니다. 한쪽이 변경됐을 때 자동으로 감지합니다."
                },
                {
                    "title": "통합 브랜치 (Develop Branch)",
                    "content": "개별 기능 브랜치를 develop으로 통합하고 통합 테스트를 수행합니다. main에는 검증된 코드만 병합합니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "마지막에 한꺼번에 통합",
                    "bad_example": "개발 완료 직전 모든 기능을 한 번에 머지",
                    "good_example": "기능 완성될 때마다 develop 브랜치에 통합"
                },
                {
                    "mistake": "통합 테스트 없이 배포",
                    "bad_example": "로컬에서 각각 확인 후 바로 프로덕션 배포",
                    "good_example": "스테이징 환경에서 E2E 시나리오 검증 후 배포"
                }
            ],
            "one_line_tip": "\"Early integration, often integration\" — 통합은 일찍 시작할수록 고통이 줄어듭니다."
        },
        "default_dictionary": [
            {"term": "CI (Continuous Integration)", "definition": "코드 변경을 자동으로 빌드·테스트하는 지속적 통합 프로세스"},
            {"term": "E2E 테스트 (End-to-End Test)", "definition": "사용자 시나리오 전체 흐름을 처음부터 끝까지 검증하는 테스트"},
            {"term": "머지 충돌 (Merge Conflict)", "definition": "두 브랜치가 같은 코드 부분을 다르게 수정해 자동 병합이 불가능한 상태"},
            {"term": "스테이징 환경 (Staging)", "definition": "프로덕션과 동일한 설정으로 배포 전 최종 검증하는 테스트 환경"},
        ],
    },
    {
        "stage_sequence": 5,
        "sequence": 4,
        "name": "코드 리뷰 및 자체 검증",
        "toast_message": "코드 리뷰 및 자체 검증을 완료했습니다! ✨",
        "template_description": "작성된 코드를 팀원(또는 본인)이 읽어보며 결함·나쁜 패턴·누락을 발견하고 개선하는 문서입니다.",
        "goal": "작성된 코드를 팀원(또는 본인)이 읽어보며 결함·나쁜 패턴·누락을 발견하고 개선한다.",
        "entry_criteria": "Step 히스토리에 핵심 기능 구현과 통합에 대한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "코드 리뷰·피어 리뷰 활동",
            "코딩 컨벤션·품질 점검",
            "단위 테스트·개발자 자체 검증",
            "발견된 결함의 수정·개선",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch8 - Code Review",
        "default_mentoring": {
            "description": "코드 리뷰는 버그를 찾는 것만이 아닙니다. 팀 전체의 코드 품질을 높이고, 지식을 공유하며, 나쁜 패턴이 코드베이스에 퍼지는 것을 막는 중요한 활동입니다.",
            "recommended_methods": [
                {
                    "title": "PR 기반 코드 리뷰",
                    "content": "코드 변경은 Pull Request를 통해 최소 1명의 승인을 받도록 규칙을 설정합니다. 리뷰어는 로직·가독성·보안·테스트 커버리지 관점에서 점검합니다."
                },
                {
                    "title": "린터·정적 분석 도구 활용",
                    "content": "ESLint·Pylint·SonarQube 등을 CI에 통합해 코딩 컨벤션 위반·잠재 버그를 자동 감지합니다."
                },
                {
                    "title": "체크리스트 기반 자체 검증",
                    "content": "PR 제출 전 본인 코드를 리뷰어 입장에서 점검합니다. \"이 코드를 처음 보는 사람이 이해할 수 있는가?\"를 기준으로 확인하세요."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "너무 많은 코드를 한 PR에 올림",
                    "bad_example": "500줄 이상의 PR → 리뷰 포기",
                    "good_example": "200줄 이하로 PR을 작게 분리"
                },
                {
                    "mistake": "리뷰가 형식적으로만 진행",
                    "bad_example": "\"LGTM\" (Looks Good To Me) → 승인",
                    "good_example": "구체적 개선 제안 또는 질문 포함"
                }
            ],
            "one_line_tip": "리뷰 코멘트는 코드가 아닌 코드를 작성한 행동에 대한 것입니다. 친절하되 명확하게 작성하세요."
        },
        "default_dictionary": [
            {"term": "코드 리뷰 (Code Review)", "definition": "다른 개발자가 작성한 코드를 읽고 오류·개선점을 찾는 활동"},
            {"term": "린터 (Linter)", "definition": "코드 스타일·문법 오류를 자동으로 검사하는 정적 분석 도구"},
            {"term": "단위 테스트 (Unit Test)", "definition": "개별 함수·모듈이 예상대로 동작하는지 검증하는 테스트"},
            {"term": "LGTM (Looks Good To Me)", "definition": "코드 리뷰에서 변경사항을 승인한다는 의미의 약어"},
        ],
    },
    # ── Stage 6: 테스트 및 검증 ──────────────────────────────────────────
    {
        "stage_sequence": 6,
        "sequence": 1,
        "name": "테스트 계획 수립",
        "toast_message": "테스트 계획 수립을 완료했습니다! 📋",
        "template_description": "Stage 3 요구사항을 어떻게 검증할지 테스트 전략과 범위를 결정하는 문서입니다. 대상·범위, 유형, 시나리오, 데이터 준비, 환경·도구를 포함합니다.",
        "goal": "Stage 3 요구사항을 어떻게 검증할지 테스트 전략과 범위를 결정한다.",
        "entry_criteria": "Step 히스토리에 통합된 시스템과 요구사항 맥락이 존재한다.",
        "fulfillment_criteria": [
            "테스트 대상·범위 정의",
            "테스트 유형 선택 (기능/통합/성능/보안 등)",
            "테스트 시나리오·케이스 설계",
            "테스트 데이터·입력값 준비 (test database 생성·샘플 데이터셋)",
            "테스트 환경·도구 준비",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch9 - Test Planning",
        "default_mentoring": {
            "description": "테스트 없이 배포는 눈 감고 운전하는 것과 같습니다. 테스트 계획은 '무엇을', '어떻게', '어느 수준까지' 검증할 것인지를 팀이 합의하는 과정입니다.",
            "recommended_methods": [
                {
                    "title": "테스트 피라미드 전략",
                    "content": "단위 테스트(많이) → 통합 테스트(중간) → E2E 테스트(적게) 비율로 설계합니다. 하위 테스트일수록 빠르고 저렴합니다."
                },
                {
                    "title": "요구사항 기반 테스트 케이스 도출",
                    "content": "RTM을 참고해 각 요구사항마다 최소 1개의 테스트 케이스를 작성합니다. 해피 패스 + 엣지 케이스를 함께 설계합니다."
                },
                {
                    "title": "테스트 데이터 전략",
                    "content": "실제 데이터를 사용하지 않고 테스트 전용 데이터셋을 만듭니다. 테스트마다 데이터를 초기화하는 픽스처(Fixture)를 활용하세요."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "해피 패스만 테스트",
                    "bad_example": "정상 로그인만 테스트",
                    "good_example": "잘못된 비밀번호·계정 없음·잠긴 계정 등 실패 케이스도 포함"
                },
                {
                    "mistake": "테스트 없이 수동 클릭으로만 검증",
                    "bad_example": "배포 전 직접 화면 클릭으로 확인",
                    "good_example": "자동화 테스트로 회귀 방지"
                }
            ],
            "one_line_tip": "테스트 케이스는 요구사항의 거울입니다. 요구사항마다 \"이게 맞는지 어떻게 확인할까?\"를 물어보세요."
        },
        "default_dictionary": [
            {"term": "테스트 피라미드", "definition": "단위·통합·E2E 테스트의 이상적인 비율을 피라미드 형태로 나타낸 전략"},
            {"term": "해피 패스 (Happy Path)", "definition": "오류 없이 정상적으로 진행되는 주요 사용 흐름"},
            {"term": "엣지 케이스 (Edge Case)", "definition": "경계값·예외 상황·비정상 입력 등 특수한 조건에서의 동작"},
            {"term": "픽스처 (Fixture)", "definition": "테스트 실행 전 준비하고 실행 후 정리하는 테스트 전용 데이터·환경"},
        ],
    },
    {
        "stage_sequence": 6,
        "sequence": 2,
        "name": "테스트 수행",
        "toast_message": "테스트 수행을 완료했습니다! 🧪",
        "template_description": "수립한 계획에 따라 테스트를 실제로 실행하여 시스템 동작을 확인하는 문서입니다.",
        "goal": "수립한 계획에 따라 테스트를 실제로 실행하여 시스템 동작을 확인한다.",
        "entry_criteria": "Step 히스토리에 테스트 계획에 대한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "기능 테스트 수행",
            "통합·시나리오 테스트 수행",
            "비기능 테스트 수행 (성능·보안·사용성 등)",
            "테스트 결과 기록·수집",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch9 - Test Execution",
        "default_mentoring": {
            "description": "계획한 테스트를 실제로 실행하고 결과를 체계적으로 기록합니다. 테스트 결과는 단순한 통과/실패가 아니라, 시스템의 현재 상태를 보여주는 증거입니다.",
            "recommended_methods": [
                {
                    "title": "자동화 테스트 실행",
                    "content": "pytest·Jest·Cypress 등 도구로 테스트를 자동 실행합니다. CI 파이프라인에 통합하면 코드 변경마다 자동으로 검증됩니다."
                },
                {
                    "title": "탐색적 테스팅 (Exploratory Testing)",
                    "content": "스크립트 없이 실제 사용자처럼 자유롭게 시스템을 사용하며 예상치 못한 버그를 찾습니다. 자동화 테스트가 발견하지 못하는 UX 문제를 발굴하는 데 효과적입니다."
                },
                {
                    "title": "성능 테스트 도구 활용",
                    "content": "k6·Apache JMeter·Locust 등으로 부하 테스트를 수행합니다. 응답 시간·처리량·에러율을 측정합니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "테스트 결과를 기록하지 않음",
                    "bad_example": "\"테스트했는데 됩니다\"",
                    "good_example": "테스트 케이스별 실행 결과·스크린샷·로그 보존"
                },
                {
                    "mistake": "기능 테스트만 수행하고 비기능 테스트 생략",
                    "bad_example": "화면이 뜨면 OK",
                    "good_example": "성능(응답 시간)·보안(인젝션 시도)·사용성 테스트도 수행"
                }
            ],
            "one_line_tip": "발견한 버그는 즉시 이슈로 등록하세요. 기억에만 의존하면 반드시 누락됩니다."
        },
        "default_dictionary": [
            {"term": "회귀 테스트 (Regression Test)", "definition": "코드 변경 후 기존 기능이 여전히 정상 동작하는지 확인하는 테스트"},
            {"term": "탐색적 테스팅", "definition": "사전 스크립트 없이 직관과 경험으로 자유롭게 버그를 찾는 테스트 방식"},
            {"term": "부하 테스트 (Load Test)", "definition": "동시 사용자 증가 시 시스템 성능을 측정하는 테스트"},
            {"term": "테스트 커버리지 (Test Coverage)", "definition": "전체 코드 중 테스트가 실행된 비율"},
        ],
    },
    {
        "stage_sequence": 6,
        "sequence": 3,
        "name": "결과 분석 및 결함 기록",
        "toast_message": "결과 분석 및 결함 기록을 완료했습니다! 📝",
        "template_description": "테스트 중 발견한 결함을 구조화된 형태로 기록하고 원인·심각도를 정리하는 문서입니다.",
        "goal": "테스트 중 발견한 결함을 구조화된 형태로 기록하고 원인·심각도를 정리한다.",
        "entry_criteria": "Step 히스토리에 테스트 수행과 결과 맥락이 존재한다.",
        "fulfillment_criteria": [
            "결함 목록화·분류",
            "결함 재현 방법·원인 분석",
            "심각도·우선순위 부여",
            "결함 수정·재테스트 계획",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch9 - Defect Analysis",
        "default_mentoring": {
            "description": "결함을 발견하면 즉시 구조화된 형태로 기록해야 합니다. \"이상하게 됨\"은 버그 보고서가 아닙니다. 재현 가능한 버그 보고서는 수정 시간을 절반으로 줄입니다.",
            "recommended_methods": [
                {
                    "title": "버그 리포트 표준 양식",
                    "content": "제목·환경·재현 단계·예상 동작·실제 동작·스크린샷으로 구성합니다. GitHub Issues·Jira의 버그 템플릿을 활용하세요."
                },
                {
                    "title": "심각도 분류 (Severity Level)",
                    "content": "Critical(서비스 불가)·Major(핵심 기능 장애)·Minor(불편하지만 사용 가능)·Trivial(미미한 문제)로 분류해 수정 우선순위를 결정합니다."
                },
                {
                    "title": "근본 원인 분석 (RCA)",
                    "content": "버그의 증상이 아닌 원인을 찾습니다. 같은 근본 원인으로 인한 버그가 여러 개라면 한 번에 해결할 수 있습니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "재현 방법 없이 버그 보고",
                    "bad_example": "\"버튼이 가끔 안 됨\"",
                    "good_example": "\"1. 로그인 → 2. 상품 클릭 → 3. 장바구니 추가 → 4. 뒤로가기 → 5. 재추가 시 404 에러\""
                },
                {
                    "mistake": "모든 버그를 동등하게 처리",
                    "bad_example": "우선순위 없이 발견 순서대로 수정",
                    "good_example": "Critical → Major → Minor 순서로 수정"
                }
            ],
            "one_line_tip": "좋은 버그 보고서는 개발자가 직접 재현할 수 있어야 합니다. 재현이 안 되면 수정도 없습니다."
        },
        "default_dictionary": [
            {"term": "결함 (Defect/Bug)", "definition": "소프트웨어가 명세된 요구사항과 다르게 동작하는 문제"},
            {"term": "심각도 (Severity)", "definition": "결함이 시스템 기능에 미치는 영향의 정도"},
            {"term": "우선순위 (Priority)", "definition": "결함을 수정해야 하는 시급성"},
            {"term": "RCA (Root Cause Analysis)", "definition": "문제의 근본 원인을 체계적으로 분석하는 방법"},
        ],
    },
    {
        "stage_sequence": 6,
        "sequence": 4,
        "name": "수용 테스트/최종 검토",
        "toast_message": "수용 테스트/최종 검토를 완료했습니다! 🎉",
        "template_description": "초기 문제/기회와 요구사항이 실제로 해결되었는지, 프로젝트 목표 달성 여부를 판단하는 문서입니다.",
        "goal": "초기 문제/기회와 요구사항이 실제로 해결되었는지, 프로젝트 목표 달성 여부를 판단한다.",
        "entry_criteria": "Step 히스토리에 결함 기록과 주요 결함 처리에 대한 맥락이 존재한다.",
        "fulfillment_criteria": [
            "Stage 1 문제/기회 해결 여부 점검",
            "Stage 3 핵심 요구사항 충족 여부 점검",
            "사용자 관점의 수용 테스트·시연",
            "프로젝트 종료 판단·회고·향후 방향",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch9 - Acceptance & Final Review",
        "default_mentoring": {
            "description": "드디어 마지막 관문입니다. 처음에 정의한 문제가 실제로 해결됐는지, 사용자가 만족하는지를 확인하는 시간입니다. 기술적 완성도보다 사용자 가치 달성 여부가 핵심 판단 기준입니다.",
            "recommended_methods": [
                {
                    "title": "사용자 수용 테스트 (UAT)",
                    "content": "실제 사용자(또는 대표 사용자)에게 핵심 시나리오를 직접 수행하게 합니다. 개발팀이 예상하지 못한 UX 문제가 드러납니다."
                },
                {
                    "title": "프로젝트 회고 (Retrospective)",
                    "content": "Keep(잘 된 것)·Problem(아쉬운 것)·Try(다음에 시도할 것) 형식으로 팀이 함께 회고합니다. 다음 프로젝트에서 같은 실수를 반복하지 않는 데 도움이 됩니다."
                },
                {
                    "title": "릴리즈 노트 작성",
                    "content": "구현된 기능·수정된 버그·알려진 이슈를 정리한 문서를 작성합니다. 이해관계자에게 프로젝트 결과를 공식적으로 전달합니다."
                }
            ],
            "common_mistakes": [
                {
                    "mistake": "개발자만의 데모로 수용 테스트 대체",
                    "bad_example": "개발팀이 직접 시연하며 \"잘 됩니다\" 확인",
                    "good_example": "사용자가 직접 조작하며 목표 태스크 완료 여부 확인"
                },
                {
                    "mistake": "회고 없이 프로젝트 종료",
                    "bad_example": "배포 완료 → 프로젝트 종료",
                    "good_example": "팀 회고 → 개선사항 문서화 → 향후 유지보수 계획 수립"
                }
            ],
            "one_line_tip": "Stage 1에서 정의한 문제가 해결됐는가? 그것이 이 프로젝트의 진정한 완료 기준입니다."
        },
        "default_dictionary": [
            {"term": "UAT (User Acceptance Testing)", "definition": "실제 사용자가 시스템이 요구사항을 충족하는지 직접 검증하는 최종 테스트"},
            {"term": "회고 (Retrospective)", "definition": "프로젝트나 스프린트를 마친 후 팀이 개선점을 논의하는 성찰 활동"},
            {"term": "릴리즈 노트 (Release Notes)", "definition": "새 버전에 포함된 기능·수정·알려진 이슈를 정리한 공식 문서"},
            {"term": "Done의 정의 (Definition of Done)", "definition": "작업이 완료됐다고 판단하는 팀 내 합의된 기준"},
        ],
    },
]


def run(db: Session) -> None:
    """Required Step 시드 데이터 삽입. stage_sequence로 Stage를 조회한 뒤 upsert한다."""
    stage_map: dict[int, object] = {s.sequence: s.id for s in db.query(Stage).all()}

    rows = []
    for item in REQUIRED_STEP_DATA:
        seq = item["stage_sequence"]
        if seq not in stage_map:
            raise ValueError(
                f"Stage sequence {seq} 를 찾을 수 없습니다. Stage 시드를 먼저 실행하세요."
            )
        rows.append(
            {
                "stage_id": stage_map[seq],
                "name": item["name"],
                "sequence": item["sequence"],
                "toast_message": item["toast_message"],
                "template_description": item["template_description"],
                "goal": item["goal"],
                "entry_criteria": item["entry_criteria"],
                "fulfillment_criteria": item["fulfillment_criteria"],
                "minimum_fulfillment_count": item["minimum_fulfillment_count"],
                "doj_reference": item["doj_reference"],
                "default_mentoring": item["default_mentoring"],
                "default_dictionary": item["default_dictionary"],
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
                "goal": insert(RequiredStep).excluded.goal,
                "entry_criteria": insert(RequiredStep).excluded.entry_criteria,
                "fulfillment_criteria": insert(RequiredStep).excluded.fulfillment_criteria,
                "minimum_fulfillment_count": insert(RequiredStep).excluded.minimum_fulfillment_count,
                "doj_reference": insert(RequiredStep).excluded.doj_reference,
                "default_mentoring": insert(RequiredStep).excluded.default_mentoring,
                "default_dictionary": insert(RequiredStep).excluded.default_dictionary,
            },
        )
    )
    db.execute(stmt)
