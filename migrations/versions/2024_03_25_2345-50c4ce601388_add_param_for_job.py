"""add param for job

Revision ID: 50c4ce601388
Revises: 9132f5e1c785
Create Date: 2024-03-25 23:45:35.332748

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50c4ce601388'
down_revision: Union[str, None] = '9132f5e1c785'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('job', sa.Column('params', sa.JSON(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('job', 'params')
    # ### end Alembic commands ###
