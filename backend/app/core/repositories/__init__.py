"""Repository 레이어.

DB 접근 로직을 service 레이어에서 분리한다.

규칙:
- Repository 함수는 SQLAlchemy 모델/raw 데이터를 반환한다 (Pydantic 스키마 변환 X).
- Repository는 `db.flush()` 까지만 수행한다. `db.commit()` 은 Service 레이어가 트랜잭션 경계로서 책임진다.
- Repository는 도메인 예외를 raise 하지 않는다 (없으면 None 반환). 검증/예외 처리는 Service에서 한다.
"""
