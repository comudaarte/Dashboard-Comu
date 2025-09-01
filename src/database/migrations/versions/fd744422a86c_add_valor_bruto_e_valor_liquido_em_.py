"""add valor_bruto e valor_liquido em transacoes

Revision ID: fd744422a86c
Revises: 5b36431818f0
Create Date: 2025-07-03 16:43:03.321744

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd744422a86c'
down_revision: Union[str, None] = '5b36431818f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Adiciona as colunas valor_bruto e valor_liquido
    op.add_column('transacoes', sa.Column('valor_bruto', sa.Numeric(10, 2)))
    op.add_column('transacoes', sa.Column('valor_liquido', sa.Numeric(10, 2)))


def downgrade() -> None:
    # Remove as colunas valor_bruto e valor_liquido
    op.drop_column('transacoes', 'valor_bruto')
    op.drop_column('transacoes', 'valor_liquido')
