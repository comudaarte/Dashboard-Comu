"""add taxa_reembolso em transacoes

Revision ID: 711fd3d6b2a7
Revises: fabcf6fd333b
Create Date: 2025-07-11 18:20:42.410666

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '711fd3d6b2a7'
down_revision: Union[str, None] = 'fabcf6fd333b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Adiciona a coluna 'taxa_reembolso' como nullable
    op.add_column('transacoes', sa.Column('taxa_reembolso', sa.Numeric(10, 2), nullable=True))


def downgrade() -> None:
    # Remove a coluna 'taxa_reembolso'
    op.drop_column('transacoes', 'taxa_reembolso')
