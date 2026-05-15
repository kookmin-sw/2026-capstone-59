"""design-export 자동 러너 (v1.4 Z+, 옵션 B-단일).

CloudShell 실측 도구 — 8개 케이스를 순차 실행하여 AI 응답 품질·응답 시간을 측정한다.
AI 응답(questions_per_rs + core_summary)을 백엔드 Renderer 흉내 함수가 .md 골격에
끼워넣어 최종 .md를 out/ 디렉토리에 저장한다.

실행:
    python auto_design_export_runner.py

환경변수:
    AWS_REGION  (기본: us-east-1)
    MODEL_ID    (기본: us.anthropic.claude-haiku-4-5-20251001-v1:0)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import boto3

# ---------------------------------------------------------------------------
# sys.path 설정 — CloudShell(zip 해제) / 로컬 개발 양쪽 지원
# ---------------------------------------------------------------------------

_HERE = Path(__file__).resolve().parent
# CloudShell: ai/ 패키지가 스크립트와 같은 디렉토리에 있음
sys.path.insert(0, str(_HERE))
# 로컬 개발: ai/ 패키지가 프로젝트 루트(poco/)에 있음
sys.path.insert(0, str(_HERE.parent.parent))

from ai.schemas.common import CommonMistake, MentoringContent, RecommendedMethod
from ai.schemas.design_export import (
    AcceptedStepForAI,
    DesignExportInput,
    DesignExportOutput,
    ProjectContextForAI,
    RequiredStepForAI,
    RSQuestions,
)
from ai.services import generate_design_export

# ---------------------------------------------------------------------------
# 로깅
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.WARNING,
    format="[%(levelname)s] %(name)s :: %(message)s",
    stream=sys.stderr,
)

# ---------------------------------------------------------------------------
# 프로젝트 박제 데이터
# ---------------------------------------------------------------------------

PROJECT_INFO_DICT: dict[str, Any] = {
    "name": "배달 라이더 경로 최적화 앱",
    "description": "라이더의 경로 비효율을 AI로 줄이는 앱",
    "duration_months": 2,
    "member_count": 4,
    "constraints": ["React + FastAPI", "AWS Lambda 서버리스", "외주 사용 불가"],
    "initial_prompt": "배달 라이더가 경로를 비효율적으로 다니는 문제를 AI로 해결하고 싶어요.",
}

# ---------------------------------------------------------------------------
# STAGE_DEFINITIONS — 24개 RS 메타 박제
# 출처: Poco_Required_Steps_Definition_v1.md
# ---------------------------------------------------------------------------

STAGE_DEFINITIONS: list[dict] = [
    {
        "stage_sequence": 1,
        "stage_name": "아이디어 구체화",
        "required_steps": [
            {
                "required_step_id": "1-R1",
                "required_step_name": "문제/기회 정의",
                "goal": "프로젝트가 해결하려는 문제 또는 포착한 기회를 명확하게 정의한다.",
                "entry_criteria": "Stage 1의 출발점이므로 별도 선행 맥락 없이 초기 프롬프트만으로 진입 가능하다.",
                "fulfillment_criteria": [
                    "문제/기회 자체에 대한 서술·명확화",
                    "문제의 중요도·임팩트 (왜 해결할 가치가 있는가)",
                    "문제의 발생 배경·상황·맥락",
                    "기존 대안의 한계 또는 미해결 지점",
                ],
            },
            {
                "required_step_id": "1-R2",
                "required_step_name": "대상 사용자 파악",
                "goal": "정의된 문제로 불편을 겪는 구체적 사용자군을 식별하고 특성을 그린다.",
                "entry_criteria": "Step 히스토리에 문제/기회에 관한 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "1차 타겟 사용자군의 특성 정의 (연령·상황·역할 등)",
                    "사용자의 현재 행동·습관·맥락 파악",
                    "사용자 페르소나 또는 시나리오 정리",
                    "사용자 검증 활동 (인터뷰·관찰·설문 등)",
                ],
            },
            {
                "required_step_id": "1-R3",
                "required_step_name": "핵심 컨셉 정의",
                "goal": "정의된 문제를 어떤 해결책으로 풀지, 그 차별점이 무엇인지 한 단락 수준으로 정리한다.",
                "entry_criteria": "Step 히스토리에 문제 정의와 사용자 이해에 관한 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "해결 접근 방식·아이디어 서술",
                    "유사/경쟁 서비스 조사 및 비교",
                    "차별점 또는 핵심 가치 제안(Value Proposition)",
                    "주요 기능의 큰 그림·윤곽",
                ],
            },
            {
                "required_step_id": "1-R4",
                "required_step_name": "실현 가능성 검토",
                "goal": "주어진 기간·인원·기술 수준으로 컨셉을 실제로 만들 수 있는지, 주요 리스크는 무엇인지 판단한다.",
                "entry_criteria": "Step 히스토리에 핵심 컨셉에 대한 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "기술적 실현 가능성 검토",
                    "기간·자원·인원·비용 관점의 적합성 검토",
                    "프로토타입·PoC 등 소규모 검증 활동",
                    "주요 리스크·제약사항 식별",
                ],
            },
        ],
    },
    {
        "stage_sequence": 2,
        "stage_name": "프로젝트 계획",
        "required_steps": [
            {
                "required_step_id": "2-R1",
                "required_step_name": "일정 계획 수립",
                "goal": "프로젝트 전체 기간을 Stage/마일스톤 단위로 배분하는 일정 뼈대를 만든다.",
                "entry_criteria": "Step 히스토리에 \"무엇을 얼마나 만들 것인지\"에 대한 컨셉·실현 가능성 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "전체 일정을 Stage/구간으로 분할",
                    "주요 마일스톤 또는 데드라인 설정",
                    "Step/작업 단위의 공수·난이도 추정",
                    "일정 관리 방식·도구 선정",
                ],
            },
            {
                "required_step_id": "2-R2",
                "required_step_name": "역할 분담",
                "goal": "팀원 각자의 담당 영역을 정하고, 1인 프로젝트인 경우 본인이 맡을 역할들을 명시적으로 구분한다.",
                "entry_criteria": "Step 히스토리에 프로젝트의 범위·일정에 대한 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "팀원별 주 담당 영역 또는 역할 정의",
                    "역할 간 경계와 책임 범위 명시",
                    "의사결정·리뷰 주체 결정",
                    "협업·커뮤니케이션 규칙 수립",
                ],
            },
            {
                "required_step_id": "2-R3",
                "required_step_name": "위험 식별",
                "goal": "프로젝트 진행을 방해할 수 있는 주요 리스크를 미리 식별하고 대응 방향을 정한다.",
                "entry_criteria": "Step 히스토리에 일정·역할·기술 선택 등 \"깨질 수 있는 계획\"이 존재한다.",
                "fulfillment_criteria": [
                    "기술 리스크 식별 (난이도·학습 곡선 등)",
                    "일정 리스크 식별 (딜레이 요인·병목)",
                    "팀 리스크 식별 (이탈·역량·커뮤니케이션)",
                    "각 리스크별 대응·완화 방안",
                ],
            },
            {
                "required_step_id": "2-R4",
                "required_step_name": "개발 환경/도구 결정",
                "goal": "프로젝트에서 공통으로 사용할 기술 스택과 협업 도구를 확정한다.",
                "entry_criteria": "Step 히스토리에 컨셉·실현 가능성 맥락이 존재하여 어떤 기술 영역이 필요할지 판단 가능하다.",
                "fulfillment_criteria": [
                    "개발 언어·프레임워크 선정",
                    "형상관리·브랜치 전략 (Git 등)",
                    "협업·이슈 관리 도구 선정",
                    "개발·배포 환경 구성 방향",
                ],
            },
        ],
    },
    {
        "stage_sequence": 3,
        "stage_name": "요구사항 정의",
        "required_steps": [
            {
                "required_step_id": "3-R1",
                "required_step_name": "요구사항 도출",
                "goal": "시스템이 수행해야 할 일들을 사용자와 팀의 관점에서 자유롭게 모은다.",
                "entry_criteria": "Step 히스토리에 대상 사용자와 핵심 컨셉에 대한 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "사용자 관점의 필요(user needs) 수집",
                    "도출 기법 적용 (인터뷰·브레인스토밍·유스케이스 등)",
                    "유사 서비스·경쟁 분석을 통한 요구사항 추출",
                    "초기 요구사항 후보 목록 정리",
                ],
            },
            {
                "required_step_id": "3-R2",
                "required_step_name": "기능 요구사항 정의",
                "goal": "시스템이 제공해야 할 기능들을 구체적이고 검증 가능한 형태로 정의한다.",
                "entry_criteria": "Step 히스토리에 요구사항 도출 활동과 그 결과 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "핵심 기능의 명세화",
                    "기능을 유스케이스·유저스토리 등으로 기술",
                    "기능 간 관계·의존성 정리",
                    "입력·출력·동작 조건 명시",
                ],
            },
            {
                "required_step_id": "3-R3",
                "required_step_name": "비기능 요구사항 정의",
                "goal": "성능·보안·사용성 등 기능 외적으로 시스템이 갖춰야 할 품질 속성을 정의한다.",
                "entry_criteria": "Step 히스토리에 기능 요구사항에 대한 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "성능·응답 시간·처리량 관련 요구사항",
                    "보안·인증·데이터 보호 요구사항",
                    "사용성·접근성 요구사항",
                    "호환성·확장성·유지보수성 요구사항",
                ],
            },
            {
                "required_step_id": "3-R4",
                "required_step_name": "요구사항 검토",
                "goal": "도출된 요구사항의 일관성·실현 가능성·우선순위를 팀이 함께 점검하고 확정한다.",
                "entry_criteria": "Step 히스토리에 기능·비기능 요구사항이 모두 논의된 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "요구사항 간 중복·충돌 정리",
                    "우선순위 부여 (Must/Should/Could 또는 MVP 포함 여부)",
                    "요구사항 실현 가능성 재점검",
                    "요구사항 추적 체계 수립 (매트릭스 등)",
                ],
            },
        ],
    },
    {
        "stage_sequence": 4,
        "stage_name": "설계",
        "required_steps": [
            {
                "required_step_id": "4-R1",
                "required_step_name": "시스템 아키텍처 정의",
                "goal": "시스템을 구성할 주요 컴포넌트와 상호 관계를 큰 그림 수준으로 그린다.",
                "entry_criteria": "Step 히스토리에 확정된 요구사항에 대한 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "주요 구성요소 식별 (프론트·백·DB·외부 서비스 등)",
                    "구성요소 간 통신·의존 관계",
                    "아키텍처 패턴·스타일 선택 (모놀리식/3-tier 등)",
                    "요구사항의 구성요소 배분·매핑 (requirement allocation)",
                    "배포·인프라 구조의 큰 그림",
                ],
            },
            {
                "required_step_id": "4-R2",
                "required_step_name": "데이터 모델 설계",
                "goal": "시스템이 다룰 핵심 데이터 엔티티와 관계를 정의한다.",
                "entry_criteria": "Step 히스토리에 기능 요구사항과 아키텍처 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "핵심 엔티티·속성 식별",
                    "엔티티 간 관계(1:N, N:M 등) 정의",
                    "데이터 타입·제약조건 정리",
                    "저장소 선택 및 스키마 구조화 (ERD 등)",
                ],
            },
            {
                "required_step_id": "4-R3",
                "required_step_name": "인터페이스 설계",
                "goal": "외부(UI·외부 API)와 내부(컴포넌트 간) 주요 인터페이스의 모습을 정의한다.",
                "entry_criteria": "Step 히스토리에 아키텍처·데이터 모델 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "사용자 UI 구성 (와이어프레임·화면 구조 등)",
                    "API 엔드포인트·입출력 스펙",
                    "컴포넌트 간 내부 인터페이스",
                    "외부 서비스 연동 인터페이스",
                ],
            },
            {
                "required_step_id": "4-R4",
                "required_step_name": "설계 리뷰",
                "goal": "설계물이 요구사항을 충족하는지, 팀이 같은 그림을 공유하는지 점검한다.",
                "entry_criteria": "Step 히스토리에 아키텍처·데이터 모델·인터페이스 설계 맥락이 모두 존재한다.",
                "fulfillment_criteria": [
                    "요구사항과 설계 간의 매핑 점검",
                    "설계 간 불일치·누락 점검",
                    "성능·보안·확장성 관점의 설계 점검",
                    "설계 결정 사항의 적절성 점검 (기술·프레임워크 선택, 프로토타입 결과 반영, 외부 컴포넌트 활용)",
                    "리뷰 결과 반영·수정 방향 정리",
                ],
            },
        ],
    },
    {
        "stage_sequence": 5,
        "stage_name": "개발",
        "required_steps": [
            {
                "required_step_id": "5-R1",
                "required_step_name": "개발 환경 구축",
                "goal": "팀원이 동일한 환경에서 개발·빌드·실행할 수 있도록 기본 환경과 저장소를 구성한다.",
                "entry_criteria": "Step 히스토리에 기술 스택 결정과 설계 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "코드 저장소·브랜치 전략 구성",
                    "로컬 개발 환경·의존성 세팅",
                    "프로젝트 스캐폴드·초기 구조 수립",
                    "빌드·실행·배포 스크립트 기초 구성",
                ],
            },
            {
                "required_step_id": "5-R2",
                "required_step_name": "핵심 기능 구현",
                "goal": "MVP 핵심 기능을 설계에 따라 구현한다.",
                "entry_criteria": "Step 히스토리에 개발 환경 구축과 설계 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "핵심 기능별 구현 작업",
                    "공통 모듈·유틸리티 구현",
                    "데이터 처리·비즈니스 로직 구현",
                    "UI 또는 진입점(엔드포인트) 구현",
                ],
            },
            {
                "required_step_id": "5-R3",
                "required_step_name": "코드 통합",
                "goal": "개별 모듈을 하나의 실행 가능한 시스템으로 통합한다.",
                "entry_criteria": "Step 히스토리에 개별 기능·모듈 구현에 대한 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "모듈 간 연결 작업 (프론트-백-DB 등)",
                    "엔드투엔드 시나리오 연결",
                    "통합 과정의 충돌·에러 해결",
                    "통합 빌드·실행 검증",
                ],
            },
            {
                "required_step_id": "5-R4",
                "required_step_name": "코드 리뷰 및 자체 검증",
                "goal": "작성된 코드를 팀원(또는 본인)이 읽어보며 결함·나쁜 패턴·누락을 발견하고 개선한다.",
                "entry_criteria": "Step 히스토리에 핵심 기능 구현과 통합에 대한 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "코드 리뷰·피어 리뷰 활동",
                    "코딩 컨벤션·품질 점검",
                    "단위 테스트·개발자 자체 검증",
                    "발견된 결함의 수정·개선",
                ],
            },
        ],
    },
    {
        "stage_sequence": 6,
        "stage_name": "테스트 및 검증",
        "required_steps": [
            {
                "required_step_id": "6-R1",
                "required_step_name": "테스트 계획 수립",
                "goal": "Stage 3 요구사항을 어떻게 검증할지 테스트 전략과 범위를 결정한다.",
                "entry_criteria": "Step 히스토리에 통합된 시스템과 요구사항 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "테스트 대상·범위 정의",
                    "테스트 유형 선택 (기능/통합/성능/보안 등)",
                    "테스트 시나리오·케이스 설계",
                    "테스트 데이터·입력값 준비 (test database 생성·샘플 데이터셋)",
                    "테스트 환경·도구 준비",
                ],
            },
            {
                "required_step_id": "6-R2",
                "required_step_name": "테스트 수행",
                "goal": "수립한 계획에 따라 테스트를 실제로 실행하여 시스템 동작을 확인한다.",
                "entry_criteria": "Step 히스토리에 테스트 계획에 대한 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "기능 테스트 수행",
                    "통합·시나리오 테스트 수행",
                    "비기능 테스트 수행 (성능·보안·사용성 등)",
                    "테스트 결과 기록·수집",
                ],
            },
            {
                "required_step_id": "6-R3",
                "required_step_name": "결과 분석 및 결함 기록",
                "goal": "테스트 중 발견한 결함을 구조화된 형태로 기록하고 원인·심각도를 정리한다.",
                "entry_criteria": "Step 히스토리에 테스트 수행과 결과 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "결함 목록화·분류",
                    "결함 재현 방법·원인 분석",
                    "심각도·우선순위 부여",
                    "결함 수정·재테스트 계획",
                ],
            },
            {
                "required_step_id": "6-R4",
                "required_step_name": "수용 테스트/최종 검토",
                "goal": "초기 문제/기회와 요구사항이 실제로 해결되었는지, 프로젝트 목표 달성 여부를 판단한다.",
                "entry_criteria": "Step 히스토리에 결함 기록과 주요 결함 처리에 대한 맥락이 존재한다.",
                "fulfillment_criteria": [
                    "Stage 1 문제/기회 해결 여부 점검",
                    "Stage 3 핵심 요구사항 충족 여부 점검",
                    "사용자 관점의 수용 테스트·시연",
                    "프로젝트 종료 판단·회고·향후 방향",
                ],
            },
        ],
    },
]

# ---------------------------------------------------------------------------
# GENERAL_STEP_FIXTURES — 도메인: 배달 라이더 경로 최적화 앱
# Stage 1·3·6: 3 steps / Stage 2·4·5: 2 steps (총합 60 steps for 24 RS)
# ---------------------------------------------------------------------------

def _m(
    description: str,
    rec: list[tuple[str, str]],
    mistakes: list[tuple[str, str, str]],
    tip: str,
) -> dict:
    return {
        "description": description,
        "rec": rec,
        "mistakes": mistakes,
        "tip": tip,
    }


GENERAL_STEP_FIXTURES: dict[str, list[dict]] = {
    # --- Stage 1 (3 steps each) ---
    "1-R1": [
        {"name": "라이더 경로 비효율 문제 정의", "desc": "배달 라이더가 주문 묶음 처리 시 최적 경로를 수동으로 판단하는 비효율 서술"},
        {"name": "기존 대안(네이버 지도·카카오 내비) 한계 분석", "desc": "현행 내비 도구의 배달 특화 경로 최적화 부재 지점 정리"},
        {"name": "문제 임팩트 정량화", "desc": "평균 배달 시간 손실·수입 감소 추정치 산출"},
    ],
    "1-R2": [
        {
            "name": "라이더 5인 현장 인터뷰 설계",
            "desc": "주요 배달 앱(배민·쿠팡이츠) 전업 라이더 대상 반구조화 인터뷰 가이드 작성",
            "mentoring": _m(
                "실제 라이더와의 접점을 통해 현장 맥락을 포착하는 자리예요.",
                [
                    ("현장 인터뷰", "5인 이상 전업 라이더를 만나 실제 주문 처리 과정·불편 점을 직접 들어요."),
                    ("동행 관찰", "라이더가 실제 배달 중일 때 동행하며 경로 결정 순간을 관찰해요."),
                ],
                [("지인 라이더에게만 물어보기", "지인 2명에게 물어봤다.", "다양한 배달 앱·근무 시간대 라이더 5명 인터뷰")],
                "하루 피크 타임(점심·저녁) 기준 행동을 구체적으로 들어야 인사이트가 살아요.",
            ),
        },
        {"name": "라이더 행동 관찰 기록", "desc": "실제 주문 처리 중 경로 결정 순간의 행동·맥락 관찰 정리"},
        {"name": "라이더 페르소나 초안 작성", "desc": "인터뷰·관찰 결과를 바탕으로 전업 라이더·부업 라이더 2종 페르소나 작성"},
    ],
    "1-R3": [
        {
            "name": "AI 경로 최적화 컨셉 초안 작성",
            "desc": "주문 데이터·지도 API 기반 실시간 최적 경로 제안 서비스 컨셉 한 단락 정리",
            "mentoring": _m(
                "우리 서비스의 존재 이유를 한 단락에 담는 자리예요.",
                [
                    ("경쟁 매트릭스 작성", "기존 서비스 5개를 기능별로 비교하는 표를 만들어요."),
                    ("한 줄 가치 제안 초안", "\"X를 위해 Y 문제를 Z 방식으로 해결한다\" 형식으로 써보세요."),
                ],
                [("차별점 없이 기능 나열", "지도 기반 경로 표시 기능이 있다.", "경쟁 앱 대비 실시간 재계획 기능이 없다는 공백을 채운다.")],
                "가장 강한 차별점 하나를 먼저 정하고 나머지를 붙여나가세요.",
            ),
        },
        {"name": "경쟁 서비스 벤치마킹", "desc": "OptimoRoute·Road Warrior·자체 물류 앱 비교 분석"},
        {"name": "핵심 차별점 정의", "desc": "라이더 특화 단거리 다중 배송 최적화 + 실시간 재계획 기능 차별점 정리"},
    ],
    "1-R4": [
        {"name": "기술 스택 실현 가능성 검토", "desc": "React Native + FastAPI + 지도 API(Kakao/Google Maps) 구현 난이도 평가"},
        {"name": "2개월 개발 일정 타당성 검토", "desc": "4인 팀 기준 MVP 범위 내 2개월 완료 가능 여부 판단"},
        {"name": "주요 리스크 목록화", "desc": "지도 API 비용·정확도 리스크, 실시간 처리 지연 리스크 정리"},
    ],
    # --- Stage 2 (2 steps each) ---
    "2-R1": [
        {"name": "2개월 전체 마일스톤 구성", "desc": "요구사항 정의 2주 → 설계 1주 → 개발 4주 → 테스트 1주 마일스톤 배분"},
        {"name": "스프린트 단위 세부 일정 작성", "desc": "1주 단위 스프린트 8회 계획, 각 스프린트 목표 정의"},
    ],
    "2-R2": [
        {
            "name": "팀원 역할 초안 정의",
            "desc": "PM 1인·프론트 1인·백엔드/AI 2인 역할 초안 분배",
            "mentoring": _m(
                "팀의 혼선을 막으려면 역할 경계를 명확히 그어야 해요.",
                [
                    ("RACI 매트릭스 작성", "핵심 업무별 Responsible·Accountable·Consulted·Informed 정리"),
                    ("경계 시나리오 협의", "\"AI 모듈 버그가 발생하면 누가 대응?\" 같은 가장자리 상황을 미리 협의해요."),
                ],
                [("\"그냥 다 같이 한다\" 정하기", "우리 팀은 모두 풀스택이라 다 같이 한다.", "기능 영역별 주 담당자를 지정하고 리뷰 책임을 명시한다.")],
                "역할보다 책임(Accountability)이 먼저예요. 누가 최종 결정권자인지를 정해요.",
            ),
        },
        {"name": "역할 간 경계 협의", "desc": "API 계약·코드 리뷰 책임·데일리 스탠드업 규칙 확정"},
    ],
    "2-R3": [
        {"name": "기술 리스크 목록화", "desc": "지도 API 비용 초과·실시간 경로 계산 지연·AI 정확도 미달 리스크 식별"},
        {"name": "일정·인력 리스크 검토", "desc": "팀원 이탈 가능성·학기말 일정 충돌 등 일정 리스크 정리"},
    ],
    "2-R4": [
        {"name": "기술 스택 확정", "desc": "React Native(Expo) + FastAPI + PostgreSQL + Kakao Maps API 스택 확정"},
        {"name": "협업 도구 결정", "desc": "GitHub(브랜치 전략) + Notion(위키) + Discord(소통) + Linear(이슈) 확정"},
    ],
    # --- Stage 3 (3 steps each) ---
    "3-R1": [
        {"name": "라이더 인터뷰 기반 요구사항 수집", "desc": "5인 인터뷰 결과에서 핵심 불편·필요 사항 추출"},
        {"name": "유사 앱 기능 벤치마킹", "desc": "경쟁 앱의 기능 목록에서 미제공 요구사항 추출"},
        {"name": "브레인스토밍 세션 진행", "desc": "팀 4인 대상 30분 브레인스토밍 → 요구사항 후보 32개 수집"},
    ],
    "3-R2": [
        {
            "name": "핵심 기능 명세화",
            "desc": "경로 최적화 요청·실시간 경로 재계획·주문 리스트 관리 기능 스펙 작성",
            "mentoring": _m(
                "기능 요구사항은 \"사용자가 무엇을 할 수 있는가\"를 기준으로 써야 해요.",
                [
                    ("유저스토리 형식 사용", "\"라이더로서, 주문 3개를 묶어 최적 경로를 받고 싶다\" 형식으로 작성"),
                    ("MVP 기준 분류", "Must Have·Should Have·Could Have로 기능을 분류해 범위를 관리해요."),
                ],
                [("기술 관점으로 쓰기", "알고리즘이 TSP를 사용한다.", "라이더가 주문 추가 시 경로가 자동으로 재계획된다.")],
                "기능 하나당 검증 기준(Acceptance Criteria) 1줄이 없으면 아직 명세가 아니에요.",
            ),
        },
        {"name": "유저스토리 작성", "desc": "라이더 페르소나 기준 12개 유저스토리 작성"},
        {"name": "기능 우선순위 결정", "desc": "MVP Must/Should/Could 분류 — Must 7개, Should 4개, Could 5개"},
    ],
    "3-R3": [
        {"name": "성능 요구사항 정의", "desc": "경로 계산 응답 시간 3초 이내, 동시 접속 100명 이상 처리 목표 정의"},
        {"name": "보안 요구사항 정의", "desc": "라이더 위치 데이터 암호화·JWT 인증 요구사항 정의"},
        {"name": "사용성 요구사항 정의", "desc": "이동 중 한 손 조작 가능한 UI·글자 크기·터치 영역 기준 정의"},
    ],
    "3-R4": [
        {"name": "요구사항 중복·충돌 정리", "desc": "기능/비기능 요구사항 간 중복 제거 및 충돌 해결 — 3건 통합"},
        {"name": "요구사항 추적 매트릭스 작성", "desc": "요구사항 ID ↔ 기능 ↔ 테스트 케이스 매핑 표 초안 작성"},
        {"name": "팀 리뷰 미팅 진행", "desc": "4인 팀 전원 대상 요구사항 최종 검토 미팅 및 확정"},
    ],
    # --- Stage 4 (2 steps each) ---
    "4-R1": [
        {
            "name": "구성요소 다이어그램 초안 작성",
            "desc": "Mobile App → API Gateway → FastAPI → AI 최적화 모듈 → DB + Kakao Maps API 구성도 작성",
            "mentoring": _m(
                "아키텍처 결정은 나중에 바꾸기 어려운 것들이에요 — 지금이 제일 중요한 자리예요.",
                [
                    ("C4 모델 1·2단계 그리기", "Context → Container 다이어그램 수준으로 큰 그림을 그려요."),
                    ("아키텍처 결정 기록(ADR)", "\"왜 Lambda를 선택했는가\" 같은 결정 이유를 짧게 기록해요."),
                ],
                [("기술 하나를 먼저 정하고 아키텍처 맞추기", "Lambda가 트렌디해서 Lambda로 간다.", "요구사항(트래픽 규모·응답 시간)을 먼저 보고 인프라를 결정한다.")],
                "지금 결정이 3개월 후 이분기를 만든다는 것을 염두에 두고 결정해요.",
            ),
        },
        {"name": "AWS 서버리스 배포 구조 확정", "desc": "Lambda + API Gateway + RDS(PostgreSQL) + S3 구조 확정 및 ARN 설계"},
    ],
    "4-R2": [
        {"name": "핵심 엔티티 식별", "desc": "Rider·Order·RouteOptimization·Waypoint 엔티티 식별 및 주요 속성 정의"},
        {"name": "ERD 초안 작성", "desc": "엔티티 간 관계(Rider 1:N Order, Order N:M Waypoint) 정의 및 ERD 작성"},
    ],
    "4-R3": [
        {"name": "주요 화면 와이어프레임 작성", "desc": "메인 지도 화면·주문 목록·경로 결과 화면 와이어프레임 Figma 작성"},
        {"name": "REST API 엔드포인트 명세", "desc": "경로 최적화 요청·주문 조회·라이더 위치 업데이트 API 스펙 OpenAPI 3.0 작성"},
    ],
    "4-R4": [
        {"name": "설계 검토 회의 진행", "desc": "아키텍처·ERD·와이어프레임 팀 리뷰 실시, 불일치 항목 5건 정리"},
        {"name": "설계 반영 수정 완료", "desc": "리뷰 결과 기반 API 스펙·ERD 수정 — Waypoint 테이블 인덱스 추가 포함"},
    ],
    # --- Stage 5 (2 steps each) ---
    "5-R1": [
        {"name": "GitHub 저장소·브랜치 전략 설정", "desc": "mono-repo 구조 + feature 브랜치 전략 설정, GitHub Actions CI 초기 구성"},
        {"name": "로컬 개발 환경 세팅 문서 작성", "desc": "팀원별 로컬 환경 세팅 가이드(Poetry + Expo + Docker Compose) 작성"},
    ],
    "5-R2": [
        {
            "name": "경로 최적화 모듈 구현",
            "desc": "TSP 근사 알고리즘 + Kakao Maps Directions API 연동 최적 경로 계산 모듈 구현",
            "mentoring": _m(
                "핵심 기능 구현 단계에서 범위 팽창(scope creep)이 가장 위험해요.",
                [
                    ("가장 어려운 부분 먼저 구현", "경로 최적화 알고리즘처럼 불확실한 핵심을 먼저 구현해 리스크를 줄여요."),
                    ("기능 플래그로 미완성 격리", "미완성 기능은 피처 플래그로 비활성화하고 메인 브랜치에 통합해요."),
                ],
                [("UI 먼저 완성하고 백엔드 연결하기", "화면이 다 만들어진 다음에 API 연결하면 된다.", "핵심 API 인터페이스를 먼저 정의하고 프론트-백이 병렬로 개발한다.")],
                "오늘 구현한 코드가 내일 리뷰 받을 수 있는가를 매일 확인해요.",
            ),
        },
        {"name": "백엔드 API 엔드포인트 구현", "desc": "경로 최적화 요청·주문 관리 FastAPI 엔드포인트 구현 (pytest 커버리지 82%)"},
    ],
    "5-R3": [
        {"name": "프론트-백엔드 API 연동", "desc": "앱 ↔ FastAPI 간 경로 요청·응답 E2E 연동 완료"},
        {"name": "통합 빌드·실행 검증", "desc": "Docker Compose 환경에서 전체 시스템 통합 실행 검증 — 주요 시나리오 3개 통과"},
    ],
    "5-R4": [
        {"name": "PR 코드 리뷰 실시", "desc": "핵심 기능 PR 4개 팀원 교차 리뷰 완료, 지적 사항 12건 수정"},
        {"name": "단위 테스트 작성 및 실행", "desc": "경로 최적화 모듈 + API 엔드포인트 단위 테스트 87% 커버리지 달성"},
    ],
    # --- Stage 6 (3 steps each) ---
    "6-R1": [
        {"name": "테스트 전략 문서 작성", "desc": "기능/통합/성능 테스트 범위·유형·도구 선정 문서 작성"},
        {"name": "테스트 케이스 설계", "desc": "주요 유저스토리 12개 기반 TC 36개 작성"},
        {"name": "테스트 데이터 준비", "desc": "실제 서울 시내 배달 경로 샘플 데이터셋 30건 준비"},
    ],
    "6-R2": [
        {
            "name": "기능 테스트 실행",
            "desc": "TC 36개 기능 테스트 실행, 34건 PASS 2건 FAIL 기록",
            "mentoring": _m(
                "테스트는 \"버그 찾기\"가 아니라 \"시스템 동작 이해\"예요.",
                [
                    ("경계값 테스트 우선", "주문 0건·1건·최대 수량 등 경계 조건을 먼저 테스트해요."),
                    ("실제 GPS 데이터로 테스트", "가상 좌표가 아닌 실제 서울 배달 경로 데이터로 최적화 결과를 검증해요."),
                ],
                [("정상 케이스만 테스트", "앱이 잘 되는 경우만 테스트했다.", "네트워크 오류·빈 주문 목록·GPS 없음 등 예외 상황을 포함한다.")],
                "테스트 결과보다 테스트 중 발견한 질문(\"이 상황에서 앱은 뭘 해야 하나?\")이 더 중요해요.",
            ),
        },
        {"name": "성능 테스트 실행", "desc": "경로 최적화 API 100 동시 요청 부하 테스트, 평균 응답 2.1초 확인"},
        {"name": "비기능 테스트 결과 수집", "desc": "보안 취약점 스캔(bandit) + 접근성 검사(axe) 결과 수집·기록"},
    ],
    "6-R3": [
        {"name": "결함 목록화 및 분류", "desc": "발견 결함 2건 (경로 재계획 오류·빈 주문 목록 처리 누락) 심각도 분류"},
        {"name": "결함 수정 완료", "desc": "2건 결함 수정·재테스트 완료 확인 — TC 36개 전부 PASS"},
        {"name": "결함 원인 분석 보고서 작성", "desc": "경로 재계획 오류의 근본 원인(Kakao API null 응답 미처리) 분석 문서 작성"},
    ],
    "6-R4": [
        {"name": "라이더 5인 수용 테스트 실시", "desc": "실제 라이더 대상 앱 시연·사용성 테스트, 만족도 4.2/5.0"},
        {"name": "프로젝트 목표 달성 최종 점검", "desc": "Stage 1 문제(경로 비효율) 해결·Stage 3 핵심 요구사항 충족 여부 최종 확인"},
        {"name": "프로젝트 회고 및 향후 방향 정리", "desc": "팀 KPT 회고 진행, 다음 버전 로드맵(실시간 배차 연동·수익 분석) 초안 작성"},
    ],
}

# ---------------------------------------------------------------------------
# 8개 케이스 정의 (stage_indices는 0-based)
# ---------------------------------------------------------------------------

CASES: list[tuple[str, list[int]]] = [
    ("case01_stage1_only",        [0]),
    ("case02_stage1_2",           [0, 1]),
    ("case03_stage1_2_3",         [0, 1, 2]),
    ("case04_stage1_2_3_4",       [0, 1, 2, 3]),
    ("case05_stage1_2_3_4_5",     [0, 1, 2, 3, 4]),
    ("case06_stage1_to_6_full",   [0, 1, 2, 3, 4, 5]),
    ("case07_stage6_only",        [5]),
    ("case08_stage1_and_4_skip",  [0, 3]),
]

# ---------------------------------------------------------------------------
# 헬퍼 함수 — AcceptedStepForAI / MentoringContent 생성
# ---------------------------------------------------------------------------


def _make_mentoring(m: dict) -> MentoringContent:
    return MentoringContent(
        description=m["description"],
        recommended_methods=[
            RecommendedMethod(title=t, content=c) for t, c in m["rec"]
        ],
        common_mistakes=[
            CommonMistake(mistake=mt, bad_example=b, good_example=g)
            for mt, b, g in m["mistakes"]
        ],
        one_line_tip=m["tip"],
    )


def _make_accepted_step(step_dict: dict) -> AcceptedStepForAI:
    mentoring: Optional[MentoringContent] = None
    if "mentoring" in step_dict:
        mentoring = _make_mentoring(step_dict["mentoring"])
    return AcceptedStepForAI(
        name=step_dict["name"],
        description=step_dict["desc"],
        sidepanel_mentoring=mentoring,
    )


# ---------------------------------------------------------------------------
# build_input — DesignExportInput 생성
# ---------------------------------------------------------------------------


def build_input(stage_indices: list[int]) -> DesignExportInput:
    """stage_indices (0-based)로 선택된 Stage들의 RS를 펼쳐 DesignExportInput을 만든다."""
    project_context = ProjectContextForAI(**PROJECT_INFO_DICT)

    selected_required_steps: list[RequiredStepForAI] = []
    for idx in stage_indices:
        stage = STAGE_DEFINITIONS[idx]
        for rs_def in stage["required_steps"]:
            rs_id = rs_def["required_step_id"]
            step_dicts = GENERAL_STEP_FIXTURES.get(rs_id, [])
            accepted_steps = [_make_accepted_step(s) for s in step_dicts]
            selected_required_steps.append(
                RequiredStepForAI(
                    required_step_id=rs_id,
                    required_step_name=rs_def["required_step_name"],
                    goal=rs_def["goal"],
                    fulfillment_criteria=rs_def["fulfillment_criteria"],
                    accepted_general_steps=accepted_steps,
                )
            )

    return DesignExportInput(
        project_context=project_context,
        selected_required_steps=selected_required_steps,
    )


# ---------------------------------------------------------------------------
# 백엔드 Design_Export_Renderer 흉내 함수
# ---------------------------------------------------------------------------

_STAGE_SEQ_TO_NAME: dict[int, str] = {
    s["stage_sequence"]: s["stage_name"] for s in STAGE_DEFINITIONS
}


def render_design_export_md(
    input_data: DesignExportInput,
    ai_output: DesignExportOutput,
    *,
    stage_definitions: list[dict],
    general_step_fixtures: dict[str, list[dict]],
    generated_at: datetime,
) -> str:
    """백엔드 Design_Export_Renderer 흉내 — 최종 .md 본문 렌더링.

    골격 (자기소개 블록쿼터·프로젝트 컨텍스트·RS 헤더·목표·충족 기준·진행한 결정·푸터)
    을 직접 박고, AI 출력(questions_per_rs, core_summary)을 끼워넣어 완성.
    """
    seq_to_name: dict[int, str] = {
        s["stage_sequence"]: s["stage_name"] for s in stage_definitions
    }

    ctx = input_data.project_context
    constraints_str = (
        ", ".join(ctx.constraints) if ctx.constraints else "(미입력)"
    )

    # AI 출력 인덱싱 (required_step_id → RSQuestions)
    rs_q_map: dict[str, RSQuestions] = {}
    for rs_q in ai_output.questions_per_rs:
        rs_q_map[rs_q.required_step_id] = rs_q

    # RS를 Stage 단위로 그룹화 (입력 순서 보존)
    seen_stage_seqs: list[int] = []
    stage_rs_map: dict[int, list[RequiredStepForAI]] = {}
    for rs in input_data.selected_required_steps:
        seq = int(rs.required_step_id.split("-")[0])
        if seq not in seen_stage_seqs:
            seen_stage_seqs.append(seq)
            stage_rs_map[seq] = []
        stage_rs_map[seq].append(rs)

    lines: list[str] = []

    # --- 제목 ---
    lines.append(f"# {ctx.name or '(이름 미설정)'} — 사고 궤적 문서")
    lines.append("")

    # --- 자기소개 블록쿼터 ---
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
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- 프로젝트 컨텍스트 ---
    lines.append("## 프로젝트 컨텍스트")
    lines.append("")
    lines.append(f"- 프로젝트 이름: {ctx.name or '(미입력)'}")
    lines.append(f"- 인원·기간: {ctx.member_count}명 / {ctx.duration_months}개월")
    lines.append(f"- 제약사항: {constraints_str}")
    lines.append(f"- 초기 아이디어: {ctx.initial_prompt}")
    lines.append("")

    # --- 사고 궤적 ---
    lines.append("## 사용자가 거쳐온 사고 궤적")
    lines.append("")

    for stage_seq in seen_stage_seqs:
        stage_name = seq_to_name.get(stage_seq, f"Stage {stage_seq}")
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

            # 진행한 결정
            lines.append("**진행한 결정** (사용자 클릭 순서):")
            if rs.accepted_general_steps:
                for i, step in enumerate(rs.accepted_general_steps, start=1):
                    lines.append(f"{i}. {step.name}")
            else:
                lines.append("(아직 없음)")
            lines.append("")

            # AI 생성 질문
            lines.append("**이 단계에서 인지한 What·Why 질문**:")
            rs_q = rs_q_map.get(rs.required_step_id)
            if rs_q:
                for q in rs_q.questions:
                    lines.append(f"- {q}")
            else:
                lines.append("- (질문 생성 실패 — ID 매칭 오류)")
                print(f"[WARN] questions_per_rs에서 {rs.required_step_id} 미발견", file=sys.stderr)
            lines.append("")

    # --- 핵심 What·Why 정리 ---
    lines.append("## 핵심 What·Why 정리")
    lines.append("")
    for item in ai_output.core_summary:
        lines.append(f"- {item}")
    lines.append("")

    # --- 푸터 ---
    lines.append("---")
    lines.append("")
    lines.append(f"생성: {generated_at:%Y-%m-%d %H:%M} (KST) / 도구: Poco")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 출력 헬퍼
# ---------------------------------------------------------------------------


def _hr(char: str = "═", width: int = 59) -> None:
    print(char * width)


def _section(title: str) -> None:
    print()
    _hr()
    print(f"  {title}")
    _hr()


# ---------------------------------------------------------------------------
# 케이스 실행
# ---------------------------------------------------------------------------


async def _run_case(
    label: str,
    stage_indices: list[int],
    model_id: str,
    bedrock: Any,
    out_dir: Path,
) -> dict:
    _section(label)

    input_data = build_input(stage_indices)
    n_rs = len(input_data.selected_required_steps)
    n_acc = sum(len(rs.accepted_general_steps) for rs in input_data.selected_required_steps)
    n_stages = len(stage_indices)

    print(f"  Stage 수      : {n_stages}")
    print(f"  Required_Step : {n_rs}개 / accepted_general_steps : {n_acc}개")

    generated_at = datetime.now(timezone.utc).replace(microsecond=0)

    t_start = time.perf_counter()
    error_msg: Optional[str] = None
    result: Optional[DesignExportOutput] = None

    try:
        result = await generate_design_export(
            input_data=input_data,
            bedrock_runtime_client=bedrock,
            model_id=model_id,
        )
    except Exception as exc:
        error_msg = f"{type(exc).__name__}: {exc}"

    elapsed = time.perf_counter() - t_start

    if error_msg or result is None:
        print(f"  응답 시간     : {elapsed:.2f}s")
        print(f"  ❌ FAIL — {error_msg}")
        return {
            "label": label,
            "elapsed": elapsed,
            "ai_chars": 0,
            "md_len": 0,
            "status": "FAIL",
            "error": error_msg,
        }

    # AI 응답 크기 추정 (questions + core_summary 전체 글자 수)
    ai_text = "".join(q for rs_q in result.questions_per_rs for q in rs_q.questions)
    ai_text += "".join(result.core_summary)
    ai_chars = len(ai_text)
    ai_tokens_est = ai_chars // 4

    # 최종 .md 렌더
    md = render_design_export_md(
        input_data,
        result,
        stage_definitions=STAGE_DEFINITIONS,
        general_step_fixtures=GENERAL_STEP_FIXTURES,
        generated_at=generated_at,
    )
    md_len = len(md)

    # 저장
    out_path = out_dir / f"{label}.md"
    out_path.write_text(md, encoding="utf-8")

    print(f"  응답 시간     : {elapsed:.2f}s")
    print(f"  AI 응답 토큰 추정 : ~{ai_tokens_est} (questions_per_rs + core_summary 글자 합 / 4)")
    print(f"  최종 .md 길이 : {md_len}자")
    print(f"  ✅ PASS — out/{label}.md 저장됨")

    return {
        "label": label,
        "elapsed": elapsed,
        "ai_chars": ai_chars,
        "ai_tokens_est": ai_tokens_est,
        "md_len": md_len,
        "status": "PASS",
        "error": None,
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


async def _main() -> None:
    region = os.environ.get("AWS_REGION", "us-east-1")
    model_id = os.environ.get("MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
    bedrock = boto3.client("bedrock-runtime", region_name=region)

    out_dir = _HERE / "out"
    out_dir.mkdir(exist_ok=True)

    _section("Poco design-export 자동 러너 (v1.4 Z+)")
    print(f"  AWS_REGION : {region}")
    print(f"  MODEL_ID   : {model_id}")
    print(f"  총 케이스  : {len(CASES)}개")

    results: list[dict] = []
    for i, (label, stage_indices) in enumerate(CASES):
        r = await _run_case(label, stage_indices, model_id, bedrock, out_dir)
        results.append(r)
        if i < len(CASES) - 1:
            time.sleep(1)  # rate limit 대비

    # 전체 요약
    _section("전체 요약")
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    fail_count = len(results) - pass_count

    for r in results:
        if r["status"] == "PASS":
            t_str = f"{r['elapsed']:.1f}s"
            tok_str = f"AI≈{r['ai_tokens_est']}t"
            md_str = f".md={r['md_len']}자"
            print(f"  ✅ {r['label']:<35} {t_str:<8} {tok_str:<12} {md_str}")
        else:
            print(f"  ❌ {r['label']:<35} FAIL: {r['error']}")

    print()
    print(f"총 {len(results)}개 중 {pass_count}개 PASS, {fail_count}개 FAIL")
    print(f"각 케이스 .md 본문은 out/ 디렉토리에 저장됨.")


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
