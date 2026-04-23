"""
시드 데이터 삽입 스크립트.
사용법: python seed.py [stage]
인자 없이 실행하면 모든 시드를 삽입한다.
"""
import sys

from app.core.database import SessionLocal
from app.core.seeds import stage as stage_seed

SEEDS = {
    "stage": stage_seed,
}


def run(targets: list[str]) -> None:
    db = SessionLocal()
    try:
        for name in targets:
            seed = SEEDS[name]
            print(f"  seeding {name}...")
            seed.run(db)
            print(f"  {name} done.")
    finally:
        db.close()


if __name__ == "__main__":
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(SEEDS.keys())
    unknown = [t for t in targets if t not in SEEDS]
    if unknown:
        print(f"unknown seeds: {unknown}. available: {list(SEEDS.keys())}")
        sys.exit(1)
    print(f"running seeds: {targets}")
    run(targets)
    print("all done.")
