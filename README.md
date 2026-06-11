<p align="center">
  <a href="https://kookmin-sw.github.io/2026-capstone-59/landing/">
    <img src="./assets/logo.png" alt="Poco 로고" width="400" />
  </a>
</p>

<h3 align="center">조금씩, 한 걸음씩 — 아이디어를 설계까지 쌓아가는 사고의 캔버스</h3>

<p align="center">
  AI가 다 만들어주는 시대, 무엇을 · 왜 만들지 정의하고 계신가요?
</p>

<p align="center">
  <a href="https://kookmin-sw.github.io/2026-capstone-59/"><img src="https://img.shields.io/badge/소개_페이지-GitHub_Pages-0969da?logo=github" alt="Intro Page" /></a>
  <a href="https://kookmin-sw.github.io/2026-capstone-59/landing/"><img src="https://img.shields.io/badge/랜딩페이지_바로가기-Poco-5C45E8" alt="Landing Page" /></a>
  <a href="https://github.com/kookmin-sw/2026-capstone-59/raw/master/assets/poco_ppt.pdf"><img src="https://img.shields.io/badge/발표자료-PDF-E8453C?logo=adobeacrobatreader&logoColor=white" alt="발표자료 PDF" /></a>
  <a href="#-팀원"><img src="https://img.shields.io/badge/Capstone_2026-AWS_분반_59팀-FF9900?logo=amazon-aws" alt="AWS 분반" /></a>
</p>

&nbsp;

## 💨 목차

