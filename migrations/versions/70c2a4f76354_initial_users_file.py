"""initial_users_file

Revision ID: 70c2a4f76354
Revises: 
Create Date: 2024-02-08 12:52:42.301907

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70c2a4f76354'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('uid', sa.Uuid(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('uid')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('file',
    sa.Column('fid', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=250), nullable=False),
    sa.Column('created', sa.DateTime(timezone=True), nullable=True),
    sa.Column('path', sa.String(length=250), nullable=True),
    sa.Column('size', sa.Float(), nullable=True),
    sa.Column('extension', sa.String(length=10), nullable=True),
    sa.Column('user_id', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.uid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('fid')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('file')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
