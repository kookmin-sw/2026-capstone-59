"""change_constraint_text_to_constraints_jsonb

Revision ID: 78ca25cfab60
Revises: 6bd360bbd9f0
Create Date: 2026-05-14 20:05:06.159899

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

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