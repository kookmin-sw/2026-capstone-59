from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.core.models.required_step import RequiredStep
from app.core.models.stage import Stage

# DOJ SDLC 기반 Required Step 시드 데이터 (24개 = 4 per stage × 6 stages)
# - 4개 측면 R: 21개 / 5개 측면 R: 3개 (4-R1, 4-R4, 6-R1)
# - 모든 R 공통 충족 기준: minimum_fulfillment_count = 2
REQUIRED_STEP_DATA: list[dict] = [
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d195980f48683e5405f780dda?source=copy_link",
        "default_mentoring": {
            "description": "프로젝트의 출발점이에요. 여기서는 프로젝트가 풀려는 문제 또는 포착한 기회를 또렷하게 정의해요. 중요한 건 '이런 서비스가 있으면 좋겠다'가 아니라 무엇이 문제이고, 누가 어떤 상황에서 불편을 겪으며, 왜 지금 중요한지를 분명히 하는 것이에요. 여기서 선명해진 문제가 이후 사용자 파악·컨셉 정의·요구사항 도출 내내 기준선이 되어요.",
            "perspectives": [
                "해결하려는 문제 또는 기회를 한두 문장으로 설명할 수 있나요?",
                "이 문제가 왜 중요한지 설명할 수 있나요?",
                "이 문제가 주로 어떤 상황이나 맥락에서 발생하는지 알고 있나요?",
                "현재 사람들이 사용하는 방식이나 기존 대안에는 어떤 한계가 있나요?",
            ],
            "goals": [
                "문제·기회를 구체적으로 설명할 수 있다.",
                "문제의 중요도 또는 해결 가치를 말할 수 있다.",
                "문제의 발생 배경이나 상황을 설명할 수 있다.",
                "기존 대안의 한계 또는 미해결 지점을 정리할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "문제를 너무 넓게 쓰기 — 대상과 상황이 드러나게 좁혀야 해요",
                    "bad_example": "프로젝트 관리가 어렵다.",
                    "good_example": "프로젝트 경험이 없는 대학생 팀은 초기 기획 단계에서 무엇부터 해야 할지 몰라 많은 시간을 낭비한다.",
                },
                {
                    "mistake": "해결책을 먼저 정해두기 — '왜 필요한가'를 먼저 분명히 해야 해요",
                    "bad_example": "AI 챗봇으로 도와주는 앱을 만들고 싶다.",
                    "good_example": "사용자가 기획 과정에서 가장 자주 막히는 지점을 먼저 찾고, 그 지점에 필요한 도움이 무엇인지 역으로 정의한다.",
                },
                {
                    "mistake": "문제의 중요도를 설명하지 않기 — 왜 해결할 가치가 있는지도 같이 써야 해요",
                    "bad_example": "많은 사람이 이 불편을 겪고 있다.",
                    "good_example": "이 불편 때문에 팀이 평균 2주를 낭비하고, 결국 절반 이상이 프로젝트를 포기한다.",
                },
                {
                    "mistake": "현재 방식의 한계를 놓치기 — 이미 존재하는 대안을 먼저 봐야 해요",
                    "bad_example": "이 문제를 해결하는 서비스가 없다.",
                    "good_example": "블로그·유튜브 같은 자료는 있지만, 흩어진 정보를 자기 프로젝트에 맞게 재구성하는 과정에서 대부분 막힌다.",
                },
            ],
            "one_line_tip": "해결책을 서두르기보다, 문제 자체를 선명하게 설명하는 것에 집중해보세요.",
        },
        "default_dictionary": [
            {
                "term": "문제 정의 (Problem Statement)",
                "definition": "해결하려는 상황을 누가·언제·어떤 맥락에서 겪는지가 드러나게 한두 문장으로 정리한 서술이에요.",
            },
            {
                "term": "기회 (Opportunity)",
                "definition": "아직 불편이 아닌 일이라도, 더 나아질 여지가 보이는 지점을 포착한 아이디어의 출발점이에요.",
            },
            {
                "term": "기존 대안 (Existing Alternative)",
                "definition": "사람들이 이 문제를 지금 어떻게 해결하고 있는지, 사용 중인 서비스·도구·우회 방식 모두를 가리키는 말이에요.",
            },
            {
                "term": "임팩트 (Impact)",
                "definition": "문제를 풀었을 때 누구에게 어떤 변화가 생기는지를 말해주는 '해결할 가치'의 근거예요.",
            },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d19598039bcdbea8be98256e6?source=copy_link",
        "default_mentoring": {
            "description": "Stage 1의 방향 전환점이에요. '무엇'에서 '누구'로 초점이 돌아가며, 문제로 불편을 겪는 구체적인 한 명을 그려봐요. 막연한 '모두'가 아니라 한 사람의 상황·습관·맥락이 또렷해질 때, 컨셉 정의와 기능 설계 내내 '이 사람이라면 어떻게 느낄까'로 결정을 이어갈 수 있어요.",
            "perspectives": [
                "1차 타겟 사용자의 연령·역할·상황을 한두 줄로 설명할 수 있나요?",
                "그 사용자가 지금 어떤 행동이나 습관을 반복하는지 알고 있나요?",
                "대표 사용자 한 명을 페르소나 또는 시나리오로 그려두었나요?",
                "인터뷰·관찰·설문 등으로 사용자의 이야기를 직접 들어봤나요?",
            ],
            "goals": [
                "1차 타겟 사용자의 특성을 또렷하게 설명할 수 있다.",
                "사용자의 현재 행동·습관·맥락을 정리할 수 있다.",
                "대표 페르소나 또는 시나리오 한 개를 그려낼 수 있다.",
                "사용자에게서 직접 얻은 인사이트를 정리할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "모두를 대상으로 삼기 — 누구의 문제인지 좁혀야 방향이 선명해져요",
                    "bad_example": "모든 대학생이 우리 서비스를 쓴다.",
                    "good_example": "개발 경험 1년 미만, 3~5인 팀으로 졸업작품을 준비하는 공대 3~4학년.",
                },
                {
                    "mistake": "페르소나를 추측만으로 채우기 — 한 명이라도 실제로 만나 들어봐야 해요",
                    "bad_example": "아마 바쁘고 시간이 없을 것이다.",
                    "good_example": "실제 2명에게 물어본 결과, 수업 후 평일 저녁에 팀 회의를 하며 주말엔 각자 작업한다고 답했다.",
                },
                {
                    "mistake": "인구 통계만 적고 끝내기 — 행동과 감정이 보여야 페르소나예요",
                    "bad_example": "23세 여자 대학생.",
                    "good_example": "23세 공대생 민수. 회의에선 참여적이지만, 다음 주 할 일을 결정하지 못한 채 회의가 끝나 답답함을 느낀다.",
                },
            ],
            "one_line_tip": "'모두'가 아닌 '한 명'을 또렷하게 그려두면 이후 결정이 훨씬 빨라져요.",
        },
        "default_dictionary": [
            {
                "term": "타겟 사용자 (Target User)",
                "definition": "우리 서비스가 가장 먼저 도와줄, 문제를 가장 크게 겪는 구체적인 사용자군이에요.",
            },
            {
                "term": "페르소나 (Persona)",
                "definition": "대표 사용자 한 명을 가상 인물로 그린 것으로, 이름·상황·고민까지 담아 결정의 기준점 역할을 해요.",
            },
            {
                "term": "사용자 시나리오 (User Scenario)",
                "definition": "페르소나가 실제 상황에서 어떻게 행동하고 느끼는지를 짧은 이야기로 풀어놓은 장면이에요.",
            },
            {
                "term": "사용자 인터뷰 (User Interview)",
                "definition": "잠재 사용자와 짧은 대화를 나누며 행동·습관·불편을 듣는 도출 기법이에요. 2~3명만 만나도 큰 힌트가 나와요.",
            },
            {
                "term": "인사이트 (Insight)",
                "definition": "관찰·대화에서 발견한 '의외의 사실'이나 '결정에 영향을 줄 만한 포인트'를 짧게 정리한 메모예요.",
            },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d1959801d9553dc77b604d587?source=copy_link",
        "default_mentoring": {
            "description": "아이디어를 컨셉으로 옮기는 자리예요. 문제와 사용자를 확인했다면, 둘을 이어줄 '해결 방식'을 한 단락으로 정리할 차례예요. 중요한 건 기능 나열이 아니라 '비슷한 서비스와 뭐가 다른가'를 한 줄로 설명할 수 있는 수준이에요. 여기서 확정된 컨셉이 실현 가능성 검토와 Stage 3의 요구사항 도출에서 내내 기준선으로 쓰여요.",
            "perspectives": [
                "해결 방식을 한 문장으로 설명할 수 있나요?",
                "유사·경쟁 서비스를 3~5개 정도 살펴봤나요?",
                "경쟁 서비스와 비교해 우리만의 차별점·핵심 가치를 말할 수 있나요?",
                "제공할 주요 기능의 큰 그림을 그릴 수 있나요?",
            ],
            "goals": [
                "해결 접근 방식을 한 단락으로 서술할 수 있다.",
                "유사·경쟁 서비스를 비교해 정리할 수 있다.",
                "경쟁 대비 차별점 또는 핵심 가치를 제시할 수 있다.",
                "주요 기능의 큰 그림을 설명할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "차별점을 막연하게 쓰기 — 무엇이 다른지 구체적으로 대조해야 해요",
                    "bad_example": "기존 앱보다 더 편리한 서비스.",
                    "good_example": "기존 앱은 흩어진 정보를 직접 찾아야 하지만, 우리는 필요한 순서대로 연결된 안내를 제공한다.",
                },
                {
                    "mistake": "기능부터 잔뜩 나열하기 — 메시지부터 또렷해야 기능이 붙어요",
                    "bad_example": "채팅·알림·통계·공유·결제 기능을 모두 넣는다.",
                    "good_example": "처음에는 '기획 단계 안내' 하나에 집중하고, 사용자가 원하면 기능을 점진적으로 붙인다.",
                },
                {
                    "mistake": "경쟁사 조사 없이 '우리 아이디어는 새롭다'고 단정하기",
                    "bad_example": "비슷한 서비스는 찾아보지 않았지만 우리 아이디어는 새롭다.",
                    "good_example": "비슷한 서비스 3개를 써본 뒤, 그중 어떤 틈이 비어 있는지를 바탕으로 우리 컨셉을 정의한다.",
                },
            ],
            "one_line_tip": "'우리만의 한 줄'이 또렷해질 때까지, 기능 수보다 메시지부터 다듬어보세요.",
        },
        "default_dictionary": [
            {
                "term": "가치 제안 (Value Proposition)",
                "definition": "'우리가 누구에게 어떤 가치를 어떻게 제공하는가'를 한 문장으로 정리한 서비스의 핵심 약속이에요.",
            },
            {
                "term": "차별점 (Differentiator)",
                "definition": "비슷한 서비스와 비교했을 때 우리만이 잘하거나 다르게 하는 한두 가지를 뜻해요.",
            },
            {
                "term": "경쟁 분석 (Competitive Analysis)",
                "definition": "유사한 문제를 푸는 서비스를 체계적으로 비교해 각자의 강점과 빈틈을 정리하는 작업이에요.",
            },
            {
                "term": "MVP (Minimum Viable Product)",
                "definition": "최소한의 기능만 담아 '이 컨셉이 통하는가'를 빠르게 확인할 수 있게 만든 첫 버전이에요.",
            },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d1959808c86bcffa8df20f288?source=copy_link",
        "default_mentoring": {
            "description": "Stage 1의 마무리 지점이에요. '좋은 아이디어인가'보다 '지금 만들 수 있는가'를 판단하는 단계이고, 주어진 기간·인원·기술 수준 안에서 컨셉이 현실화될 수 있는지와 주요 리스크가 무엇인지를 미리 알아두는 게 목적이에요. 모든 불확실성을 없앨 필요는 없고, '알고 있는 상태'로 다음 단계들을 계속 진행해나가면 어느 순간 좌측 Stage Navigator에서 다음 Stage가 자연스럽게 열려 있을 거예요.",
            "perspectives": [
                "핵심 기능을 기술적으로 만들 수 있을지 판단했나요?",
                "주어진 기간·자원·인원·비용 안에서 가능할지 살펴봤나요?",
                "가장 불확실한 부분을 작게 검증할 방법(프로토타입·작은 실험)을 떠올렸나요?",
                "주요 리스크와 제약사항을 미리 적어두었나요?",
            ],
            "goals": [
                "기술적 실현 가능성을 판단할 수 있다.",
                "기간·자원·인원·비용 관점의 적합성을 설명할 수 있다.",
                "프로토타입·PoC 등 작은 검증 방법을 계획할 수 있다.",
                "주요 리스크·제약사항을 정리할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "할 수 있다고 단언하기 — 모르는 부분은 모르는 채로 적어두는 게 정직해요",
                    "bad_example": "어차피 어떻게든 되니까 구현은 문제없다.",
                    "good_example": "AI 연동 품질은 아직 불확실하므로, 일주일짜리 작은 실험으로 먼저 확인한다.",
                },
                {
                    "mistake": "리스크를 전부 해결하려 들기 — 보이게 두는 것만으로도 큰 진전이에요",
                    "bad_example": "모든 리스크를 지금 다 없애고 시작한다.",
                    "good_example": "가장 크게 느껴지는 두세 개만 완화 방안을 적고, 나머지는 '알아두기'로 남긴다.",
                },
                {
                    "mistake": "기술 가능성만 보고 자원·시간은 놓치기",
                    "bad_example": "기술적으로 가능하니 하자.",
                    "good_example": "기술적으로는 가능하지만 3인 팀·2개월 기준에선 범위를 절반으로 줄여야 현실적이다.",
                },
            ],
            "one_line_tip": "모르는 건 '모르는 채로 적어두기'만 해도 실현 가능성 검토는 충분해요.",
        },
        "default_dictionary": [
            {
                "term": "실현 가능성 (Feasibility)",
                "definition": "주어진 기간·자원·기술 수준 안에서 이 컨셉을 실제로 만들 수 있는지를 판단하는 관점이에요.",
            },
            {
                "term": "프로토타입 (Prototype)",
                "definition": "최종 제품이 아닌 '핵심 아이디어를 빠르게 보여주는 임시 모형'이에요. 종이 스케치·클릭 가능한 화면 모두 포함돼요.",
            },
            {
                "term": "PoC (Proof of Concept)",
                "definition": "'이 방식이 실제로 동작하는가'를 확인하기 위해 작은 범위에서 돌려보는 검증 실험이에요.",
            },
            {
                "term": "리스크 (Risk)",
                "definition": "프로젝트 진행을 방해하거나 지연시킬 수 있는 '가능성 있는 문제'를 미리 식별해둔 항목이에요.",
            },
            {
                "term": "제약사항 (Constraint)",
                "definition": "기간·예산·기술·정책처럼 바꿀 수 없는 조건을 뜻해요. 설계·구현 내내 기준선 역할을 해요.",
            },
        ],
    },
    {
        "stage_sequence": 2,
        "sequence": 1,
        "name": "일정 계획 수립",
        "toast_message": "일정 계획 수립을 완료했습니다! 📅",
        "template_description": "프로젝트 전체 기간을 Stage/마일스톤 단위로 배분하는 일정 뼈대를 정의하는 문서입니다. 마일스톤, 공수 추정, 일정 도구를 포함합니다.",
        "goal": "프로젝트 전체 기간을 Stage/마일스톤 단위로 배분하는 일정 뼈대를 만든다.",
        "entry_criteria": 'Step 히스토리에 "무엇을 얼마나 만들 것인지"에 대한 컨셉·실현 가능성 맥락이 존재한다.',
        "fulfillment_criteria": [
            "전체 일정을 Stage/구간으로 분할",
            "주요 마일스톤 또는 데드라인 설정",
            "Step/작업 단위의 공수·난이도 추정",
            "일정 관리 방식·도구 선정",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch5 - Schedule Planning",
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d195980178a6de61e5676f5e3?source=copy_link",
        "default_mentoring": {
            "description": "Stage 2의 첫 걸음이에요. 정확한 일정표가 아니라 '틀'을 잡는 단계이고, 실제 개발은 거의 반드시 흔들리기 때문에 완벽을 노리기보다 큰 덩어리와 마일스톤을 뚜렷하게 두는 게 목적이에요. 여기서 잡은 시간 축이 Stage 2 전체에서 '어떻게 일할 것인가'의 기본 뼈대가 되어요.",
            "perspectives": [
                "프로젝트 전체 기간을 구간 단위로 나눠봤나요?",
                "주요 마일스톤 또는 데드라인을 정해두었나요?",
                "작업 단위의 공수나 난이도를 가늠해봤나요?",
                "일정 관리 방식·도구를 정했나요?",
            ],
            "goals": [
                "전체 일정을 구간으로 분할할 수 있다.",
                "주요 마일스톤 또는 데드라인을 설정할 수 있다.",
                "작업 단위의 공수·난이도를 가늠할 수 있다.",
                "일정 관리 방식·도구를 선정할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "여유 없이 빡빡하게 잡기 — 버퍼를 두지 않으면 한 번 밀리는 순간 전체가 무너져요",
                    "bad_example": "12주를 구간당 2주씩 딱 맞춘다.",
                    "good_example": "각 구간 예상치의 70~80%만 배정하고, 나머지는 버퍼로 남긴다.",
                },
                {
                    "mistake": "마일스톤 없이 '끝날 때까지'만 잡기 — 중간 점검이 없으면 방향이 흐려져요",
                    "bad_example": "개발이 끝나면 발표를 한다.",
                    "good_example": "중반과 후반에 중간 데모를 두어 팀과 이해관계자가 진행 상황을 함께 확인한다.",
                },
                {
                    "mistake": "공수를 '느낌'으로만 추정 — 최소한의 근거를 두면 조정이 쉬워져요",
                    "bad_example": "이 기능은 하루면 끝난다.",
                    "good_example": "비슷한 기능을 해본 팀원의 경험에 따라 2~3일을 배정하고, 완료 후 실제 공수를 기록한다.",
                },
            ],
            "one_line_tip": "완벽한 일정보다, 흔들려도 돌아올 수 있는 '기준점' 두세 개가 더 중요해요.",
        },
        "default_dictionary": [
            {
                "term": "마일스톤 (Milestone)",
                "definition": "프로젝트 진행 중 '중요한 지점'을 표시하는 기준점이에요. 중간 데모, 특정 기능 완성 같은 형태로 설정돼요.",
            },
            {
                "term": "데드라인 (Deadline)",
                "definition": "꼭 지켜야 하는 마감 시점을 뜻해요. 외부 발표나 제출처럼 바꿀 수 없는 날짜가 대표적이에요.",
            },
            {
                "term": "버퍼 (Buffer)",
                "definition": "예상치 못한 지연에 대비해 일정에 남겨두는 여유 기간이에요. 보통 전체의 20~30%를 권장해요.",
            },
            {
                "term": "공수 (Effort)",
                "definition": "특정 작업을 끝내기 위해 필요한 시간과 노력의 양을 말해요. 일·시간 단위로 추정해요.",
            },
            {
                "term": "스프린트 (Sprint)",
                "definition": "1~4주 단위로 목표를 정하고 짧게 끊어서 진행하는 작업 구간이에요. 주기마다 점검과 조정이 일어나요.",
            },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d195980f08d36cfda6680c439?source=copy_link",
        "default_mentoring": {
            "description": "사람 축을 잡는 자리예요. 팀원 각자 어디까지가 본인 일인지 선을 긋는 단계이고, 선이 흐리면 협업 후반에 반드시 갈등이 생기기 때문에 지금 명시적으로 정해두는 것이 중요해요. 혼자 하는 프로젝트여도 본인이 쓰는 여러 역할(기획·개발·테스트)을 나눠 적어두면 일정 관리와 의사결정이 훨씬 수월해져요.",
            "perspectives": [
                "팀원별 주 담당 영역 또는 역할을 정했나요?",
                "역할 간 경계와 책임 범위를 명확히 했나요?",
                "결정·리뷰가 필요한 순간 누구에게 묻는지 정해두었나요?",
                "협업·커뮤니케이션 규칙을 합의했나요?",
            ],
            "goals": [
                "팀원별 담당 영역·역할을 정의할 수 있다.",
                "역할 간 경계와 책임 범위를 설명할 수 있다.",
                "의사결정·리뷰 주체를 정할 수 있다.",
                "협업·커뮤니케이션 규칙을 수립할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "'같이 하면 되지'라고 두루뭉술하게 두기 — 모두의 일은 아무의 일도 아니게 돼요",
                    "bad_example": "프론트는 같이 맡기로 했다.",
                    "good_example": "A가 화면 레이아웃·CSS, B가 상태 관리·API 호출로 경계를 그었다.",
                },
                {
                    "mistake": "의사결정 담당자 없이 모든 걸 합의로만 가기 — 결정이 지연돼 속도가 느려져요",
                    "bad_example": "모든 결정을 팀 전체 회의에서만 한다.",
                    "good_example": "설계는 B, 기능 추가는 A, 배포는 C가 최종 결정 후 팀에 공유한다.",
                },
                {
                    "mistake": "협업 규칙을 말로만 정하고 문서화하지 않기",
                    "bad_example": "대충 얘기했으니 다들 알 거다.",
                    "good_example": "회의 요일·시간, 기록 위치, 이슈 관리 방식을 한 장 문서로 남긴다.",
                },
            ],
            "one_line_tip": "'누가·무엇을·어디까지' 한 줄로 적혀 있으면 협업의 절반은 끝나요.",
        },
        "default_dictionary": [
            {
                "term": "담당 영역 (Responsibility)",
                "definition": "한 사람이 주도적으로 맡아 처리하는 작업 범위예요. 프론트·백엔드·디자인처럼 큰 덩어리로 나눠요.",
            },
            {
                "term": "의사결정권자 (Decision Owner)",
                "definition": "특정 영역의 최종 결정을 내리는 사람이에요. 협의는 함께 하되 결정은 한 명이 내리면 지연이 줄어요.",
            },
            {
                "term": "커뮤니케이션 규칙 (Communication Rule)",
                "definition": "팀이 어떻게 회의하고 기록하고 소통할지에 대한 약속이에요. 초반에 정해두면 후반에 갈등이 줄어요.",
            },
        ],
    },
    {
        "stage_sequence": 2,
        "sequence": 3,
        "name": "위험 식별",
        "toast_message": "위험 식별을 완료했습니다! ⚠️",
        "template_description": "프로젝트 진행을 방해할 수 있는 주요 리스크를 미리 식별하고 대응 방향을 정하는 문서입니다.",
        "goal": "프로젝트 진행을 방해할 수 있는 주요 리스크를 미리 식별하고 대응 방향을 정한다.",
        "entry_criteria": 'Step 히스토리에 일정·역할·기술 선택 등 "깨질 수 있는 계획"이 존재한다.',
        "fulfillment_criteria": [
            "기술 리스크 식별 (난이도·학습 곡선 등)",
            "일정 리스크 식별 (딜레이 요인·병목)",
            "팀 리스크 식별 (이탈·역량·커뮤니케이션)",
            "각 리스크별 대응·완화 방안",
        ],
        "minimum_fulfillment_count": 2,
        "doj_reference": "DOJ SDLC Ch5 - Risk Management",
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d19598084981de6d981dc7836?source=copy_link",
        "default_mentoring": {
            "description": "계획의 점검 지점이에요. 일정과 역할처럼 '깨질 수 있는 계획' 뒤에 오는 자연스러운 자리이고, 리스크는 '없애는 것'이 아니라 '보이게 두는 것'이 목표예요. 여기서 적어둔 리스크가 Stage 2를 마무리하며 '무엇이 흔들릴 수 있는지' 팀이 공유해두는 자산이 되어요. 전부 해결하려 하지 말고 지금 눈에 보이는 것부터 적어봐요.",
            "perspectives": [
                "기술 난이도·학습 곡선 관점의 리스크를 떠올려봤나요?",
                "일정이 밀릴 수 있는 요인·병목을 식별했나요?",
                "팀원의 이탈·역량·가용 시간 관점의 리스크를 적어뒀나요?",
                "각 리스크별 대응·완화 방안을 한 줄이라도 남겼나요?",
            ],
            "goals": [
                "기술 리스크를 식별할 수 있다.",
                "일정 리스크를 식별할 수 있다.",
                "팀 리스크를 식별할 수 있다.",
                "리스크별 대응·완화 방안을 정리할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "리스크를 막연히 '시간이 부족하다'로만 적기 — 언제·무엇이 부족한지 구체화해야 대응이 가능해요",
                    "bad_example": "일정이 빡빡할 것 같다.",
                    "good_example": "중반 구간이 시험 기간과 겹쳐 2주간 가용 시간이 절반으로 줄어든다.",
                },
                {
                    "mistake": "발견한 리스크에 대응책을 안 적기 — 한 줄만 적어도 대비가 가능해져요",
                    "bad_example": "AI 연동이 어렵다.",
                    "good_example": "AI 연동이 어려움 → 첫 주에 최소 예제로 한 번 돌려보고 결과를 확인한다.",
                },
                {
                    "mistake": "팀 내부 리스크를 빼기 — 사람 문제가 가장 자주 프로젝트를 흔들어요",
                    "bad_example": "팀 관련 리스크는 없다.",
                    "good_example": "한 명이 중간에 장기 휴가가 있어 그 구간의 작업을 앞당겨 분산한다.",
                },
            ],
            "one_line_tip": "리스크를 '발견'만 해도 절반은 해결돼요. 대응책은 한 줄이면 충분해요.",
        },
        "default_dictionary": [
            {
                "term": "리스크 (Risk)",
                "definition": "일정·품질·팀 운영을 방해할 수 있는 '가능성 있는 문제'예요. 식별 자체만으로도 대응 여력이 생겨요.",
            },
            {
                "term": "병목 (Bottleneck)",
                "definition": "전체 진행 속도를 떨어뜨리는 좁은 구간이에요. 사람·기술·승인 프로세스 등이 될 수 있어요.",
            },
            {
                "term": "완화 방안 (Mitigation)",
                "definition": "리스크가 실제로 일어나지 않도록 혹은 일어나도 영향을 줄이도록 미리 준비해두는 대응책이에요.",
            },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d195980b4bb89c31eb5fddf25?source=copy_link",
        "default_mentoring": {
            "description": "Stage 2의 마무리 지점이에요. 언어·프레임워크·협업 도구를 확정해 팀 모두가 같은 출발선에 서게 하는 단계이고, 정답 찾기가 아니라 '우리는 이걸로 간다'는 합의가 핵심이에요. 여기서 내린 결정이 Stage 5의 '개발 환경 구축'에서 실제 세팅으로 이어지니, 지금은 큰 줄기만 정해도 충분해요.",
            "perspectives": [
                "개발 언어·프레임워크를 선정했나요?",
                "형상관리와 브랜치 전략(Git 등)을 정했나요?",
                "협업·이슈 관리 도구를 정했나요?",
                "개발·배포 환경 구성 방향을 잡았나요?",
            ],
            "goals": [
                "개발 언어·프레임워크를 선정할 수 있다.",
                "형상관리·브랜치 전략을 수립할 수 있다.",
                "협업·이슈 관리 도구를 선정할 수 있다.",
                "개발·배포 환경 구성 방향을 설명할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "유행하는 기술을 이유 없이 고르기 — 팀 경험과 레퍼런스 양이 훨씬 중요해요",
                    "bad_example": "요즘 많이 쓰니까 Rust로 간다.",
                    "good_example": "팀의 기존 경험과 레퍼런스가 많은 Node.js로 간다.",
                },
                {
                    "mistake": "협업 도구가 흩어져 정보가 파편화되기 — 한 곳에 모이게 설계해야 해요",
                    "bad_example": "회의는 디스코드, 이슈는 노션, 일정은 카톡에 흩어짐.",
                    "good_example": "문서는 노션, 이슈·스프린트는 깃허브 프로젝트로 단일화.",
                },
                {
                    "mistake": "결정을 말로만 남기고 문서화하지 않기",
                    "bad_example": "회의 때 정한 대로 각자 기억해서 쓴다.",
                    "good_example": "선택한 스택·이유·버전 범위를 README 또는 위키에 한 페이지로 정리한다.",
                },
            ],
            "one_line_tip": "'최고의 기술'이 아니라 '팀이 지금 같이 쓸 수 있는 기술'을 고르는 단계예요.",
        },
        "default_dictionary": [
            {
                "term": "프레임워크 (Framework)",
                "definition": "자주 쓰는 기능을 미리 묶어 빠르게 개발할 수 있게 해주는 도구 모음이에요. 예: React, FastAPI.",
            },
            {
                "term": "형상관리 (Version Control)",
                "definition": "코드 변경 이력을 기록하고 이전 상태로 되돌릴 수 있게 해주는 체계예요. 대표적으로 Git이 있어요.",
            },
            {
                "term": "브랜치 전략 (Branching Strategy)",
                "definition": "Git에서 기능·버그·실험을 어떻게 나눠서 작업할지에 대한 팀 규칙이에요. 협업 충돌을 줄여줘요.",
            },
            {
                "term": "이슈 트래커 (Issue Tracker)",
                "definition": "할 일과 버그를 리스트로 관리하는 도구예요. 깃허브 Issues, Jira 등이 대표적이에요.",
            },
        ],
    },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d195980688afbd333dc4ae183?source=copy_link",
        "default_mentoring": {
            "description": "요구사항의 출발점이에요. 시스템이 해야 할 일을 사용자·팀 관점에서 자유롭게 펼쳐내는 단계이고, 지금은 정리가 아니라 '수집'이라 중복되거나 크기가 달라도 괜찮아요. 여기서 모은 후보들이 다음 Step(기능 요구사항 정의)과 Stage 3의 마무리(요구사항 검토)에서 골라 다듬어져요.",
            "perspectives": [
                "사용자 관점의 필요(user needs)를 모아봤나요?",
                "인터뷰·브레인스토밍·유스케이스 등 도출 기법을 활용했나요?",
                "유사·경쟁 서비스 분석으로 후보를 추출했나요?",
                "초기 요구사항 후보 목록을 정리했나요?",
            ],
            "goals": [
                "사용자 관점의 필요를 수집할 수 있다.",
                "도출 기법을 적어도 한 가지 적용할 수 있다.",
                "유사 서비스·경쟁 분석에서 후보를 추출할 수 있다.",
                "초기 요구사항 후보 목록을 정리할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "구현 가능성을 먼저 따져 후보를 지우기 — 이 단계에선 넓게 펼쳐두는 게 우선이에요",
                    "bad_example": "이건 어려우니 아예 리스트에 안 쓴다.",
                    "good_example": "일단 후보에 적어두고 이후 검토 단계에서 우선순위로 조정한다.",
                },
                {
                    "mistake": "팀 내부 의견만으로 끝내기 — 사용자의 말을 한 번이라도 직접 들어야 해요",
                    "bad_example": "팀원들이 생각한 기능만 리스트에 적었다.",
                    "good_example": "잠재 사용자 2~3명에게 '어떤 게 있으면 좋을까'를 묻고 리스트에 합친다.",
                },
                {
                    "mistake": "요구사항을 기능 이름만 적고 끝내기 — 누구의 어떤 필요인지가 함께 있어야 의미가 생겨요",
                    "bad_example": "검색 기능.",
                    "good_example": "바쁜 사용자는 키워드만으로 필요한 정보를 2초 안에 찾고 싶다.",
                },
            ],
            "one_line_tip": "지금은 걸러내는 단계가 아니에요. 많이·넓게 펼쳐두는 게 이 단계의 미덕이에요.",
        },
        "default_dictionary": [
            {
                "term": "요구사항 (Requirement)",
                "definition": "시스템이 해야 할 일 혹은 갖춰야 할 품질을 한 줄로 표현한 문장이에요. 기능 요구와 비기능 요구로 나뉘어요.",
            },
            {
                "term": "유저 스토리 (User Story)",
                "definition": "'~로서, ~를 할 수 있다, 왜냐하면 ~'처럼 사용자 관점에서 쓴 짧은 요구사항 표현이에요.",
            },
            {
                "term": "유스케이스 (Use Case)",
                "definition": "사용자가 시스템을 통해 목적을 달성하는 시나리오를 단계별로 나열한 설명이에요.",
            },
            {
                "term": "브레인스토밍 (Brainstorming)",
                "definition": "평가를 미루고 자유롭게 아이디어를 펼치는 도출 기법이에요. 중복·비현실은 신경 쓰지 않아요.",
            },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d1959809e9720ef6b61eb3b28?source=copy_link",
        "default_mentoring": {
            "description": "모은 아이디어를 '검증할 수 있는 문장'으로 바꾸는 자리예요. '무엇을 입력하면 무엇이 나와야 하는가'가 한 줄로 보이면, Stage 6에서 테스트 케이스를 만들 때 자연스럽게 기준이 따라와요. 기능은 많이 쓰기보다 선명하게 쓰는 것이 핵심이에요.",
            "perspectives": [
                "핵심 기능을 검증 가능한 형태로 명세했나요?",
                "기능을 유스케이스·유저스토리 등으로 기술했나요?",
                "기능 간 관계·의존성을 정리했나요?",
                "각 기능의 입력·출력·동작 조건을 적었나요?",
            ],
            "goals": [
                "핵심 기능을 검증 가능한 형태로 명세할 수 있다.",
                "기능을 유스케이스·유저스토리로 기술할 수 있다.",
                "기능 간 관계·의존성을 정리할 수 있다.",
                "입력·출력·동작 조건을 명시할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "'편리한 ~' 같은 모호한 문장 — 검증할 수 없는 요구사항은 요구사항이 아니에요",
                    "bad_example": "사용자가 편리하게 검색할 수 있어야 한다.",
                    "good_example": "사용자는 키워드를 입력해 2초 이내에 관련 게시글 목록을 받는다.",
                },
                {
                    "mistake": "기능을 단독으로만 보고 의존성을 놓치기",
                    "bad_example": "결제 기능과 주문 기능을 따로 정의한다.",
                    "good_example": "결제는 주문 생성 완료가 선행된다는 의존성을 명시한다.",
                },
                {
                    "mistake": "정상 케이스만 적고 예외는 빼기",
                    "bad_example": "로그인에 성공하면 메인 화면으로 이동한다.",
                    "good_example": "로그인 성공 시 메인 화면으로 이동하고, 실패 시 오류 메시지를 같은 화면에 표시한다.",
                },
            ],
            "one_line_tip": "'무엇을 받고, 어떤 조건에서, 무엇을 내놓는지'가 한 줄로 보이면 좋은 요구사항이에요.",
        },
        "default_dictionary": [
            {
                "term": "기능 요구사항 (Functional Requirement)",
                "definition": "시스템이 '무엇을 하는가'를 정의한 요구사항이에요. 입력·출력·조건이 분명할수록 좋은 문장이에요.",
            },
            {
                "term": "입력·출력 (I/O Specification)",
                "definition": "어떤 값을 받아서 어떤 결과를 돌려주는지 정의한 기능의 계약이에요. 테스트의 기준이 되기도 해요.",
            },
            {
                "term": "의존성 (Dependency)",
                "definition": "한 기능이 제대로 동작하려면 먼저 끝나 있어야 하는 다른 기능이나 조건을 말해요.",
            },
            {
                "term": "예외 처리 (Error Handling)",
                "definition": "정상 흐름이 깨졌을 때(실패·잘못된 입력 등) 시스템이 어떻게 반응할지를 정해둔 규칙이에요.",
            },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d195980beb8cbd9020c5abd5a?source=copy_link",
        "default_mentoring": {
            "description": "품질 기준을 세우는 자리예요. 기능이 '무엇을 하는가'라면, 비기능은 '얼마나 잘 하는가'예요. 성능·보안·사용성·확장성처럼 기능 외적으로 시스템이 갖춰야 할 속성을 정의해요. 전부 완벽히 정할 필요는 없고, 프로젝트 규모에 맞춰 '지금 꼭 지켜야 하는 선'만 숫자로 적어두면 Stage 6 테스트 기준으로 그대로 쓸 수 있어요.",
            "perspectives": [
                "주요 기능의 성능·응답 시간·처리량 목표를 정했나요?",
                "보안·인증·데이터 보호 관련 최소 기준을 적었나요?",
                "사용성·접근성 관점에서 지원 범위를 정했나요?",
                "호환성·확장성·유지보수성 관점의 요구를 적어뒀나요?",
            ],
            "goals": [
                "성능·응답 시간·처리량 목표를 설정할 수 있다.",
                "보안·인증·데이터 보호 요구사항을 정의할 수 있다.",
                "사용성·접근성 요구사항을 정의할 수 있다.",
                "호환성·확장성·유지보수성 요구사항을 정리할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "'빠르게' 같은 주관적 표현 — 숫자 하나로 바꾸면 기준이 생겨요",
                    "bad_example": "응답이 빨라야 한다.",
                    "good_example": "주요 API 응답이 2초 이내여야 한다(동시 사용자 20명 가정).",
                },
                {
                    "mistake": "MVP에서 감당 못 할 수준의 목표를 잡기 — 현실적인 초기 목표부터 시작해야 해요",
                    "bad_example": "동시 사용자 10만 명을 지원한다.",
                    "good_example": "초기에는 동시 사용자 100명 기준, 이후 단계에서 점진 확장한다.",
                },
                {
                    "mistake": "보안을 '나중에'로 미루기",
                    "bad_example": "보안은 나중에 생각한다.",
                    "good_example": "최소한 비밀번호 해시·외부 API 키 분리 정도는 초기부터 지킨다.",
                },
            ],
            "one_line_tip": "숫자 한 줄만 적어도 '빠르게'보다 훨씬 구체적인 기준이 돼요.",
        },
        "default_dictionary": [
            {
                "term": "비기능 요구사항 (Non-Functional Requirement)",
                "definition": "시스템이 '얼마나 잘 해야 하는가'를 정의한 요구사항이에요. 성능·보안·사용성 등이 대표적이에요.",
            },
            {
                "term": "성능 (Performance)",
                "definition": "응답 속도·처리량·자원 사용량처럼 시스템의 속도와 규모에 관한 품질 지표예요.",
            },
            {
                "term": "접근성 (Accessibility)",
                "definition": "시각·청각·조작 등에 어려움이 있는 사용자도 서비스를 이용할 수 있도록 고려한 품질이에요.",
            },
            {
                "term": "확장성 (Scalability)",
                "definition": "사용자·데이터가 늘어나도 시스템이 무너지지 않고 감당할 수 있는 정도를 뜻해요.",
            },
            {
                "term": "유지보수성 (Maintainability)",
                "definition": "시간이 지나 수정·기능 추가가 필요할 때 쉽게 대응할 수 있는 정도를 뜻해요.",
            },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d195980538815c17843e4dfe9?source=copy_link",
        "default_mentoring": {
            "description": "Stage 3의 마무리 지점이에요. 많이 적은 요구사항을 선명하게 정리하는 단계이고, 중복·충돌을 걸러내고 우선순위를 정하면 Stage 4의 설계가 훨씬 가벼워져요. 여기서 남긴 '요구사항 기준표'는 설계·개발·테스트 내내 참조되는 자산이 되어요.",
            "perspectives": [
                "요구사항 간 중복·충돌을 정리했나요?",
                "Must·Should·Could 또는 MVP 포함 여부로 우선순위를 정했나요?",
                "현재 자원 안에서 실현 가능한지 다시 점검했나요?",
                "요구사항-기능-테스트를 이어줄 연결 표(또는 메모)를 준비했나요?",
            ],
            "goals": [
                "요구사항 간 중복·충돌을 정리할 수 있다.",
                "요구사항에 우선순위를 부여할 수 있다.",
                "실현 가능성을 재점검할 수 있다.",
                "요구사항 추적 체계를 수립할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "모두를 'Must'로 분류하기 — '전부 중요'는 '아무것도 중요하지 않다'와 같아요",
                    "bad_example": "대부분의 요구사항이 Must로 표시됨.",
                    "good_example": "MVP 데모에 꼭 필요한 5개만 Must, 나머지는 Should·Could로 나눈다.",
                },
                {
                    "mistake": "요구사항-테스트 연결을 미루기 — 이 단계에서 한 줄씩 붙여두면 Stage 6가 쉬워져요",
                    "bad_example": "테스트는 Stage 6에서 한꺼번에 붙인다.",
                    "good_example": "각 Must 요구사항 옆에 '어떤 방식으로 검증하는지' 한 줄씩 적어둔다.",
                },
                {
                    "mistake": "중복된 요구사항을 합치지 않고 그대로 두기",
                    "bad_example": "비슷한 요구사항이 3개 나열되어 있다.",
                    "good_example": "비슷한 3개를 하나로 합치고, 세부는 하위 항목으로 풀어 쓴다.",
                },
            ],
            "one_line_tip": "'전부 중요'는 '아무것도 중요하지 않다'와 같아요. 최소 Must 3~5개만 고르세요.",
        },
        "default_dictionary": [
            {
                "term": "MoSCoW 우선순위",
                "definition": "Must·Should·Could·Won't 네 단계로 요구사항을 나눠 무엇을 먼저 할지 정하는 기법이에요.",
            },
            {
                "term": "MVP (Minimum Viable Product)",
                "definition": "가장 핵심이 되는 기능만으로 먼저 만들어 내는 '작동하는 최소 제품'이에요. 모든 Must 요구를 포함해요.",
            },
            {
                "term": "요구사항 추적 (Traceability)",
                "definition": "각 요구사항이 어떤 기능·설계·테스트와 연결되는지를 표나 링크로 남기는 체계예요.",
            },
            {
                "term": "충돌 (Conflict)",
                "definition": "두 요구사항이 서로 양립하기 어려운 상태예요. 검토 단계에서 합치거나 한쪽을 포기해야 해요.",
            },
        ],
    },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d1959802f9d0afaec4f4e98e6?source=copy_link",
        "default_mentoring": {
            "description": "설계의 첫 걸음이에요. 상세 설계가 아니라 '시스템 전체 모양'을 그리는 단계이고, 한 장짜리 다이어그램이어도 좋아요. 여기서 그려진 큰 그림이 데이터 모델·인터페이스·개발·테스트 전반에서 팀이 같은 구조를 떠올리게 해주는 지도 역할을 해요. 세부는 다음 Step에서 채우면 돼요.",
            "perspectives": [
                "프론트·백엔드·DB·외부 서비스 등 주요 구성요소를 식별했나요?",
                "구성요소 간 통신·의존 관계를 그려봤나요?",
                "아키텍처 패턴(모놀리식·3-tier 등)을 선택했나요?",
                "요구사항이 어떤 구성요소에서 실현되는지 매핑해봤나요?",
                "배포·인프라 구조의 큰 그림을 잡았나요?",
            ],
            "goals": [
                "주요 구성요소를 식별할 수 있다.",
                "구성요소 간 통신·의존 관계를 설명할 수 있다.",
                "아키텍처 패턴·스타일을 선택할 수 있다.",
                "요구사항을 구성요소에 배분할 수 있다.",
                "배포·인프라 구조의 큰 그림을 설명할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "너무 상세하게 그리려 하기 — 큰 덩어리 5~7개면 첫 아키텍처로 충분해요",
                    "bad_example": "처음부터 모든 함수·테이블·엔드포인트까지 그린다.",
                    "good_example": "한 장에 큰 덩어리 5~7개만 그리고 세부는 다음 작업으로 미룬다.",
                },
                {
                    "mistake": "요구사항과 연결하지 않고 그리기 — 설계는 요구사항을 실현하기 위한 도구예요",
                    "bad_example": "아키텍처를 먼저 그린 뒤 요구사항을 나중에 맞춘다.",
                    "good_example": "핵심 요구사항 옆에 '어느 구성요소가 맡는가'를 한 줄씩 적으며 그린다.",
                },
                {
                    "mistake": "팀 내에서 설명 한 번도 안 해보고 넘어가기",
                    "bad_example": "혼자 그리고 공유만 한다.",
                    "good_example": "팀원 한 명에게 10분 안에 설명할 수 있는지 시도해보고, 막히면 다시 다듬는다.",
                },
            ],
            "one_line_tip": "세부 대신 '큰 덩어리'에 집중하면, 팀이 같은 그림을 떠올릴 수 있어요.",
        },
        "default_dictionary": [
            {
                "term": "아키텍처 (Architecture)",
                "definition": "시스템을 구성하는 큰 덩어리와 그들의 관계를 그림으로 보여주는 설계예요.",
            },
            {
                "term": "모놀리식 (Monolithic)",
                "definition": "모든 기능이 하나의 앱으로 묶여 있는 아키텍처 스타일이에요. 초반 개발이 단순해요.",
            },
            {
                "term": "3-tier 구조",
                "definition": "프론트(화면)·백엔드(로직)·DB(저장소) 세 층으로 나눈 고전적인 아키텍처 스타일이에요.",
            },
            {
                "term": "API",
                "definition": "서로 다른 구성요소가 데이터를 주고받기 위해 정해둔 호출 방식이에요. 입력과 출력의 계약이에요.",
            },
            {
                "term": "배포 (Deployment)",
                "definition": "개발한 시스템을 실제 운영 환경으로 올려 사용자에게 서비스하는 과정이에요.",
            },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d1959801b9ec5ccaaca273002?source=copy_link",
        "default_mentoring": {
            "description": "데이터의 기준선을 세우는 자리예요. 시스템이 저장할 데이터 종류(엔티티)와 데이터들 사이의 관계를 정리하는 단계이고, 여기서 잡아둔 데이터 모델이 이후 Stage 내내 '진실의 기준선'으로 쓰여요. 처음부터 완벽할 필요는 없어도 주요 엔티티 5~10개와 그 관계는 또렷해야 해요.",
            "perspectives": [
                "핵심 데이터 종류(엔티티)와 주요 속성을 식별했나요?",
                "데이터 종류 간 관계(하나-여럿·여럿-여럿 등)를 정의했나요?",
                "데이터 타입·제약조건(필수·고유·길이 제한 등)을 정리했나요?",
                "저장소를 선택하고 스키마 구조를 정리했나요?",
            ],
            "goals": [
                "핵심 엔티티와 속성을 식별할 수 있다.",
                "엔티티 간 관계를 정의할 수 있다.",
                "데이터 타입·제약조건을 정리할 수 있다.",
                "저장소를 선택하고 스키마를 구조화할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "엔티티를 너무 많이 쪼개 시작부터 복잡해지기 — 핵심 5~10개로 시작하면 충분해요",
                    "bad_example": "30개의 테이블을 먼저 설계하고 시작한다.",
                    "good_example": "핵심 5~10개만 먼저 잡고, 이후 기능이 생길 때 추가한다.",
                },
                {
                    "mistake": "관계를 이름만 적고 방향을 생략하기",
                    "bad_example": "게시글과 사용자는 연관이 있다.",
                    "good_example": "한 사용자는 여러 게시글을 가질 수 있다(하나-여럿).",
                },
                {
                    "mistake": "기능 관점으로만 생각해 데이터 중복이 숨기",
                    "bad_example": "'주문 화면에 필요한 필드'만 주문 엔티티에 전부 넣는다.",
                    "good_example": "주문·사용자·상품을 별도 엔티티로 두고 참조로 연결해 중복을 없앤다.",
                },
            ],
            "one_line_tip": "엔티티는 '저장해야 할 데이터 종류'라고 생각하면 부담이 훨씬 줄어요.",
        },
        "default_dictionary": [
            {
                "term": "엔티티 (Entity)",
                "definition": "시스템이 저장할 데이터 종류예요. 사용자, 게시글, 주문처럼 '명사'로 떠올릴 수 있는 대상이에요.",
            },
            {
                "term": "속성 (Attribute)",
                "definition": "한 엔티티가 가지는 세부 정보예요. 사용자 엔티티의 이메일·이름 같은 것들이 해당해요.",
            },
            {
                "term": "관계 (Relationship)",
                "definition": "엔티티들이 서로 어떻게 이어져 있는지 표현한 것. '하나-여럿', '여럿-여럿' 같은 형태가 있어요.",
            },
            {
                "term": "ERD (Entity Relationship Diagram)",
                "definition": "엔티티와 관계를 한 장의 그림으로 표현한 도식이에요. 데이터 설계의 지도 역할을 해요.",
            },
            {
                "term": "스키마 (Schema)",
                "definition": "데이터가 어떤 형태로 저장되는지를 정의한 구조예요. 컬럼 이름·타입·제약이 포함돼요.",
            },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d195980eea311ede63cb86ce1?source=copy_link",
        "default_mentoring": {
            "description": "외부 계약을 그리는 자리예요. 외부(UI·API)와 내부(컴포넌트 간)의 주요 인터페이스를 정의하는 단계이고, 인터페이스는 '외부에서 보이는 계약'이기 때문에 세부 명세까지 가지 않더라도 '모양'만 잡혀 있으면 개발 중에도 프론트·백엔드가 중심을 잃지 않아요.",
            "perspectives": [
                "주요 UI 화면 구성(와이어프레임·화면 구조)을 잡았나요?",
                "API 엔드포인트와 입출력 스펙의 초안을 적었나요?",
                "컴포넌트 간 내부 인터페이스의 계약을 정의했나요?",
                "외부 서비스 연동 인터페이스를 정리했나요?",
            ],
            "goals": [
                "사용자 UI 구성을 설명할 수 있다.",
                "API 엔드포인트·입출력 스펙 초안을 작성할 수 있다.",
                "컴포넌트 간 내부 인터페이스를 정의할 수 있다.",
                "외부 서비스 연동 인터페이스를 정리할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "UI 픽셀 단위 디자인부터 시작 — 흐름이 먼저, 디테일은 나중이에요",
                    "bad_example": "처음부터 피그마로 완성도 100% 시안을 만든다.",
                    "good_example": "손 스케치 수준 와이어프레임으로 흐름만 잡고 세부 디자인은 이후에.",
                },
                {
                    "mistake": "API 입출력을 정하지 않은 채 프론트·백엔드 동시 개발 — 나중에 반드시 어긋나요",
                    "bad_example": "일단 각자 구현하고 나중에 맞춰본다.",
                    "good_example": "핵심 API 3~5개의 입출력 스펙을 한 장 문서로 먼저 합의한다.",
                },
                {
                    "mistake": "외부 서비스 연동을 가볍게 생각하기",
                    "bad_example": "쓰면 되겠지.",
                    "good_example": "인증 방식·호출 제한·오류 대응을 미리 확인하고 인터페이스 명세에 함께 기록한다.",
                },
            ],
            "one_line_tip": "계약의 '모양'만 잡혀 있어도 구현 도중 방향을 잃을 일이 확 줄어요.",
        },
        "default_dictionary": [
            {
                "term": "와이어프레임 (Wireframe)",
                "definition": "화면의 구성과 흐름만 빠르게 스케치한 단순한 초안이에요. 디자인보다 구조에 집중해요.",
            },
            {
                "term": "엔드포인트 (Endpoint)",
                "definition": "API에서 특정 기능을 부를 수 있는 주소예요. 예: /users, /orders 같은 경로가 해당해요.",
            },
            {
                "term": "입출력 스펙 (I/O Spec)",
                "definition": "API가 받는 값과 돌려주는 값의 형식을 정해둔 명세예요. 프론트·백엔드의 계약서가 돼요.",
            },
            {
                "term": "외부 연동 (Integration)",
                "definition": "우리 시스템과 다른 서비스(결제·지도·인증 등)를 연결해서 함께 동작하게 만드는 작업이에요.",
            },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d195980ed82e6c00fb7178a5c?source=copy_link",
        "default_mentoring": {
            "description": "Stage 4의 마무리 지점이에요. 리뷰의 목적은 '결함 찾기'가 아니라 '팀이 같은 그림을 보고 있는지 맞추는' 시간이에요. Stage 4에서 만든 아키텍처·데이터 모델·인터페이스 세 문서가 요구사항을 제대로 실현할 수 있는지 함께 점검하고, 수정 방향을 합의해요. 발견된 수정사항은 가볍게 기록하고 Stage 5(개발)에 반영하면 돼요.",
            "perspectives": [
                "각 요구사항이 설계의 어느 구성요소로 구현되는지 확인했나요?",
                "아키텍처·데이터 모델·인터페이스 세 문서 사이에 어긋난 부분은 없나요?",
                "성능·보안·확장성 관점에서 위험해 보이는 부분은 없나요?",
                "초기 선택한 기술·프레임워크가 여전히 적절한지 점검했나요?",
                "오늘 리뷰에서 나온 수정 방향을 정리했나요?",
            ],
            "goals": [
                "요구사항과 설계의 매핑을 점검할 수 있다.",
                "설계 간 불일치·누락을 식별할 수 있다.",
                "성능·보안·확장성 관점의 설계를 점검할 수 있다.",
                "기술·프레임워크 선택의 적절성을 재검토할 수 있다.",
                "리뷰 결과와 수정 방향을 정리할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "수정만 지적하고 이유를 안 남기기 — 근거가 있어야 다음 결정에도 쓸 수 있어요",
                    "bad_example": "이 부분은 바꾸는 게 좋겠다.",
                    "good_example": "이 부분은 해당 요구사항과 연결이 약해서 X 구조로 바꾸는 게 좋겠다.",
                },
                {
                    "mistake": "리뷰 후 수정 항목을 추적하지 않기 — 기억은 일주일을 못 가요",
                    "bad_example": "회의 후 기억에 의존한다.",
                    "good_example": "수정 항목을 담당자·기한과 함께 체크리스트로 남긴다.",
                },
                {
                    "mistake": "모두 '좋아 보인다'로 끝내기 — 의도적으로 약한 지점을 찾아봐야 해요",
                    "bad_example": "특별한 문제는 없다.",
                    "good_example": "'성능이 가장 걱정되는 구간', '요구사항 연결이 가장 약한 구간'을 의도적으로 짚고 토론한다.",
                },
            ],
            "one_line_tip": "리뷰의 목적은 '틀린 점 찾기'보다 '같은 그림 맞추기'에 있어요.",
        },
        "default_dictionary": [
            {
                "term": "설계 리뷰 (Design Review)",
                "definition": "설계가 요구사항을 잘 실현할 수 있는지 팀이 함께 점검하는 자리예요. 결함 찾기보다 그림 맞추기가 목적이에요.",
            },
            {
                "term": "매핑 (Mapping)",
                "definition": "요구사항과 설계 요소를 1대1 또는 1대N으로 연결해 '어디서 구현되는가'를 드러내는 작업이에요.",
            },
            {
                "term": "리뷰 이슈 (Review Issue)",
                "definition": "리뷰 중에 발견된 수정·개선 항목이에요. 담당자·기한과 함께 체크리스트로 남기면 추적이 쉬워요.",
            },
        ],
    },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d1959802c9d57e4f8f92a62d1?source=copy_link",
        "default_mentoring": {
            "description": "개발의 출발선을 세팅하는 자리예요. 팀원 모두가 0에서 같은 환경으로 시작할 수 있게 준비하는 단계이고, Stage 2에서 결정한 기술 스택과 Stage 4 설계를 실제 폴더·스크립트·저장소로 구현하는 첫 작업이에요. 여기서 준비한 내용이 그대로 프로젝트 README의 첫 장이 되어요.",
            "perspectives": [
                "코드 저장소·브랜치 전략을 구성했나요?",
                "로컬 개발 환경·의존성 설치 방법을 정리했나요?",
                "프로젝트 스캐폴드·초기 폴더 구조를 잡았나요?",
                "빌드·실행·배포 스크립트의 기본을 준비했나요?",
            ],
            "goals": [
                "코드 저장소·브랜치 전략을 수립할 수 있다.",
                "로컬 개발 환경·의존성을 세팅할 수 있다.",
                "프로젝트 스캐폴드·초기 구조를 수립할 수 있다.",
                "빌드·실행·배포 스크립트 기초를 구성할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "환경 구성을 구두로만 전달 — 문서가 없으면 새 팀원마다 같은 질문이 반복돼요",
                    "bad_example": "내가 한 번 보여줄게.",
                    "good_example": "필요한 명령어를 README에 단계별로 적어두어 누구나 따라올 수 있게 한다.",
                },
                {
                    "mistake": "버전·환경 변수 차이로 '내 컴퓨터에서만 되기'",
                    "bad_example": "내 환경에서는 잘 되는데 왜 안 되지.",
                    "good_example": "필요한 런타임 버전·환경 변수 목록을 문서화해 공유한다.",
                },
                {
                    "mistake": "빌드·실행 스크립트 없이 구두 명령만 공유",
                    "bad_example": "그냥 이 명령어 치면 돼.",
                    "good_example": "자주 쓰는 명령을 package.json 스크립트 또는 Makefile 등으로 저장소에 저장한다.",
                },
            ],
            "one_line_tip": "'같은 명령어로 같은 결과'가 이 단계의 성공 기준이에요.",
        },
        "default_dictionary": [
            {
                "term": "저장소 (Repository)",
                "definition": "코드와 그 변경 이력을 모아두는 공간이에요. GitHub·GitLab 같은 서비스에 올려두고 팀이 함께 써요.",
            },
            {
                "term": "의존성 (Dependency)",
                "definition": "우리 프로젝트가 제대로 돌아가기 위해 필요한 외부 라이브러리·패키지들을 뜻해요.",
            },
            {
                "term": "스캐폴드 (Scaffold)",
                "definition": "프로젝트 시작 시 기본 폴더·설정·예제 코드가 미리 깔려 있는 골격을 말해요.",
            },
            {
                "term": "빌드 (Build)",
                "definition": "소스코드를 실제로 실행·배포할 수 있는 형태로 변환하는 과정이에요.",
            },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d195980abbe60dc0947053f5c?source=copy_link",
        "default_mentoring": {
            "description": "Stage 5의 가장 긴 구간이에요. 앞서 만든 설계를 실제 동작하는 코드로 바꾸는 단계이고, 완성도보다 '무엇이 돌아가고 무엇이 남았는지'를 한눈에 보이게 하는 것이 중요해요. 여기서는 작업 상태를 팀이 공유할 수 있는 기록을 함께 남겨두는 것이 핵심이에요.",
            "perspectives": [
                "핵심 기능을 우선순위대로 구현하고 있나요?",
                "공통 모듈·유틸리티를 정리하며 구현하고 있나요?",
                "데이터 처리·비즈니스 로직이 잘 드러나는 구조인가요?",
                "UI 또는 엔드포인트 등 사용자 접점을 구현했나요?",
            ],
            "goals": [
                "핵심 기능별 구현을 진행할 수 있다.",
                "공통 모듈·유틸리티를 구현할 수 있다.",
                "데이터 처리·비즈니스 로직을 구현할 수 있다.",
                "UI 또는 엔드포인트를 구현할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "한 기능을 완벽히 끝내려다 다른 기능이 밀림 — '덜 완성된 전체'가 '완벽한 일부'보다 가치 있어요",
                    "bad_example": "첫 기능에만 2주를 쓴다.",
                    "good_example": "모든 핵심 기능을 먼저 '돌아가는 수준'까지 만들고, 품질은 이후 반복 개선한다.",
                },
                {
                    "mistake": "공통 로직을 한 곳에 두지 않고 중복 작성",
                    "bad_example": "같은 검증 로직을 세 화면에 각각 구현한다.",
                    "good_example": "공통 유틸리티 함수 하나로 정리해 세 화면에서 호출한다.",
                },
                {
                    "mistake": "작업 진행 상황을 공유하지 않기",
                    "bad_example": "혼자 구현하고 끝나면 공유한다.",
                    "good_example": "주간 짧은 기록(완료·진행·막힘)을 팀에 남겨 병목을 조기에 발견한다.",
                },
            ],
            "one_line_tip": "'덜 완성된 전체'가 '완벽한 일부'보다 훨씬 가치 있어요.",
        },
        "default_dictionary": [
            {
                "term": "핵심 기능 (Core Feature)",
                "definition": "서비스의 가치를 가장 먼저 전달하는 Must 기능들이에요. MVP에서 반드시 작동해야 하는 항목이에요.",
            },
            {
                "term": "공통 모듈 (Shared Module)",
                "definition": "여러 기능에서 반복해서 쓰이는 코드 묶음이에요. 중복을 줄이고 수정 포인트를 한 곳으로 모아줘요.",
            },
            {
                "term": "비즈니스 로직 (Business Logic)",
                "definition": "서비스의 규칙과 흐름을 담은 코드예요. '주문이 생성되면 재고를 줄인다' 같은 의사결정이 해당해요.",
            },
            {
                "term": "엔드포인트 (Endpoint)",
                "definition": "클라이언트가 특정 기능을 호출하는 API 주소예요. URL과 메서드 조합으로 표시돼요.",
            },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d195980148092e7ebe298e534?source=copy_link",
        "default_mentoring": {
            "description": "조각을 하나로 합치는 자리예요. 따로 잘 돌던 모듈들이 한 시스템으로 움직이는지 확인하는 단계이고, 통합에서 발견되는 문제는 기록만 잘 해둬도 이후 디버깅 시간이 크게 줄어요. 이 단계가 잘 되어 있어야 Stage 6의 테스트가 '기능 개별 테스트'가 아니라 '실제 사용 시나리오 테스트'로 올라갈 수 있어요.",
            "perspectives": [
                "프론트·백엔드·DB 등 모듈 간 연결이 이루어졌나요?",
                "대표 시나리오(처음부터 끝까지 흐름)가 엔드투엔드로 연결되나요?",
                "통합 과정에서 생긴 충돌·에러를 해결·기록했나요?",
                "통합 빌드·실행이 정상으로 확인됐나요?",
            ],
            "goals": [
                "모듈 간 연결 작업을 수행할 수 있다.",
                "엔드투엔드 시나리오를 연결할 수 있다.",
                "통합 과정의 충돌·에러를 해결할 수 있다.",
                "통합 빌드·실행을 검증할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "통합을 프로젝트 막바지로 미루기 — 자주·작게 합쳐야 문제가 작게 드러나요",
                    "bad_example": "모든 모듈이 완성된 뒤에야 붙여본다.",
                    "good_example": "초기부터 가짜 데이터로라도 전체 흐름을 이어두고, 점진적으로 실제 구현으로 교체한다.",
                },
                {
                    "mistake": "통합 중 에러를 메모 없이 바로 고치기 — 다음에 또 만나면 다시 헤매요",
                    "bad_example": "문제가 발생했지만 고치고 넘어간다.",
                    "good_example": "원인·해결책을 짧게 기록해 팀 공유 문서에 남긴다.",
                },
                {
                    "mistake": "구간별 성공만 보고 전체를 안 돌려보기",
                    "bad_example": "각 구간이 된다고 하니 통합도 될 것이다.",
                    "good_example": "대표 시나리오를 처음부터 끝까지 한 번 돌려보고, 끊기는 지점을 기록한다.",
                },
            ],
            "one_line_tip": "자주·작게 통합할수록, 드러나는 문제도 작고 고치기 쉬워요.",
        },
        "default_dictionary": [
            {
                "term": "통합 (Integration)",
                "definition": "개별 모듈을 합쳐 하나의 실행 가능한 시스템으로 만드는 작업이에요. 모듈 간 충돌이 드러나는 지점이에요.",
            },
            {
                "term": "엔드투엔드 (End-to-End)",
                "definition": "사용자가 시작 버튼부터 마지막 화면까지 실제 흐름을 따라가는 전체 경로를 뜻해요.",
            },
            {
                "term": "머지 (Merge)",
                "definition": "서로 다른 브랜치의 변경사항을 하나로 합치는 Git 작업이에요. 충돌이 생기면 직접 해결해야 해요.",
            },
            {
                "term": "CI (Continuous Integration)",
                "definition": "코드를 올릴 때마다 자동으로 빌드·테스트를 돌려 문제를 일찍 발견하는 개발 방식이에요.",
            },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d19598042b443dc51d22b0e1c?source=copy_link",
        "default_mentoring": {
            "description": "Stage 5의 마무리 지점이에요. 작성된 코드를 팀원이나 본인이 다시 읽으며 결함과 나쁜 패턴을 찾고 개선하는 단계이고, 목적은 '잘못 잡기'가 아니라 '팀이 코드를 이해할 수 있게 만들기'에 가까워요. 혼자 하는 프로젝트여도 '나중의 나를 위한 리뷰'로 같은 효과를 낼 수 있어요.",
            "perspectives": [
                "코드 리뷰·피어 리뷰 활동을 진행했나요?",
                "코딩 컨벤션·품질을 점검했나요?",
                "단위 테스트나 개발자 자체 검증을 수행했나요?",
                "발견된 결함을 수정·개선했나요?",
            ],
            "goals": [
                "코드 리뷰·피어 리뷰 활동을 수행할 수 있다.",
                "코딩 컨벤션·품질을 점검할 수 있다.",
                "단위 테스트 또는 자체 검증을 수행할 수 있다.",
                "발견된 결함을 수정·개선할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "리뷰 코멘트를 인신 공격처럼 전달 — 코드를 비판하되 사람을 비판하지 않아요",
                    "bad_example": "이 코드 너무 이상해요.",
                    "good_example": "이 부분은 X 이유로 Y 방식이 더 적절해 보입니다. 어떻게 생각하세요?",
                },
                {
                    "mistake": "자동화 없이 컨벤션을 사람 눈으로만 잡기",
                    "bad_example": "매번 수동으로 포맷을 맞춘다.",
                    "good_example": "린터·포매터를 도입해 커밋 전에 자동으로 통일한다.",
                },
                {
                    "mistake": "테스트 없이 '되겠지'로 마무리하기",
                    "bad_example": "직접 눌러보니 되니까 된 거다.",
                    "good_example": "핵심 비즈니스 로직에 한해서는 단위 테스트 한두 개라도 작성해둔다.",
                },
            ],
            "one_line_tip": "리뷰는 '잘못 잡기'가 아니라 '함께 읽을 수 있는 코드 만들기'예요.",
        },
        "default_dictionary": [
            {
                "term": "코드 리뷰 (Code Review)",
                "definition": "작성된 코드를 다른 사람이(또는 본인이 나중에) 읽으며 개선점을 찾는 활동이에요. 품질과 이해도를 함께 높여요.",
            },
            {
                "term": "컨벤션 (Convention)",
                "definition": "네이밍·포맷·주석 같은 코드 스타일에 대한 팀 약속이에요. 통일되면 읽기와 유지보수가 쉬워져요.",
            },
            {
                "term": "린터 (Linter)",
                "definition": "코드의 문법·스타일 문제를 자동으로 찾아주는 도구예요. 사람 눈으로 놓치는 사소한 오류를 잡아줘요.",
            },
            {
                "term": "단위 테스트 (Unit Test)",
                "definition": "함수·모듈 같은 작은 단위 하나를 독립적으로 검증하는 테스트예요. 회귀 방지에 효과적이에요.",
            },
        ],
    },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d1959808ea370c2f2433237f7?source=copy_link",
        "default_mentoring": {
            "description": "검증의 출발점이에요. Stage 3에서 약속한 요구사항을 어떻게 검증할지 전략을 정하는 단계이고, '모두 테스트하겠다'보다 '어디까지 이번에 검증할지'를 분명히 하는 게 핵심이에요. 여기서 정한 범위·유형·시나리오가 Stage 6 전체의 기준이 되어요.",
            "perspectives": [
                "테스트 대상과 범위를 정의했나요?",
                "기능·통합·성능·보안 등 필요한 테스트 유형을 골랐나요?",
                "테스트 시나리오와 케이스를 설계했나요?",
                "테스트 데이터·입력값을 어떻게 준비할지 정했나요?",
                "테스트 환경·도구를 준비했나요?",
            ],
            "goals": [
                "테스트 대상·범위를 정의할 수 있다.",
                "필요한 테스트 유형을 선택할 수 있다.",
                "테스트 시나리오·케이스를 설계할 수 있다.",
                "테스트 데이터·입력값을 준비할 수 있다.",
                "테스트 환경·도구를 준비할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "범위 없이 '다 테스트한다'로 시작 — 범위가 없으면 끝도 없어요",
                    "bad_example": "모든 기능을 완벽히 테스트하자.",
                    "good_example": "이번에는 핵심 Must 기능 5개와 대표 흐름 1개만 검증한다.",
                },
                {
                    "mistake": "정상 케이스만 준비하기 — 실패 경로에서 더 많은 결함이 나와요",
                    "bad_example": "성공 시나리오만 테스트 케이스로 작성.",
                    "good_example": "성공·실패·경계값·예외 케이스를 함께 준비한다.",
                },
                {
                    "mistake": "요구사항과 테스트를 연결하지 않기",
                    "bad_example": "요구사항과 테스트 케이스를 따로 관리한다.",
                    "good_example": "각 요구사항 옆에 '어떤 케이스로 검증하는지'를 한 줄씩 연결해둔다.",
                },
            ],
            "one_line_tip": "'어디까지 검증할지'가 분명해지는 순간, 테스트는 부담에서 도구로 바뀌어요.",
        },
        "default_dictionary": [
            {
                "term": "테스트 범위 (Test Scope)",
                "definition": "이번 검증에서 다룰 기능·요구사항과 다루지 않을 영역을 분명히 정해둔 경계예요.",
            },
            {
                "term": "테스트 케이스 (Test Case)",
                "definition": "특정 조건에서 시스템이 어떻게 동작해야 하는지를 입력·기대 결과로 정리한 한 건의 검증 시나리오예요.",
            },
            {
                "term": "경계값 (Boundary Value)",
                "definition": "허용 범위의 끝(최소·최대·초과)에서 시스템이 제대로 동작하는지 확인할 때 쓰는 입력값이에요.",
            },
            {
                "term": "테스트 환경 (Test Environment)",
                "definition": "테스트를 실행하기 위해 준비된 별도의 시스템·데이터 공간이에요. 실제 서비스에 영향을 주지 않아요.",
            },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d195980cfadd7cf5b6275bc91?source=copy_link",
        "default_mentoring": {
            "description": "검증 실행 구간이에요. 계획한 테스트를 실제로 돌려 결과를 수집하는 단계이고, 한 번에 모두 통과시키려 하지 말고 '돌린 결과를 깔끔히 기록하는 것'을 목표로 해요. 여기서의 기록이 다음 Step(결과 분석 및 결함 기록)의 분석 재료가 되어요.",
            "perspectives": [
                "기능 테스트를 정상·예외 케이스 중심으로 수행했나요?",
                "통합·시나리오 테스트를 수행했나요?",
                "성능·보안·사용성 등 비기능 테스트를 수행했나요?",
                "테스트 결과를 체계적으로 기록·수집했나요?",
            ],
            "goals": [
                "기능 테스트를 수행할 수 있다.",
                "통합·시나리오 테스트를 수행할 수 있다.",
                "비기능 테스트를 수행할 수 있다.",
                "테스트 결과를 기록·수집할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "실패한 케이스를 기억으로만 두기 — 기록되지 않은 실패는 사라진 실패예요",
                    "bad_example": "'그건 아까 안 됐던 것 같은데.'",
                    "good_example": "실패 케이스를 캡처·재현 절차와 함께 한 줄씩 기록한다.",
                },
                {
                    "mistake": "한 번 돌려보고 끝내기 — 수정 후 회귀 테스트를 빼먹으면 새 결함이 숨어들어요",
                    "bad_example": "한 번 테스트 돌렸으니 됐다.",
                    "good_example": "수정 후 영향받는 케이스를 다시 돌리는 회귀 테스트를 함께 계획한다.",
                },
                {
                    "mistake": "비기능 테스트는 아예 빼고 가기",
                    "bad_example": "동작만 되면 됐다.",
                    "good_example": "성능·접근성 한 가지씩이라도 가볍게 돌려 결과를 기록해둔다.",
                },
            ],
            "one_line_tip": "'무엇이 되는가'만큼 '무엇이 안 되는가'를 또렷하게 기록하세요.",
        },
        "default_dictionary": [
            {
                "term": "기능 테스트 (Functional Test)",
                "definition": "요구사항에 정의된 기능이 명세대로 동작하는지 확인하는 테스트예요. 정상·실패 케이스를 함께 돌려요.",
            },
            {
                "term": "통합 테스트 (Integration Test)",
                "definition": "여러 모듈이 한 시스템으로 이어져 제대로 흐르는지 확인하는 테스트예요.",
            },
            {
                "term": "회귀 테스트 (Regression Test)",
                "definition": "수정한 부분이 기존에 잘 되던 기능을 망가뜨리지 않았는지 다시 검증하는 테스트예요.",
            },
            {
                "term": "재현 절차 (Reproduction Steps)",
                "definition": "버그나 실패 케이스를 다른 사람이 똑같이 재현할 수 있도록 단계별로 정리한 설명이에요.",
            },
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d195980bdb7edf39a9280dc12?source=copy_link",
        "default_mentoring": {
            "description": "발견을 정리하는 자리예요. 테스트 중 발견된 결함을 구조화된 형태로 남기고, 원인·심각도·수정 계획을 정리하는 단계예요. 기록되지 않은 결함은 해결되지 않는다는 원칙이 핵심이고, 여기서 남긴 결함 리스트가 프로젝트 종료 판단의 객관적 근거가 되어요.",
            "perspectives": [
                "발견된 결함을 분류·목록화했나요?",
                "재현 방법과 추정 원인을 분석했나요?",
                "결함별 심각도·우선순위를 부여했나요?",
                "결함 수정·재테스트 계획을 세웠나요?",
            ],
            "goals": [
                "결함을 목록화·분류할 수 있다.",
                "재현 방법과 원인을 분석할 수 있다.",
                "결함에 심각도·우선순위를 부여할 수 있다.",
                "수정·재테스트 계획을 수립할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "결함 설명이 추상적이라 재현이 안 됨 — 환경·조작·결과가 함께 있어야 고칠 수 있어요",
                    "bad_example": "버튼이 가끔 이상함.",
                    "good_example": "Chrome 모바일 뷰에서 '제출' 버튼을 2회 연속 누르면 요청이 중복 발송됨.",
                },
                {
                    "mistake": "모두 심각도 '높음'으로 매기기 — 우선순위가 없으면 없는 것과 같아요",
                    "bad_example": "모든 결함이 긴급.",
                    "good_example": "데모에 영향을 주는 것만 High, 나머지는 Medium·Low로 나눈다.",
                },
                {
                    "mistake": "결함을 고치고 닫기만 하고 원인을 안 남기기",
                    "bad_example": "고쳤으니 닫는다.",
                    "good_example": "원인·수정 내용·재발 방지책을 한 줄씩 남겨 유사 결함을 예방한다.",
                },
            ],
            "one_line_tip": "결함은 '기록된 것만' 해결돼요. 제목 한 줄·재현 절차 3줄이면 충분해요.",
        },
        "default_dictionary": [
            {
                "term": "결함 (Defect)",
                "definition": "예상한 대로 동작하지 않는 지점이에요. 버그, 잘못된 결과, 누락된 기능 모두 포함돼요.",
            },
            {
                "term": "심각도 (Severity)",
                "definition": "결함이 서비스와 사용자에게 미치는 영향의 크기를 High·Medium·Low 같은 단계로 매긴 것이에요.",
            },
            {
                "term": "우선순위 (Priority)",
                "definition": "결함을 언제 먼저 고칠지 순서를 정한 기준이에요. 심각도와 일치하지 않을 수도 있어요.",
            },
            {
                "term": "근본 원인 (Root Cause)",
                "definition": "결함이 발생한 진짜 이유예요. 겉으로 보이는 증상 뒤에 숨은 원인을 찾으면 재발을 막을 수 있어요.",
            },
        ],
    },
    {
        "stage_sequence": 6,
        "sequence": 4,
        "name": "최종 검토",
        "toast_message": "최종 검토를 완료했습니다! 🎉",
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
        "template_url": "https://pentagonal-berry-490.notion.site/35cc611d195980ca83f8da49dece6f22?source=copy_link",
        "default_mentoring": {
            "description": "프로젝트의 마지막 관문이에요. Stage 1에서 정의한 문제·기회와 Stage 3의 핵심 요구사항이 실제로 해결되었는지 확인하고, 프로젝트 종료 판단과 회고를 남기는 단계예요. 과하게 힘주지 말고 솔직하게 써두면 다음 프로젝트의 가장 든든한 출발점이 되어요.",
            "perspectives": [
                "처음 정의한 문제·기회가 얼마나 해결됐는지 판단했나요?",
                "핵심 요구사항이 충족됐는지 점검했나요?",
                "사용자 관점의 수용 테스트나 시연을 진행했나요?",
                "종료 판단·회고·향후 방향을 정리했나요?",
            ],
            "goals": [
                "초기 문제·기회의 해결 여부를 점검할 수 있다.",
                "핵심 요구사항 충족 여부를 점검할 수 있다.",
                "사용자 관점의 수용 테스트·시연을 수행할 수 있다.",
                "프로젝트 종료 판단과 회고·향후 방향을 정리할 수 있다.",
            ],
            "common_mistakes": [
                {
                    "mistake": "성공만 기록하고 아쉬움은 빼기 — 아쉬움이 다음 프로젝트의 자산이에요",
                    "bad_example": "완성도 높게 마무리했다.",
                    "good_example": "핵심 기능은 목표 달성, 성능 최적화와 모바일 대응은 향후 과제로 남긴다.",
                },
                {
                    "mistake": "회고를 감정만으로 끝내기 — 구체적인 행동 항목이 있어야 다음에 달라져요",
                    "bad_example": "힘들었지만 좋았다.",
                    "good_example": "잘한 것 3가지·아쉬운 것 3가지·다음에 바꿀 것 3가지 형식으로 구체화한다.",
                },
                {
                    "mistake": "사용자 없이 팀 내부만 시연하고 마무리하기",
                    "bad_example": "팀끼리 돌려보고 끝낸다.",
                    "good_example": "실제 타겟 사용자 2~3명에게 짧은 시연을 보여주고 반응을 기록한다.",
                },
            ],
            "one_line_tip": "솔직한 회고 한 장이 다음 프로젝트의 가장 든든한 출발점이 되어요.",
        },
        "default_dictionary": [
            {
                "term": "수용 테스트 (Acceptance Test)",
                "definition": "사용자나 이해관계자가 '이 정도면 쓸 만하다'고 판단하기 위해 수행하는 마지막 검증이에요.",
            },
            {
                "term": "시연 (Demo)",
                "definition": "완성된 기능을 팀 외부에 보여주며 반응을 듣는 자리예요. 수용 테스트와 함께 진행하기도 해요.",
            },
            {
                "term": "회고 (Retrospective)",
                "definition": "프로젝트 기간을 되돌아보며 잘한 것·아쉬운 것·다음에 바꿀 것을 정리하는 활동이에요.",
            },
            {
                "term": "향후 로드맵 (Future Roadmap)",
                "definition": "이번 MVP 이후 이어갈 수 있는 기능·개선 방향을 시간 축 위에 가볍게 정리한 계획이에요.",
            },
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

        # template_url: 사전 생성된 Notion 템플릿 URL (시드에서 제공)
        template_url = item.get("template_url", "")

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
                "template_url": template_url,
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
                "template_description": insert(
                    RequiredStep
                ).excluded.template_description,
                "goal": insert(RequiredStep).excluded.goal,
                "entry_criteria": insert(RequiredStep).excluded.entry_criteria,
                "fulfillment_criteria": insert(
                    RequiredStep
                ).excluded.fulfillment_criteria,
                "minimum_fulfillment_count": insert(
                    RequiredStep
                ).excluded.minimum_fulfillment_count,
                "doj_reference": insert(RequiredStep).excluded.doj_reference,
                "default_mentoring": insert(RequiredStep).excluded.default_mentoring,
                "default_dictionary": insert(RequiredStep).excluded.default_dictionary,
                "template_url": insert(RequiredStep).excluded.template_url,
            },
        )
    )
    db.execute(stmt)
    db.commit()
