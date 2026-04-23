from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.core.models.stage import Stage

# DOJ SDLC 기반 6단계 Stage 시드 데이터
# sequence | name              | DOJ SDLC Chapter
# ---------+-------------------+------------------
#        1 | 아이디어 구체화   | Ch3 + Ch4 (Initiation + System Concept Development)
#        2 | 프로젝트 계획     | Ch5 (Planning)
#        3 | 요구사항 정의     | Ch6 (Requirements Analysis)
#        4 | 설계              | Ch7 (Design)
#        5 | 개발              | Ch8 (Development)
#        6 | 테스트 및 검증    | Ch9 (Integration and Test)
STAGE_DATA: list[dict] = [
    {"sequence": 1, "name": "아이디어 구체화"},
    {"sequence": 2, "name": "프로젝트 계획"},
    {"sequence": 3, "name": "요구사항 정의"},
    {"sequence": 4, "name": "설계"},
    {"sequence": 5, "name": "개발"},
    {"sequence": 6, "name": "테스트 및 검증"},
]


def run(db: Session) -> None:
    """Stage 시드 데이터 삽입. 이미 존재하는 sequence는 name을 업데이트한다."""
    stmt = (
        insert(Stage)
        .values([{"name": r["name"], "sequence": r["sequence"]} for r in STAGE_DATA])
        .on_conflict_do_update(
            index_elements=["sequence"],
            set_={"name": insert(Stage).excluded.name},
        )
    )
    db.execute(stmt)
    db.commit()