1. [포스터](#-포스터)
1. [시연 영상](#-시연-영상)
1. [한 줄 요약](#-한-줄-요약)
2. [핵심 기능](#-핵심-기능)
3. [시스템 아키텍처](#-시스템-아키텍처)
4. [기술 스택](#-기술-스택)
5. [빠른 시작](#-빠른-시작)
6. [레포지토리 구조](#-레포지토리-구조)
7. [팀원](#-팀원)

&nbsp;

## 🐾 포스터

<p align="center">
  <img src="./assets/poster.png" alt="Poco 포스터" width="100%" style="max-width:900px;" />
</p>

&nbsp;

## 🐾 시연 영상

[![Poco 시연 영상](./assets/video_thumbnail.png)](https://youtu.be/dm9nSAuRjMo)

&nbsp;

## 🐾 한 줄 요약

서비스를 만들고 싶은 사람이 **"뭘 만들고 싶고, 왜 만드는지"** 를 **제 언어로** 말할 수 있도록,
AI가 다음 한 걸음의 선택지를 제시하고 의사결정의 궤적을 **트리로 시각화**해주는 **사고의 캔버스**.

&nbsp;

## 🐾 핵심 기능

### 1. AI 기반 Step 생성

> 막연함을 "다음 한 걸음"으로 바꿉니다.

검증된 소프트웨어 개발 방법론의 **6단계**를 따라, AI가 프로젝트 맥락에 맞춘 다음 할 일을 실시간 제안합니다.

### 2. Step별 클릭 어시스턴트

> 맥락에 맞는 어시스턴트가, 곁에.

노드 클릭 시 **멘토링 · 용어 사전**이 사이드패널로 펼쳐지고, 핵심 관문에서는 **팀이 설계한 노션 템플릿**(웹 게시 링크)이 연결됩니다.

### 3. Footprint — 의사결정 궤적

> 되돌아갈 수 있는 선택, 트리로 남는 사고 과정.

선택한 경로가 **캔버스 트리**로 남아, 이전 분기점으로 롤백하며 새로운 길을 AI가 다시 제안합니다.

### 4. 의사결정 궤적 추출

> 선택은 자산이 됩니다.

사용자가 쌓아온 사고의 흐름이 **마크다운 파일**로 한 번에 정돈되어, 매번 같은 고민을 다시 풀어 설명하지 않아도 됩니다.

&nbsp;

## 🐾 시스템 아키텍처

<img src="./assets/architecture.png" alt="Poco System Architecture" />

> *AI가 검증된 방법론을 실시간 참조하는 구조. [자세히 보기 →](https://kookmin-sw.github.io/2026-capstone-59/#5-기술-설계)*

&nbsp;

## 🐾 기술 스택

**Frontend**

![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white)
![Amazon S3](https://img.shields.io/badge/Amazon_S3_%28Static_Website_Hosting%29-569A31?style=flat-square&logo=amazons3&logoColor=white)

**Backend**

![Python](https://img.shields.io/badge/Python_3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic_v2-E92063?style=flat-square&logo=pydantic&logoColor=white)
![Amazon API Gateway](https://img.shields.io/badge/Amazon_API_Gateway-FF4F8B?style=flat-square&logo=amazonapigateway&logoColor=white)
![AWS Lambda](https://img.shields.io/badge/AWS_Lambda_%28Business_API%29-FF9900?style=flat-square&logo=awslambda&logoColor=white)
![Amazon RDS](https://img.shields.io/badge/Amazon_RDS-C924D0?style=flat-square&logo=amazonrds&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)

**AI & RAG**

![Python](https://img.shields.io/badge/Python_3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![Claude](https://img.shields.io/badge/Claude_Haiku_4.5-D97757?style=flat-square&logo=anthropic&logoColor=white)
![Amazon Bedrock](https://img.shields.io/badge/Amazon_Bedrock-01A88D?style=flat-square&logo=amazonaws&logoColor=white)
![Amazon Bedrock Knowledge Bases](https://img.shields.io/badge/Amazon_Bedrock_Knowledge_Bases-222F3E?style=flat-square&logo=amazonaws&logoColor=white)
![Amazon S3 Vectors](https://img.shields.io/badge/Amazon_S3_Vectors-569A31?style=flat-square&logo=amazons3&logoColor=white)
![AWS Lambda](https://img.shields.io/badge/AWS_Lambda_%28AI_Orchestrator%29-FF9900?style=flat-square&logo=awslambda&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest_+_Hypothesis-0A9EDC?style=flat-square&logo=pytest&logoColor=white)

**DevOps (Local)**

![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)

&nbsp;

## 🐾 빠른 시작

```bash
git clone https://github.com/kookmin-sw/2026-capstone-59.git
cd 2026-capstone-59
docker-compose up -d
```

세부 실행 방법은 각 폴더(`frontend/`, `backend/`, `ai/`)의 README.md를 참조해주세요.

&nbsp;

## 🐾 레포지토리 구조

```
2026-capstone-59/
├── frontend/          → React SPA (UI/UX, 캔버스 시각화)
│   ├── src/
│   │   ├── api/        →  백엔드 통신 클라이언트 (auth, projects, steps, exports …)
│   │   ├── components/ →  공용·캔버스 컴포넌트 (StepNode, SidePanel, MdExportModal …)
│   │   ├── pages/      →  라우트 단위 페이지 (Landing, Login, Canvas, ProjectList …)
│   │   ├── hooks/      →  커스텀 훅
│   │   └── utils/      →  레이아웃·트리 유틸
│   └── public/         →  정적 자산 (로고, 랜딩페이지 이미지)
│
├── backend/           → FastAPI 메인 서버 (Lambda A: Business API + Lambda B: AI Orchestrator)
│   ├── app/
│   │   ├── ai/         →  AI 엔드포인트 (Lambda B 진입점)
│   │   ├── business/   →  비즈니스 엔드포인트 (Lambda A 진입점, 인증·프로젝트·CRUD)
│   │   └── core/       →  공통 모델·스키마·DB·예외·시드 데이터
│   ├── alembic/        →  DB 마이그레이션
│   └── docs/           →  Swagger 보조 자료
│
├── ai/                → AI 모듈 독립 개발·검증 공간 (Bedrock + RAG)
│   ├── services/       →  step_generator, required_step_judge, side_panel_generator, design_export_generator, position_label
│   ├── clients/        →  Bedrock Claude · Knowledge Base 공통 클라이언트
│   ├── prompts/        →  시나리오별 프롬프트 템플릿 (.txt)
│   ├── schemas/        →  Pydantic 스키마 (generate, accept, side_panel, design_export)
│   ├── data/           →  RAG 인덱싱 원본
│   │   ├── doj/        →    DOJ SDLC 마크다운 변환본
│   │   └── custom/     →    팀 자체 제작 가이드 (glossary, technique)
│   └── tests/          →  단위 + Property-Based Tests (hypothesis)
│
├── assets/            → 소개 페이지·README 이미지 (포스터, 로고, 아키텍처 다이어그램)
├── docker-compose.yml → 로컬 개발 환경 (db, backend-a, backend-b, frontend)
├── index.md           → GitHub Pages 소개 페이지
└── README.md          → 프로젝트 개요 (이 파일)
```

&nbsp;

## 🐾 팀원

<table>
  <tr>
    <td align="center" width="180">
      <a href="https://github.com/jys705">
        <img src="https://github.com/jys705.png" width="140" alt="정연승" style="border-radius:6px;" />
      </a>
      <br />
      <a href="https://github.com/jys705"><strong>정연승 (팀장)</strong></a>
    </td>
    <td align="center" width="180">
      <a href="https://github.com/woori02">
        <img src="https://github.com/woori02.png" width="140" alt="장우리" style="border-radius:6px;" />
      </a>
      <br />
      <a href="https://github.com/woori02"><strong>장우리</strong></a>
    </td>
    <td align="center" width="180">
      <a href="https://github.com/gksfla8947">
        <img src="https://github.com/gksfla8947.png" width="140" alt="김한림" style="border-radius:6px;" />
      </a>
      <br />
      <a href="https://github.com/gksfla8947"><strong>김한림</strong></a>
    </td>
    <td align="center" width="180">
      <a href="https://github.com/syeon111">
        <img src="https://github.com/syeon111.png" width="140" alt="박수연" style="border-radius:6px;" />
      </a>
      <br />
      <a href="https://github.com/syeon111"><strong>박수연</strong></a>
    </td>
  </tr>
  <tr>
    <td align="center">기획, AI, Infra</td>
    <td align="center">Frontend, UI/UX</td>
    <td align="center">Backend, DB, CI/CD</td>
    <td align="center">Backend, DB</td>
  </tr>
</table>

&nbsp;

<!-- ---

&nbsp;

<p align="center">
  <br/>
  <b style="font-size:1.4em;">조금씩, 한 걸음씩</b>
  <br/>
  <b style="font-size:1.4em;">첫 한 걸음을 시작하세요.</b>
  <br/><br/>
</p>

$${\color{#6c63b5}\textsf{Poco는 그 답을 스스로 찾아가는 구조를 제공합니다.}}$$

<p align="center">
  <br/>
  <a href="http://pj-kmucd1-09-poco-frontend.s3-website-us-east-1.amazonaws.com/">
    <img src="./assets/cta-start.svg" alt="시작하기" height="42" />
  </a>
  <br/><br/>
</p>

&nbsp; -->

---

<sub>*본 프로젝트는 미국 법무부 SDLC Guidance Document의 10단계 Phase를 재검토·선별하여 6단계로 재구성하고, SWEBOK V4.0a (2024, IEEE Computer Society)의 토픽 구조를 참고하여 자체 가이드를 제작했습니다.*</sub>
