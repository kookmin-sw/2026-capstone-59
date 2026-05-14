"""change_constraint_text_to_constraints_jsonb

Revision ID: 78ca25cfab60
Revises: 6bd360bbd9f0
Create Date: 2026-05-14 20:05:06.159899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '78ca25cfab60'
down_revision: Union[str, Sequence[str], None] = '6bd360bbd9f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('project', sa.Column('constraints', postgresql.JSONB(), nullable=True))
    op.execute("""
        UPDATE project
        SET constraints = jsonb_build_array(constraint_text)
        WHERE constraint_text IS NOT NULL AND constraint_text != ''
    """)
    op.execute("""
        UPDATE project
        SET constraints = '[]'::jsonb
        WHERE constraint_text IS NULL OR constraint_text = ''
    """)
    op.drop_column('project', 'constraint_text')

def downgrade():
    op.add_column('project', sa.Column('constraint_text', sa.Text(), nullable=True))
    op.drop_column('project', 'constraints')