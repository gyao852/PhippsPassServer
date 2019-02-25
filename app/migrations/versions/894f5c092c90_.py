"""empty message

Revision ID: 894f5c092c90
Revises: c9e44c741b1a
Create Date: 2019-02-24 01:32:43.471007

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '894f5c092c90'
down_revision = 'c9e44c741b1a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('device',
    sa.Column('device_lib_id', sa.String(length=100), nullable=False),
    sa.Column('push_token', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('device_lib_id')
    )
    op.create_table('member_pass',
    sa.Column('member_id', sa.String(length=100), nullable=False),
    sa.Column('pass_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['member_id'], ['member.id'], ),
    sa.ForeignKeyConstraint(['pass_id'], ['pass.id'], ),
    sa.PrimaryKeyConstraint('member_id', 'pass_id')
    )
    op.drop_column('member', 'expiration_date')
    op.add_column('pass', sa.Column('authenticationToken', sa.String(length=100), nullable=True))
    op.add_column('pass', sa.Column('expiration_date', sa.DateTime(), nullable=True))
    op.add_column('pass', sa.Column('last_updated', sa.DateTime(), nullable=True))
    op.add_column('pass', sa.Column('membership_level', sa.String(length=100), nullable=True))
    op.alter_column('pass', 'file_name',
               existing_type=sa.VARCHAR(length=300),
               type_=sa.String(length=100),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('pass', 'file_name',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=300),
               existing_nullable=True)
    op.drop_column('pass', 'membership_level')
    op.drop_column('pass', 'last_updated')
    op.drop_column('pass', 'expiration_date')
    op.drop_column('pass', 'authenticationToken')
    op.add_column('member', sa.Column('expiration_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_table('member_pass')
    op.drop_table('device')
    # ### end Alembic commands ###