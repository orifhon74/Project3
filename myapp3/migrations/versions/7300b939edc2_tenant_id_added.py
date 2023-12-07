"""tenant id added

Revision ID: 7300b939edc2
Revises: 5c398703ba75
Create Date: 2023-12-06 19:03:08.645928

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7300b939edc2'
down_revision = '5c398703ba75'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('maintenance_requests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tenant_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'tenants', ['tenant_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('maintenance_requests', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('tenant_id')

    # ### end Alembic commands ###
