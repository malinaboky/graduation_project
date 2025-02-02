"""replace cron with time_lag in pipeline

Revision ID: 90d4f20374cb
Revises: 1061c01f553d
Create Date: 2024-04-11 22:48:00.590979

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '90d4f20374cb'
down_revision: Union[str, None] = '1061c01f553d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('data_pipeline', sa.Column('min_time_lag', sa.INTEGER(), nullable=True))
    op.alter_column('data_pipeline', 'date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.drop_column('data_pipeline', 'cron_string')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('data_pipeline', sa.Column('cron_string', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.alter_column('data_pipeline', 'date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.drop_column('data_pipeline', 'min_time_lag')
    # ### end Alembic commands ###
