"""add log table

Revision ID: 0f5d24b50f7d
Revises: 2018d4ff074b
Create Date: 2024-03-28 00:28:45.669940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f5d24b50f7d'
down_revision: Union[str, None] = '2018d4ff074b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('log',
    sa.Column('data_pipeline', sa.UUID(), nullable=False),
    sa.Column('status', sa.VARCHAR(length=50), nullable=False),
    sa.Column('message', sa.VARCHAR(length=255), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['data_pipeline'], ['data_pipeline.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_log_data_pipeline'), 'log', ['data_pipeline'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_log_data_pipeline'), table_name='log')
    op.drop_table('log')
    # ### end Alembic commands ###
