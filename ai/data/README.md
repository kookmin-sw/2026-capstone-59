# ai/data/

Poco의 **RAG 파이프라인**(Bedrock Knowledge Base + S3 Vectors)에 인덱싱되는 **장기 지식(Long-term knowledge)** 원본 저장소.

## 폴더 구조

```
ai/data/
├── doj/        → DOJ SDLC Guidance Document (Jan 2003) 마크다운 변환본
└── custom/     → 팀 자체 제작 가이드 문서 (SWEBOK 토픽 체계 참조)
    ├── glossary/   → 용어 사전 (1 파일 = 1 개념)
    └── technique/  → 기법 가이드 (1 파일 = 1 기법)
```

## 설계 원칙

| 구분 | 역할 | AI 활용 시나리오 |
|---|---|---|
| **doj/** (KB-A) | 절차/산출물/활동 범위 검색 | "이 Stage에서 뭘 해야 해?" 류 질문 |
| **custom/** (KB-B) | 용어·기법 검색 | "그걸 어떤 방법으로 해?" / "이 용어가 뭐야?" 류 질문 |

두 데이터 소스는 **물리적으로 분리**하여 Bedrock Knowledge Base의 Data Source로 각각 등록됩니다.  
분리 이유와 상세 설계는 `.kiro/steering/Poco_AI_Design_Guide_v1.md` 섹션 3 참조.

## 업데이트 시 주의

- 이 폴더의 마크다운 파일이 추가·수정되면, **S3 업로드 후 Bedrock Knowledge Base의 Sync 작업**이 필요합니다.
- Sync 절차는 팀 내부 배포 문서 참조.

## 라이선스·출처 표시

- **DOJ SDLC** — 미국 법무부 간행물 (public domain, 17 U.S.C. § 105). 원본 출처는 하위 `doj/` 문서 내에 명시.
- **custom/** — 팀 자체 저작물. SWEBOK V4.0a의 토픽 체계만 참조하고, 원문은 사용하지 않음.
