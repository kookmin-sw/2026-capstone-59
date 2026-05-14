"""add is_keep to step

Revision ID: 8d7474fd5838
Revises: 78ca25cfab60
Create Date: 2026-05-14 23:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d7474fd5838'
down_revision: Union[str, Sequence[str], None] = '78ca25cfab60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'step',
        sa.Column(
            'is_keep',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
        ),
    )


def downgrade() -> None:
    op.drop_column('step', 'is_keep')
