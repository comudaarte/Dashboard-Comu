"""add plataforma em transacoes

Revision ID: fabcf6fd333b
Revises: d1cf5db83d83
Create Date: 2025-07-11 14:58:35.537722

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fabcf6fd333b'
down_revision: Union[str, None] = 'd1cf5db83d83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Adiciona a coluna 'plataforma' como nullable
    op.add_column('transacoes', sa.Column('plataforma', sa.String(length=50), nullable=True))
    # Preenche registros antigos com 'desconhecido'
    op.execute("UPDATE transacoes SET plataforma = 'desconhecido' WHERE plataforma IS NULL")
    # Torna NOT NULL
    op.alter_column('transacoes', 'plataforma', nullable=False)


def downgrade() -> None:
    # Remove a coluna 'plataforma'
    op.drop_column('transacoes', 'plataforma')
