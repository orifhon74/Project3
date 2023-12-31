"""Removed tenant_id from requests

Revision ID: 36b72e858406
Revises: 5602bb2b7d6c
Create Date: 2023-12-06 05:56:27.835289

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '36b72e858406'
down_revision = '5602bb2b7d6c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('maintenance_requests', schema=None) as batch_op:
        batch_op.drop_constraint('maintenance_requests_ibfk_1', type_='foreignkey')
        batch_op.drop_column('tenant_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('maintenance_requests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tenant_id', mysql.INTEGER(), autoincrement=False, nullable=False))
        batch_op.create_foreign_key('maintenance_requests_ibfk_1', 'tenants', ['tenant_id'], ['id'])

    # ### end Alembic commands ###
