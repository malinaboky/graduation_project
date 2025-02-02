"""add column_number to field

Revision ID: 3c34e83dabdd
Revises: 50c4ce601388
Create Date: 2024-03-26 21:34:52.549441

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c34e83dabdd'
down_revision: Union[str, None] = '50c4ce601388'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('field', sa.Column('column_number', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('field', 'column_number')
    # ### end Alembic commands ###
