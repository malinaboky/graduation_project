"""add db_type to connection

Revision ID: 999aa8bed040
Revises: 6493c239c218
Create Date: 2024-04-24 13:43:00.987849

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '999aa8bed040'
down_revision: Union[str, None] = '6493c239c218'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('connection', sa.Column('db_type', sa.VARCHAR(length=50), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('connection', 'db_type')
    # ### end Alembic commands ###
