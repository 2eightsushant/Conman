"""Added Ingestion_head with constraints, also updated on relative tables

Revision ID: b3fb426ff74e
Revises: 59d1a621d7ce
Create Date: 2025-07-09 06:22:53.059730

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3fb426ff74e'
down_revision: Union[str, Sequence[str], None] = '59d1a621d7ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
