"""empty message

Revision ID: 76a6a544a65b
Revises: 894f5c092c90
Create Date: 2019-02-24 01:58:37.997369

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '76a6a544a65b'
down_revision = '894f5c092c90'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pass_device',
    sa.Column('pass_id', sa.Integer(), nullable=True),
    sa.Column('device_id', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['device_id'], ['device.id'], ),
    sa.ForeignKeyConstraint(['pass_id'], ['pass.id'], )
    )
    op.add_column('device', sa.Column('id', sa.Integer(), nullable=False))
    op.alter_column('device', 'device_lib_id',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    op.add_column('member', sa.Column('expiration_date', sa.DateTime(), nullable=True))
    op.alter_column('member', 'address_line_1',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    op.alter_column('member', 'city',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    op.alter_column('member', 'state',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    op.alter_column('member', 'status',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('member', 'zip',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    op.alter_column('member_pass', 'member_id',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    op.alter_column('member_pass', 'pass_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_constraint('pass_member_id_fkey', 'pass', type_='foreignkey')
    op.drop_column('pass', 'member_id')
    op.drop_column('pass', 'active')
    op.drop_column('pass', 'membership_level')
    op.drop_column('pass', 'expiration_date')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pass', sa.Column('expiration_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('pass', sa.Column('membership_level', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('pass', sa.Column('active', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('pass', sa.Column('member_id', sa.VARCHAR(length=100), autoincrement=False, nullable=False))
    op.create_foreign_key('pass_member_id_fkey', 'pass', 'member', ['member_id'], ['id'])
    op.alter_column('member_pass', 'pass_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('member_pass', 'member_id',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    op.alter_column('member', 'zip',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    op.alter_column('member', 'status',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('member', 'state',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    op.alter_column('member', 'city',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    op.alter_column('member', 'address_line_1',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    op.drop_column('member', 'expiration_date')
    op.alter_column('device', 'device_lib_id',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    op.drop_column('device', 'id')
    op.drop_table('pass_device')
    # ### end Alembic commands ###