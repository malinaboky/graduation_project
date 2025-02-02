"""first database init

Revision ID: 9132f5e1c785
Revises: 
Create Date: 2024-02-07 19:15:10.837162

"""
from typing import Sequence, Union

import fastapi_users_db_sqlalchemy
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9132f5e1c785'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('row',
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('email', sa.VARCHAR(length=255), nullable=False),
    sa.Column('hashed_password', sa.VARCHAR(length=512), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_table('access_token',
    sa.Column('user_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('token', sa.String(length=43), nullable=False),
    sa.Column('created_at', fastapi_users_db_sqlalchemy.generics.TIMESTAMPAware(timezone=True), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('token', 'id')
    )
    op.create_index(op.f('ix_access_token_created_at'), 'access_token', ['created_at'], unique=False)
    op.create_table('data_pipeline',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), nullable=False),
    sa.Column('pause', sa.Boolean(), nullable=False),
    sa.Column('cron_string', sa.VARCHAR(length=255), nullable=True),
    sa.Column('type_res', sa.VARCHAR(length=255), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_data_pipeline_user_id'), 'data_pipeline', ['user_id'], unique=False)
    op.create_table('connection',
    sa.Column('data_pipeline', sa.UUID(), nullable=False),
    sa.Column('connect_str', sa.VARCHAR(length=255), nullable=False),
    sa.Column('auth', sa.Boolean(), nullable=False),
    sa.Column('user', sa.VARCHAR(length=255), nullable=True),
    sa.Column('hashed_password', sa.VARCHAR(length=512), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['data_pipeline'], ['data_pipeline.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_connection_data_pipeline'), 'connection', ['data_pipeline'], unique=False)
    op.create_table('field',
    sa.Column('data_pipeline', sa.UUID(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), nullable=False),
    sa.Column('type', sa.VARCHAR(length=255), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['data_pipeline'], ['data_pipeline.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_field_data_pipeline'), 'field', ['data_pipeline'], unique=False)
    op.create_table('file',
    sa.Column('data_pipeline', sa.UUID(), nullable=False),
    sa.Column('path', sa.VARCHAR(length=255), nullable=False),
    sa.Column('type', sa.VARCHAR(length=255), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['data_pipeline'], ['data_pipeline.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_file_data_pipeline'), 'file', ['data_pipeline'], unique=False)
    op.create_table('version',
    sa.Column('data_pipeline', sa.UUID(), nullable=False),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('is_done', sa.Boolean(), nullable=False),
    sa.Column('date', sa.TIMESTAMP(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['data_pipeline'], ['data_pipeline.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_version_data_pipeline'), 'version', ['data_pipeline'], unique=False)
    op.create_table('data',
    sa.Column('field_id', sa.UUID(), nullable=False),
    sa.Column('row_id', sa.UUID(), nullable=False),
    sa.Column('version_id', sa.UUID(), nullable=False),
    sa.Column('value', sa.VARCHAR(length=255), nullable=False),
    sa.Column('last_job', sa.Integer(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['field_id'], ['field.id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['row_id'], ['row.id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['version_id'], ['version.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_data_field_id'), 'data', ['field_id'], unique=False)
    op.create_index(op.f('ix_data_row_id'), 'data', ['row_id'], unique=False)
    op.create_index(op.f('ix_data_version_id'), 'data', ['version_id'], unique=False)
    op.create_table('job',
    sa.Column('data_pipeline', sa.UUID(), nullable=False),
    sa.Column('field_id', sa.UUID(), nullable=True),
    sa.Column('version_id', sa.UUID(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.Column('type', sa.VARCHAR(length=255), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['data_pipeline'], ['data_pipeline.id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['field_id'], ['field.id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['version_id'], ['version.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_data_pipeline'), 'job', ['data_pipeline'], unique=False)
    op.create_index(op.f('ix_job_field_id'), 'job', ['field_id'], unique=False)
    op.create_index(op.f('ix_job_version_id'), 'job', ['version_id'], unique=False)
    op.create_table('running_job',
    sa.Column('data_pipeline', sa.UUID(), nullable=False),
    sa.Column('job_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['data_pipeline'], ['data_pipeline.id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['job_id'], ['job.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_running_job_data_pipeline'), 'running_job', ['data_pipeline'], unique=False)
    op.create_index(op.f('ix_running_job_job_id'), 'running_job', ['job_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_running_job_job_id'), table_name='running_job')
    op.drop_index(op.f('ix_running_job_data_pipeline'), table_name='running_job')
    op.drop_table('running_job')
    op.drop_index(op.f('ix_job_version_id'), table_name='job')
    op.drop_index(op.f('ix_job_field_id'), table_name='job')
    op.drop_index(op.f('ix_job_data_pipeline'), table_name='job')
    op.drop_table('job')
    op.drop_index(op.f('ix_data_version_id'), table_name='data')
    op.drop_index(op.f('ix_data_row_id'), table_name='data')
    op.drop_index(op.f('ix_data_field_id'), table_name='data')
    op.drop_table('data')
    op.drop_index(op.f('ix_version_data_pipeline'), table_name='version')
    op.drop_table('version')
    op.drop_index(op.f('ix_file_data_pipeline'), table_name='file')
    op.drop_table('file')
    op.drop_index(op.f('ix_field_data_pipeline'), table_name='field')
    op.drop_table('field')
    op.drop_index(op.f('ix_connection_data_pipeline'), table_name='connection')
    op.drop_table('connection')
    op.drop_index(op.f('ix_data_pipeline_user_id'), table_name='data_pipeline')
    op.drop_table('data_pipeline')
    op.drop_index(op.f('ix_access_token_created_at'), table_name='access_token')
    op.drop_table('access_token')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('row')
    # ### end Alembic commands ###
