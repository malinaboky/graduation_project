"""add version id to row

Revision ID: cd0b4ea64cc4
Revises: 4d693d9a8d87
Create Date: 2024-04-22 13:28:16.829158

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd0b4ea64cc4'
down_revision: Union[str, None] = '4d693d9a8d87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('row', sa.Column('version_id', sa.UUID(), nullable=False))
    op.create_index(op.f('ix_row_version_id'), 'row', ['version_id'], unique=False)
    op.create_foreign_key(None, 'row', 'version', ['version_id'], ['id'], ondelete='cascade')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'row', type_='foreignkey')
    op.drop_index(op.f('ix_row_version_id'), table_name='row')
    op.drop_column('row', 'version_id')
    # ### end Alembic commands ###
