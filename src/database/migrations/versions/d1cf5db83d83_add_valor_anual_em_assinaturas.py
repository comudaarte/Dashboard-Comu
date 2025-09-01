"""add valor_anual em assinaturas

Revision ID: d1cf5db83d83
Revises: b852f1244e69
Create Date: 2025-07-07 13:40:30.314030

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1cf5db83d83'
down_revision: Union[str, None] = 'b852f1244e69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Adiciona a coluna valor_anual em assinaturas
    op.add_column('assinaturas', sa.Column('valor_anual', sa.Numeric(10, 2)))


def downgrade() -> None:
    # Remove a coluna valor_anual em assinaturas
    op.drop_column('assinaturas', 'valor_anual')
