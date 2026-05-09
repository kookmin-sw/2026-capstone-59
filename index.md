---
layout: default
title: Poco
---

<p align="center">
  <img src="./assets/logo.png" alt="Poco 로고" width="420" />
</p>

### *조금씩, 한 걸음씩 — 아이디어를 설계까지 쌓아가는 사고의 캔버스*

> **AI가 다 만들어주는 시대,**
> **무엇을, 왜 만들지 정의하고 계신가요?**

[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?logo=github)](https://github.com/kookmin-sw/2026-capstone-59)
[![AWS Track](https://img.shields.io/badge/Capstone_2026-AWS_Track_59팀-FF9900?logo=amazon-aws)](#team)

<!-- TODO: 완성 후 포스터 이미지 및 소개 영상 embed 자리 -->
<!--
![포스터](./assets/poster.png)
[소개 영상](https://...)
-->

---

## 📑 목차

1. [프로젝트 소개](#1-프로젝트-소개)
2. [문제 정의](#2-문제-정의)
3. [해결 방법 — Top 3 핵심 기능](#3-해결-방법--top-3-핵심-기능)
4. [기술 설계](#4-기술-설계)
5. [데이터와 확장 가능성](#5-데이터와-확장-가능성)
6. [소프트웨어 방법론 근거](#6-소프트웨어-방법론-근거)
7. [팀 소개](#7-팀-소개)
8. [레포지토리 탐색 가이드](#8-레포지토리-탐색-가이드)
9. [사용법](#9-사용법)

---

## 1. 프로젝트 소개

### 한 줄 요약

> 서비스를 만들고 싶은 사람이 **'AI에게 무엇을 시켜야 하는지'** 부터 체계적으로 정리할 수 있도록, AI가 다음 할 일의 선택지를 제시하고 의사결정의 궤적을 **트리로 시각화**해주는 **사고의 캔버스**.

### 세 줄 요약

> 만들고 싶은 건 있는데 어디서부터 정리해야 할지 모를 때, AI가 **문제 정의부터 다음 할 일을 단계별로 추천**하고 그 과정을 트리 형태로 시각화해주는 사고의 캔버스.
>
> 각 단계마다 **용어 설명·멘토링·템플릿**을 제공해서, 기획 경험이 없어도 **검증된 소프트웨어 개발 프로세스**를 자연스럽게 따라갈 수 있다.
>
> **"어떤 결정을 해왔고, 지금 어디까지 왔는지"** 가 캔버스 위에 트리로 뻗어나가며 한눈에 정리된다.

### 핵심 가치

AI가 엄청난 속도로 모든 것을 만들어주는 시대, 진짜 경쟁력은 이 한 문장으로 요약된다.

> **"무엇을(What) 왜(Why) 만들지 스스로 정의하는 능력"**

AI는 **"어떻게(How)"** 를 엄청난 속도로 만들어준다. 코드도, 디자인도, 문서도. 그러나 AI가 하지 못하는 것이 있다. 바로 *"무엇을·왜 만들어야 하는가"* 를 사용자 대신 결정해주는 것. Poco는 사용자가 그 영역을 구조적으로 수행할 수 있도록 돕는다.

### 소개 영상

<!-- TODO: 완성 후 소개 영상 임베드 -->
> *영상 준비 중입니다.*

---

## 2. 문제 정의

> 💡 **평가 기준 대응:** 문제 정의의 타당성 (15점) — Pain Point의 구체성, 기존 방식의 한계, 해결 필요성  
> 💡 **체크포인트 대응:** (1) 프로젝트 목적 · (2) 타겟 사용자 · (3) AI 챗봇으로 대체 가능한가

### 2-1. 타겟 사용자

**소프트웨어 프로젝트를 "처음부터 끝까지 스스로 설계해봐야 하는" 사람.**

대표적으로 **캡스톤·사이드 프로젝트를 시작하는 개인 또는 2~6명 규모의 소규모 팀**이다. 만들고 싶은 것은 어렴풋이 있지만, *무엇을 어떤 순서로 정의해야 하는지*에 대한 체계적 경험이 아직 쌓이지 않은 상태.

특히 **AI 시대에 기능 구현(How)은 점점 쉬워지지만, 정작 "무엇을·왜 만들지(What·Why)"를 스스로 정리해본 적이 없어** AI에게 좋은 질문을 던지는 데 어려움을 겪는 사람들이다.

### 2-2. 실제로 겪는 Pain Point

> *"AI한테 뭐라도 시켜보려는데… 정작 내가 뭘 만들고 싶은 건지부터 모르겠다.*  
> *용어도 어렵고, 빠뜨린 단계는 없는지 불안하고, 사람들에게 '왜 이 결정을 했는지' 설명할 자신도 없다."*

뭔가 만들고 싶은데 **"문제 정의 → 요구사항 → 설계 → 개발 → 테스트"** 로 이어지는 흐름을 모른다. 막연한 상태든, 어느 정도 구체화된 상태든 **"다음에 뭘 해야 하는지"** 가 안 보인다.

### 2-3. 기존 방식의 한계

| 구분 | 한계 |
|---|---|
| **Jira / Notion** | 할 일을 *관리*해주지만, **"뭘 해야 하는지" 자체를 알려주지는 않는다.** |
| **방법론 문서 (SWEBOK, PMBOK)** | 내용은 체계적이지만 **딱딱해서 초심자가 읽기 어렵다.** |
| **일반 AI 챗봇** | 질문을 잘 던져야 좋은 답을 주는데, **"어떤 질문을 해야 할지 모르는 사람"** 에게는 진입 장벽이 크다. |
| **팀 협업 시** | *"뭘 만들기로 했는지, 왜 이 결정을 했는지"* 가 정리되지 않아 방향이 흐트러지고, 과정이 텍스트로만 남아 **전체 흐름을 한눈에 보기 어렵다.** |

### 2-4. AI 챗봇으로 대체 가능한가?

> 💡 **체크포인트 3 정면 대응**

**대체 불가능하다.** 이유는 세 가지.

1. **"선택지 제시형" 구조의 차별성**
   일반 AI 챗봇은 **사용자가 질문을 던져야** 답한다. 그러나 초심자는 *"무엇을 질문해야 하는지"* 부터 모른다. Poco는 사용자가 질문을 짜내지 않아도 되도록, **AI가 다음 할 일의 선택지 3개를 먼저 제시**한다. 사용자는 *"가장 공감되는 것을 클릭"* 만 하면 된다.

2. **"의사결정 궤적의 시각화"**
   챗봇의 대화는 선형 텍스트로만 남아 **이전 결정으로 되돌아가거나 다른 경로를 탐색하기 어렵다.** Poco는 모든 선택을 **캔버스 위 트리 구조**로 시각화하고, 분기점으로 자유롭게 돌아가 다시 AI 추천을 받을 수 있다.

3. **"검증된 방법론 기반의 안내"**
   챗봇은 매번 답이 흔들릴 수 있다. Poco는 **DOJ SDLC + SWEBOK + 자체 제작 가이드**를 RAG 파이프라인으로 엮어, 모든 단계의 안내가 **일관된 방법론의 근거 위에서** 제공된다. *"이 단계에서 이걸 왜 하는지"* 에 대해 항상 같은 학술적 근거를 가진다.

---

## 3. 해결 방법 — Top 3 핵심 기능

### ① AI 기반 Step Flow 생성

프로젝트 맥락에 맞춰, AI가 다음 한 걸음을 실시간 제안한다. 검증된 소프트웨어 개발 방법론의 **6단계 프로세스**를 따라 캔버스 위 노드가 동적으로 뻗어나가며, 각 단계의 **핵심 관문**은 특별한 형태의 노드(다이아몬드)로 자연스럽게 나타난다.

> *— 막연함을 "다음 한 걸음"으로 바꾼다.*

### ② Step별 클릭 어시스턴트

노드를 클릭하면, 해당 단계의 **멘토링과 용어 사전**이 사이드패널로 펼쳐진다. 핵심 관문에 도달하면 **전문가가 설계한 노션 템플릿**이 바로 열려, 경험이 없어도 사고 흐름을 그대로 따라갈 수 있다.

> *— 딱딱한 방법론 문서 대신, 맥락에 맞는 가이드가 곁에 있다.*

### ③ Footprint — 의사결정 궤적

아이디어가 흔들려도 괜찮다. 이전 분기점으로 돌아가면, AI가 바뀐 맥락에 맞춰 **새로운 길을 다시 제안**한다. 선택의 궤적이 캔버스에 그대로 남아, 프로젝트가 끝날 때쯤엔 **"무엇을 왜 만들었는지"** 를 스스로 설명할 수 있게 된다.

> *— 되돌아갈 수 있는 선택, 자산으로 남는 사고 과정.*

---

## 4. 기술 설계

> 💡 **평가 기준 대응:** 기술 설계 및 활용 (25점) — 기술 선택·조합의 적합성, 아키텍처 설계의 근거  
> 💡 **체크포인트 대응:** (4) 백엔드의 AI 의존도와 프론트엔드 등의 차별화된 기여

### 4-1. AWS 서버리스 중심 아키텍처

<!-- 이미지 파일(`assets/architecture.png`) 업로드 후 아래 이미지가 자동 표시됩니다. -->
<img src="./assets/architecture.png" alt="Poco System Architecture" onerror="this.style.display='none'; document.getElementById('arch-placeholder').style.display='block';" />
<div id="arch-placeholder" style="display:none; padding:2rem; background:#f6f8fa; border:1px dashed #d0d7de; border-radius:6px; text-align:center; color:#57606a;">
  📐 아키텍처 다이어그램 준비 중입니다.
</div>

> *RAG 파이프라인과 "단기 기억 · 장기 지식" 분리 설계로, AI가 검증된 방법론을 실시간 참조합니다.*

### 4-2. 설계 철학 — "단기 기억 · 장기 지식" 분리

| 구분 | 역할 | 저장소 |
|---|---|---|
| **단기 기억 (Short-term)** | 프로젝트별 상태, Step 히스토리, 사용자 선택 궤적 | **Amazon RDS PostgreSQL** |
| **장기 지식 (Long-term)** | DOJ SDLC, SWEBOK, 자체 제작 가이드의 임베딩 | **Amazon S3 Vectors + Bedrock Knowledge Base** |

이 분리 설계가 왜 중요한가? 프로젝트마다 *상태*는 매 요청마다 갱신되지만, *방법론 지식*은 거의 변하지 않는다. 변경 빈도와 접근 패턴이 **완전히 다른 두 층**을 하나의 DB에 섞으면 확장성과 비용 효율이 모두 나빠진다. 그래서 저장소부터 구조적으로 분리하여, **지식은 한 번만 인덱싱하고 여러 프로젝트가 공유**하도록 했다.

### 4-3. 기술 스택

**Frontend**

![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)

**Backend & AI**

![Python](https://img.shields.io/badge/Python_3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic_v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest_+_Hypothesis-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)

**AWS (서버리스 중심)**

![AWS Lambda](https://img.shields.io/badge/AWS_Lambda-FF9900?style=for-the-badge&logo=awslambda&logoColor=white)
![Amazon API Gateway](https://img.shields.io/badge/API_Gateway-FF4F8B?style=for-the-badge&logo=amazonapigateway&logoColor=white)
![Amazon RDS](https://img.shields.io/badge/Amazon_RDS-527FFF?style=for-the-badge&logo=amazonrds&logoColor=white)
![Amazon S3](https://img.shields.io/badge/Amazon_S3-569A31?style=for-the-badge&logo=amazons3&logoColor=white)
![Amazon Bedrock](https://img.shields.io/badge/Amazon_Bedrock-222F3E?style=for-the-badge&logo=amazonaws&logoColor=white)
![AWS CloudWatch](https://img.shields.io/badge/CloudWatch-FF4F8B?style=for-the-badge&logo=amazoncloudwatch&logoColor=white)

**Database & Storage**

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![S3 Vectors](https://img.shields.io/badge/S3_Vectors-569A31?style=for-the-badge&logo=amazons3&logoColor=white)

**AI · RAG**

![Claude](https://img.shields.io/badge/Claude_Haiku_4.5-D97757?style=for-the-badge&logo=anthropic&logoColor=white)
![Bedrock KB](https://img.shields.io/badge/Bedrock_Knowledge_Base-222F3E?style=for-the-badge&logo=amazonaws&logoColor=white)

**External**

![Notion API](https://img.shields.io/badge/Notion_API-000000?style=for-the-badge&logo=notion&logoColor=white)

**DevOps**

![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

### 4-4. 레이어별 아키텍처 요약

| 레이어 | 기술 |
|---|---|
| **Frontend** | React SPA, S3 Static Website Hosting |
| **API Gateway** | Amazon API Gateway (HTTP API) |
| **Backend** | FastAPI (Python 3.13) on AWS Lambda (Mangum) |
| **AI Orchestrator** | 별도 Lambda, Amazon Bedrock Claude (Haiku 4.5) |
| **RAG** | Amazon Bedrock Knowledge Base + S3 Vectors |
| **DB** | Amazon RDS PostgreSQL (단일 인스턴스) |
| **External** | Notion API (템플릿 페이지 생성, Write only) |
| **Monitoring** | Amazon CloudWatch |

### 4-5. 백엔드의 AI 의존도와 기여점 (체크포인트 4 대응)

> **질문:** "백엔드에서 AI에 의존하는가? 그렇다면 프론트엔드 등 다른 부분에서 더 좋아진 것은?"

**AI 의존 범위 (정확히 명시)**

| AI가 담당하는 일 | AI가 담당하지 **않는** 일 |
|---|---|
| 다음 Step 3개 동적 생성 (`generate`) | 6개 Stage 정의 (백엔드 DB에 고정) |
| 필수 Step 충족 판단 (`accept`) | 24개 필수 Step의 목표·진입·충족 기준 정의 (팀 자체 정의) |
| 사이드패널 멘토링·용어 생성 (`side_panel`, 일반 Step만) | 필수 Step 사이드패널 콘텐츠 (팀 자체 제작, DB 사전 저장) |
| — | 필수 Step 노션 템플릿 (팀 자체 제작) |
| — | Stage 진행 판단 (규칙 기반, AI 호출 없음) |

즉 **AI는 "동적 생성이 필요한 3개 시나리오"에만 한정**되고, 나머지는 모두 사전 정의된 자산·규칙 기반으로 돌아간다. AI가 뱉어낸 결과물을 그대로 노출하는 것이 아니라, **팀이 설계한 구조(Stage·필수 Step·충족 기준)의 틀 안에서 작동**하도록 제약했다.

**프론트엔드/UX의 차별화된 기여**

1. **캔버스 기반 트리 시각화** — 기존 챗봇의 선형 대화와 달리, 사용자의 **의사결정 궤적**을 분기·롤백 가능한 시각적 구조로 제공한다. 이것은 AI가 아닌 **프론트엔드의 상호작용 설계**의 몫이다.
2. **핵심 관문 노드(다이아몬드)의 UX** — *"필수 Step"* 이라는 용어를 사용자에게 노출하지 않고, **특별한 형태의 노드**로만 인식되도록 설계. 체계적 방법론을 따라가고 있다는 감각을 자연스럽게 형성한다.
3. **사이드패널 탭 구조** — Mentoring / Dictionary / Template 세 탭을 하나의 사이드패널로 통합하여, **클릭 한 번의 확장감**을 UX적으로 구현.
4. **Footprint 시각화** — 롤백·재탐색이 캔버스 위에서 직관적으로 이루어지도록, 선택의 궤적을 **시간이 아닌 공간(트리)** 에 남기는 방식을 채택.

---

## 5. 데이터와 확장 가능성

> 💡 **평가 기준 대응:** 실용성·확장 가능성 (15점)  
> 💡 **체크포인트 대응:** (5) 수집 정보의 가치 · (6) 프로젝트 규모의 적절성

### 5-1. 서비스가 축적하는 데이터와 가치

**수집되는 정보**

| 데이터 | 성격 |
|---|---|
| **사용자 행동** | 어떤 노드에서 많이 막히는지(이탈 지점), 어떤 선택지를 많이 고르는지, 어떤 분기에서 롤백하는지 |
| **기획 결과** | 어떤 노드 선택으로 프로젝트를 마무리했는지, 어떤 주제·도메인 프로젝트가 많이 기획되는지, 많이 선택된 노드 조합 |
| **AI 성능 피드백** | AI가 생성한 Step 중 실제로 Accept된 비율, 어떤 RAG 검색 결과가 실제 선택으로 이어졌는지 |

**예상 가치**

- **교육 자산화** — 초심자가 **어디에서 멈추는지**가 데이터로 남으면, 개발 교육 커리큘럼의 취약점을 정량적으로 보완할 수 있다.
- **방법론 개선 루프** — DOJ SDLC·SWEBOK의 **이론과 실제 사용 패턴 차이**를 데이터로 관찰하여, 자체 제작 가이드 문서를 지속 개선할 수 있다.
- **AI 프롬프트·RAG 품질 개선** — 실제 Accept된 Step의 맥락을 분석하여, 동적 생성 AI의 프롬프트와 RAG 검색 전략을 데이터 기반으로 튜닝한다.

### 5-2. 확장 가능성

- **도메인 확장**: 현재는 소프트웨어 프로젝트 대상이지만, **검증된 방법론 + Stage/Step 정의서 + 템플릿** 세트만 교체하면 *제품 기획, 연구 프로젝트, 논문 작성* 등 다른 지식 구조적 영역으로 확장 가능한 구조다.
- **지식 베이스 확장**: Bedrock Knowledge Base의 Data Source만 추가하면, 새로운 방법론·도메인 지식을 바로 RAG에 태울 수 있다.
- **기관·교육 기관 도입**: 수집된 학습 행동 데이터는 **대학·부트캠프의 교육 개선 데이터**로 확장될 가능성이 있다.

### 5-3. 프로젝트 규모의 적절성 (체크포인트 6 대응)

> **질문:** "AI의 활용으로 1인 프로젝트 규모도 상당히 커진 것을 감안할 때, 4명 팀에 적절한 규모인가?"

**결론: 적절하다.** 근거는 세 가지.

1. **분명한 역할 분리 + 상호 의존성 존재**
   FE(1명) · BE(2명) · AI/Infra(1명, 팀장)로 나뉘되, 각 파트가 **독립적으로 개발 가능**하면서도 **최종 통합 시 팀 협업이 필수**인 구조. 1인 프로젝트로는 전 영역을 깊이 있게 다루기 어려운 스코프다.
2. **AI 자동화로도 대체 안 되는 설계 영역**
   24개 필수 Step의 **목표·진입·충족 기준 정의**, 사이드패널 콘텐츠 자체 제작, 노션 템플릿 설계 등은 **팀의 전문적 판단**이 필요한 영역이다. AI가 코드는 도와주지만, *"어떤 기준으로 필수 Step을 정의할 것인가"* 는 팀이 설계해야 한다.
3. **AWS 아키텍처의 운영 복잡도**
   Bedrock, Lambda 2개, RDS, S3 Vectors, Knowledge Base 등 **8개 AWS 서비스**를 연동하고 CI/CD·배포·모니터링까지 구축하는 것은 1인 스코프로는 부담이 크다.

**AI 활용으로 팀이 더 집중한 영역** — 단순 코드 작성에 들어가던 공수를 **도메인 설계 · 방법론 문서 작성 · UX 실험 · RAG 품질 튜닝** 등 AI가 대체할 수 없는 영역에 재배치했다.

---

## 6. 소프트웨어 방법론 근거

Poco가 참조하는 학술적 근거와, 각 출처가 실제 서비스 어디에서 사용되는지를 투명하게 공개한다.

### 6-1. 참조 문서와 역할

| 문서 | 분류 | 활용 범위 |
|---|---|---|
| **DOJ SDLC Guidance Document** (미국 법무부, Jan 2003) | 소프트웨어 개발 방법론 | **Stage 6개 구성 + 24개 필수 Step 정의**의 가장 큰 틀. 동적 생성 일반 Step의 RAG 참고 지식으로도 사용. |
| **SWEBOK V4.0a** (2024, IEEE Computer Society) | 소프트웨어 공학 지식체계 | 동적 생성 일반 Step의 **자체 제작 가이드 문서**의 뼈대 참조. |

### 6-2. 자체 제작 자산

Poco는 참조 문서를 **그대로 노출하지 않는다.** 팀이 다음 자산들을 자체 제작하여, 참조 문서를 **초심자 친화적인 형태로 변환**했다.

| 자체 제작 자산 | 근거 | 설명 |
|---|---|---|
| **6개 Stage 구성** | DOJ SDLC 기반, 팀 자체 정의 | 타겟 사용자(초심자)에 맞게 DOJ의 10개 Phase 중 6개만 선별. |
| **24개 필수 Step** (Stage별 4개씩) | DOJ SDLC 기반, 팀 자체 정의 | 각 필수 Step의 **목표·진입 기준·충족 기준 측면**을 팀이 모두 자체 정의. |
| **필수 Step 사이드패널 콘텐츠** | 팀 자체 제작 | Description·Perspectives·Goals·Common Mistakes·One-line Tip 등 모든 항목 자체 작성. |
| **필수 Step 노션 템플릿 (24개)** | 팀 자체 제작 | 각 필수 Step의 산출물 작성을 돕는 템플릿 페이지. |
| **일반 Step RAG 참고 가이드 문서** | SWEBOK 토픽 참조, 팀 자체 제작 | 자체 작성한 Glossary(용어 사전) + Technique(기법 가이드) 문서를 S3 Vectors에 인덱싱. |

> 이 구조의 의미는, Poco의 **안내 품질이 AI의 즉흥성이 아닌, 팀이 설계한 학술적 근거 위에서 나온다**는 것이다. AI는 팀이 만든 구조 안에서 **동적 맥락 생성**만 담당한다.

### 6-3. 6 Stage 진행 플로우

| 번호 | 한글명 | 영문명 | 설명 |
|:---:|---|---|---|
| 1 | 아이디어 구체화 | *Ideation* | 막연한 아이디어를 "왜 만들 가치가 있는가"로 다듬는다. |
| 2 | 프로젝트 계획 | *Planning* | 기간·인원·역할을 정하고, 어떻게 일할지 설계한다. |
| 3 | 요구사항 정의 | *Requirement* | 시스템이 "무엇을" 해야 하는지 구체적으로 정의한다. |
| 4 | 설계 | *Design* | 요구사항을 구조·데이터·인터페이스로 그려낸다. |
| 5 | 개발 | *Development* | 설계를 실제 동작하는 코드로 구현한다. |
| 6 | 테스트 및 검증 | *Test* | 만든 것이 처음 정의한 요구사항을 충족하는지 확인한다. |

---

## 7. 팀 소개 {#team}

**국민대학교 소프트웨어학부 | 2026 캡스톤 디자인 | AWS 트랙 1분반 59팀**

| 이름 | 역할 | GitHub |
|---|---|---|
| **정연승** *(팀장)* | 기획 · AI · Infra | [@jys705](https://github.com/jys705) |
| **장우리** | Frontend · UI/UX | [@woori02](https://github.com/woori02) |
| **김한림** | Backend · DB · CI/CD | [@gksfla8947](https://github.com/gksfla8947) |
| **박수연** | Backend · DB | [@syeon111](https://github.com/syeon111) |

---

## 8. 레포지토리 탐색 가이드

> 평가자가 실제 코드를 열어볼 때 참고할 수 있는 폴더 맵입니다.

```
2026-capstone-59/
│
├── frontend/               → React SPA (UI/UX, 캔버스 시각화)
│   ├── src/
│   └── public/
│
├── backend/                → FastAPI 메인 서버
│   ├── app/
│   │   ├── ai/             → AI 모듈 납품 자리 (ai/ 폴더에서 검증 후 이관)
│   │   ├── core/
│   │   │   ├── models/     → SQLAlchemy 모델 (Project, Stage, Step, RequiredStep ...)
│   │   │   └── seeds/      → 24개 필수 Step 시드 데이터 + 필수 Step 사이드패널 콘텐츠
│   │   └── routers/        → API 엔드포인트
│   ├── alembic/            → DB 마이그레이션
│   └── tests/
│
├── ai/                     → AI 모듈 독립 개발·검증 공간
│   ├── services/           → step_generator, required_step_judge, side_panel_generator
│   ├── clients/            → Bedrock Claude, Knowledge Base 공통 클라이언트
│   ├── prompts/            → 시나리오별 프롬프트 템플릿 (.txt)
│   ├── schemas/            → Pydantic 스키마 (generate, accept, side_panel)
│   ├── data/               → RAG 인덱싱 원본 (Bedrock Knowledge Base로 업로드)
│   │   ├── doj/            →   KB-A: DOJ SDLC Guidance Document 마크다운 변환본
│   │   └── custom/         →   KB-B: 팀 자체 제작 가이드 문서
│   │       ├── glossary/   →     용어 사전 (1 파일 = 1 개념)
│   │       └── technique/  →     기법 가이드 (1 파일 = 1 기법)
│   └── tests/              → 단위 테스트 + Property-Based Tests (hypothesis)
│
├── assets/                 → 소개 페이지 이미지 (로고, 아키텍처 다이어그램, 포스터 등)
├── docker-compose.yml      → 로컬 개발 환경
├── index.md                → GitHub Pages 소개 페이지 (이 페이지)
└── README.md               → 프로젝트 개요
```

**주요 문서**
- [프로젝트 전체 레포](https://github.com/kookmin-sw/2026-capstone-59)
<!-- TODO: 아래 경로들은 각 파트 README 작성 후 활성화 -->
- `backend/README.md` — 백엔드 실행 방법
- `ai/README.md` — AI 모듈 독립 검증 방법
- `ai/data/README.md` — RAG 인덱싱 원본 가이드
- `frontend/README.md` — 프론트엔드 실행 방법

---

## 9. 사용법

### 9-1. 배포 버전 (개발 중)

<!-- TODO: 배포 완료 후 링크 삽입 -->
> *현재 개발 중입니다. 배포 후 링크를 추가할 예정입니다.*

### 9-2. 로컬 실행

```bash
# 1. 레포 클론
git clone https://github.com/kookmin-sw/2026-capstone-59.git
cd 2026-capstone-59

# 2. Docker Compose로 전체 스택 실행
docker-compose up -d

# 3. 개별 실행 시
# - Backend: cd backend && uvicorn app.main:app --reload
# - Frontend: cd frontend && npm install && npm run dev
# - AI 모듈 테스트: cd ai && uv run pytest
```

자세한 환경 변수 및 AWS 자격증명 설정은 각 폴더의 `README.md`를 참조해주세요.

---

<sub>*본 프로젝트는 소프트웨어 공학 지식체계 **SWEBOK V4.0a** (2024, IEEE Computer Society) 및 미국 법무부(**DOJ**) **SDLC Guidance Document** 를 참조하여 설계되었습니다.*</sub>