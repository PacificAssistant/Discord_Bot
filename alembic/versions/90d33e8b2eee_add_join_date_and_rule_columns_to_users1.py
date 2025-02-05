"""add join_date and rule columns to users1

Revision ID: 90d33e8b2eee
Revises: ad3c00c81ce2
Create Date: 2025-02-04 13:37:24.480187

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '90d33e8b2eee'
down_revision: Union[str, None] = 'ad3c00c81ce2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
