"""adding external ID column to Posts

Revision ID: e8132f513d1b
Revises: 352280a41aeb
Create Date: 2026-06-13 20:58:36.491493

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8132f513d1b'
down_revision: Union[str, Sequence[str], None] = '352280a41aeb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('external_id', sa.String(), nullable=False))
    op.create_unique_constraint('uq_platform_source', 'posts', ['platform_id', 'external_id'])

def downgrade() -> None:
    op.drop_constraint('uq_platform_source', 'posts', type_='unique')
    op.drop_column('posts', 'external_id')
