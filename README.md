<p align="center">
  <a href="https://kookmin-sw.github.io/2026-capstone-59/">
    <img src="./assets/logo.png" alt="Poco 로고" width="320" />
  </a>
</p>

<h3 align="center">조금씩, 한 걸음씩 — 아이디어를 설계까지 쌓아가는 사고의 캔버스</h3>

<p align="center">
  <b>AI가 다 만들어주는 시대, 무엇을 · 왜 만들지 정의하고 계신가요?</b>
</p>

<p align="center">
  <a href="https://kookmin-sw.github.io/2026-capstone-59/"><img src="https://img.shields.io/badge/소개_페이지-GitHub_Pages-0969da?logo=github" alt="Intro Page" /></a>
  <a href="https://poco.example.com"><img src="https://img.shields.io/badge/서비스_바로가기-Poco-5C45E8" alt="Live Service" /></a>
  <a href="#-팀원"><img src="https://img.shields.io/badge/Capstone_2026-AWS_Track_59팀-FF9900?logo=amazon-aws" alt="AWS Track" /></a>
</p>

&nbsp;

## 💨 목차

1. [한 줄 요약](#-한-줄-요약)
2. [핵심 기능](#-핵심-기능)
3. [기술 스택](#-기술-스택)
4. [빠른 시작](#-빠른-시작)
5. [레포지토리 구조](#-레포지토리-구조)
6. [팀원](#-팀원)

&nbsp;

## 🐾 한 줄 요약

서비스를 만들고 싶은 사람이 **'AI에게 무엇을 시켜야 하는지'** 부터 체계적으로 정리할 수 있도록,
AI가 다음 할 일의 선택지를 제시하고 의사결정의 궤적을 **트리로 시각화**해주는 **사고의 캔버스**.

&nbsp;

## 🐾 핵심 기능

### 1. AI 기반 Step Flow 생성

> 막연함을 "다음 한 걸음"으로 바꾼다.

검증된 소프트웨어 개발 방법론의 **6단계**를 따라, AI가 프로젝트 맥락에 맞춘 다음 할 일을 실시간 제안합니다.

### 2. Step별 클릭 어시스턴트

> 딱딱한 방법론 문서 대신, 맥락에 맞는 가이드가 곁에.

노드 클릭 시 **멘토링 · 용어 사전 · 노션 템플릿**이 사이드패널로 펼쳐집니다.

### 3. Footprint — 의사결정 궤적

> 되돌아갈 수 있는 선택, 자산으로 남는 사고 과정.

선택한 경로가 **캔버스 트리**로 남아, 이전 분기점으로 롤백하며 새로운 길을 AI가 다시 제안합니다.

&nbsp;

## 🐾 기술 스택

**Frontend**

![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white)

**Backend**

![Python](https://img.shields.io/badge/Python_3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic_v2-E92063?style=flat-square&logo=pydantic&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest_+_Hypothesis-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)

**AI & RAG**

![Claude](https://img.shields.io/badge/Claude_Haiku_4.5-D97757?style=flat-square&logo=anthropic&logoColor=white)
![Amazon Bedrock](https://img.shields.io/badge/Amazon_Bedrock-01A88D?style=flat-square&logo=amazonaws&logoColor=white)
![Bedrock KB](https://img.shields.io/badge/Bedrock_Knowledge_Base-222F3E?style=flat-square&logo=amazonaws&logoColor=white)
![S3 Vectors](https://img.shields.io/badge/S3_Vectors-569A31?style=flat-square&logo=amazons3&logoColor=white)

**Infra (서버리스 중심)**

![AWS Lambda](https://img.shields.io/badge/AWS_Lambda-FF9900?style=flat-square&logo=awslambda&logoColor=white)
![Amazon API Gateway](https://img.shields.io/badge/API_Gateway-FF4F8B?style=flat-square&logo=amazonapigateway&logoColor=white)
![Amazon RDS](https://img.shields.io/badge/Amazon_RDS-527FFF?style=flat-square&logo=amazonrds&logoColor=white)
![Amazon S3](https://img.shields.io/badge/Amazon_S3-569A31?style=flat-square&logo=amazons3&logoColor=white)

**DevOps**

![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)

**External**

![Notion API](https://img.shields.io/badge/Notion_API-000000?style=flat-square&logo=notion&logoColor=white)

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
├── backend/           → FastAPI 메인 서버 (Business API, DB, AI 납품)
├── ai/                → AI 모듈 독립 개발·검증 공간
│   ├── services/      →   step_generator, required_step_judge, side_panel_generator
│   ├── prompts/       →   시나리오별 프롬프트 템플릿
│   ├── schemas/       →   Pydantic 스키마
│   └── data/          →   RAG 인덱싱 원본 (doj/ + custom/)
├── assets/            → 소개 페이지 이미지
├── docker-compose.yml → 로컬 개발 환경
├── index.md           → GitHub Pages 소개 페이지
└── README.md          → 프로젝트 개요
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

---

<sub>본 프로젝트는 소프트웨어 공학 지식체계 <b>SWEBOK V4.0a</b> (2024, IEEE Computer Society) 및 미국 법무부(<b>DOJ</b>) <b>SDLC Guidance Document</b> 를 참조하여 설계되었습니다.</sub>
