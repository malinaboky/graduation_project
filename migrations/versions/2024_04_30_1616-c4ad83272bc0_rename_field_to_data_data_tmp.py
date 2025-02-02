"""rename field to data data_tmp

Revision ID: c4ad83272bc0
Revises: 222f277e24e9
Create Date: 2024-04-30 16:16:49.773774

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4ad83272bc0'
down_revision: Union[str, None] = '222f277e24e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('data_tmp', sa.Column('data_id', sa.UUID(), nullable=False))
    op.alter_column('data_tmp', 'version_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.drop_column('data_tmp', 'field_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('data_tmp', sa.Column('field_id', sa.UUID(), autoincrement=False, nullable=False))
    op.alter_column('data_tmp', 'version_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.drop_column('data_tmp', 'data_id')
    # ### end Alembic commands ###
