"""Merge migration heads

Revision ID: e4ae062c3208
Revises: 001, 0622f5d1172d
Create Date: 2026-07-07 20:20:26.322024

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4ae062c3208'
down_revision = ('001', '0622f5d1172d')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
