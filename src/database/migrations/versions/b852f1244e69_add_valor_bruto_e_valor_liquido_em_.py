"""add valor_bruto e valor_liquido em transacoes (forçado)

Revision ID: b852f1244e69
Revises: 74e8bc0d6085
Create Date: 2025-07-03 19:11:37.178374

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b852f1244e69'
down_revision: Union[str, None] = '74e8bc0d6085'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from alembic import op
    import sqlalchemy as sa
    op.add_column('transacoes', sa.Column('valor_bruto', sa.Numeric(10, 2)))
    op.add_column('transacoes', sa.Column('valor_liquido', sa.Numeric(10, 2)))



def downgrade() -> None:
    from alembic import op
    op.drop_column('transacoes', 'valor_bruto')
    op.drop_column('transacoes', 'valor_liquido')
