"""empty message

Revision ID: b5b00d8bae15
Revises: 7812f28e1416
Create Date: 2019-02-24 02:42:47.948542

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b5b00d8bae15'
down_revision = '7812f28e1416'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pass_device_association',
    sa.Column('pass_id', sa.Integer(), nullable=True),
    sa.Column('device_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['device_id'], ['device.id'], ),
    sa.ForeignKeyConstraint(['pass_id'], ['pass.id'], )
    )
    op.create_unique_constraint(None, 'device', ['device_lib_id'])
    op.create_unique_constraint(None, 'device', ['id'])
    op.create_unique_constraint(None, 'device', ['push_token'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'device', type_='unique')
    op.drop_constraint(None, 'device', type_='unique')
    op.drop_constraint(None, 'device', type_='unique')
    op.drop_table('pass_device_association')
    # ### end Alembic commands ###
