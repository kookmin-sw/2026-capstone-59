"""seed_stage_data

Revision ID: 897a468e3c9f
Revises: 619522ef5fe8
Create Date: 2026-04-23 22:50:10.870108

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.core.seeds.stage import STAGE_DATA

# revision identifiers, used by Alembic.
revision: str = '897a468e3c9f'
down_revision: Union[str, Sequence[str], None] = '619522ef5fe8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    values = ", ".join(
        f"(gen_random_uuid(), {r['sequence']}, '{r['name']}')"
        for r in STAGE_DATA
    )
    op.execute(sa.text(
        f"INSERT INTO stage (id, sequence, name) VALUES {values} ON CONFLICT DO NOTHING"
    ))


def downgrade() -> None:
    sequences = ", ".join(str(r["sequence"]) for r in STAGE_DATA)
    op.execute(sa.text(f"DELETE FROM stage WHERE sequence IN ({sequences})"))
