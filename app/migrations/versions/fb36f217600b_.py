"""empty message

Revision ID: fb36f217600b
Revises: c808a9b03565
Create Date: 2019-02-24 02:37:37.766025

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb36f217600b'
down_revision = 'c808a9b03565'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('device', sa.Column('device_lib_id', sa.String(length=100), nullable=True))
    op.add_column('device', sa.Column('push_token', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('device', 'push_token')
    op.drop_column('device', 'device_lib_id')
    # ### end Alembic commands ###