<p align="center">
  <img src="./assets/logo.png" alt="Poco 로고" width="360" />
</p>

### 조금씩, 한 걸음씩 — 아이디어를 설계까지 쌓아가는 사고의 캔버스

> **AI가 다 만들어주는 시대, 무엇을·왜 만들지 정의하고 계신가요?**

🌐 **[팀 소개페이지 바로가기](https://kookmin-sw.github.io/2026-capstone-59/)**

---

## 📌 한 줄 요약

서비스를 만들고 싶은 사람이 **'AI에게 무엇을 시켜야 하는지'** 부터 체계적으로 정리할 수 있도록, AI가 다음 할 일의 선택지를 제시하고 의사결정의 궤적을 **트리로 시각화**해주는 **사고의 캔버스**.

## ✨ 핵심 기능 Top 3

| # | 기능 | 설명 |
|---|---|---|
| ① | **AI 기반 Step Flow 생성** | 검증된 소프트웨어 개발 방법론의 6단계를 따라, AI가 프로젝트 맥락에 맞춘 다음 할 일을 실시간 제안합니다. |
| ② | **Step별 클릭 어시스턴트** | 노드 클릭 시 DOJ Chapter 근거의 멘토링·용어 사전·노션 템플릿이 사이드패널로 펼쳐집니다. |
| ③ | **Footprint — 의사결정 궤적** | 선택한 경로가 캔버스 트리로 남아, 이전 분기점으로 롤백하며 새로운 길을 AI가 다시 제안합니다. |

## 🏗️ 기술 스택

![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python_3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![AWS Lambda](https://img.shields.io/badge/AWS_Lambda-FF9900?style=flat-square&logo=awslambda&logoColor=white)
![Amazon Bedrock](https://img.shields.io/badge/Amazon_Bedrock-222F3E?style=flat-square&logo=amazonaws&logoColor=white)
![Claude](https://img.shields.io/badge/Claude_Haiku_4.5-D97757?style=flat-square&logo=anthropic&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Amazon S3](https://img.shields.io/badge/Amazon_S3-569A31?style=flat-square&logo=amazons3&logoColor=white)
![Notion API](https://img.shields.io/badge/Notion_API-000000?style=flat-square&logo=notion&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

- **Frontend:** React SPA · S3 Static Website Hosting
- **Backend:** FastAPI (Python 3.13) · AWS Lambda · Amazon RDS PostgreSQL
- **AI:** Amazon Bedrock Claude (Haiku 4.5) · Bedrock Knowledge Base · S3 Vectors
- **Architecture:** AWS 서버리스 중심 + RAG 파이프라인 (단기 기억 · 장기 지식 분리 설계)
- **External:** Notion API (필수 Step 템플릿 생성)

## 🚀 빠른 시작

```bash
git clone https://github.com/kookmin-sw/2026-capstone-59.git
cd 2026-capstone-59
docker-compose up -d
```

세부 실행 방법은 각 폴더(`frontend/`, `backend/`, `ai/`)의 README.md를 참조해주세요.

## 📂 레포지토리 구조

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

## 👥 팀원

| 이름 | 역할 | GitHub |
|---|---|---|
| **정연승** *(팀장)* | 기획 · AI · Infra | [@jys705](https://github.com/jys705) |
| **장우리** | Frontend · UI/UX | [@woori02](https://github.com/woori02) |
| **김한림** | Backend · DB · CI/CD | [@gksfla8947](https://github.com/gksfla8947) |
| **박수연** | Backend · DB | [@syeon111](https://github.com/syeon111) |

## 📖 문서
<!-- TODO: 포스터·소개 영상·배포 링크 완성 후 추가 -->

---

<sub>본 프로젝트는 소프트웨어 공학 지식체계 **SWEBOK V4.0a** (2024, IEEE Computer Society) 및 미국 법무부(**DOJ**) **SDLC Guidance Document** 를 참조하여 설계되었습니다.</sub>
