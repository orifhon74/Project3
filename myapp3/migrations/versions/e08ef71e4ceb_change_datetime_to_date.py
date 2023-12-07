"""Change DateTime to Date

Revision ID: e08ef71e4ceb
Revises: 36b72e858406
Create Date: 2023-12-06 08:24:47.095447

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e08ef71e4ceb'
down_revision = '36b72e858406'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tenants', schema=None) as batch_op:
        batch_op.alter_column('check_in_date',
               existing_type=mysql.DATETIME(),
               type_=sa.Date(),
               existing_nullable=False)
        batch_op.alter_column('check_out_date',
               existing_type=mysql.DATETIME(),
               type_=sa.Date(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tenants', schema=None) as batch_op:
        batch_op.alter_column('check_out_date',
               existing_type=sa.Date(),
               type_=mysql.DATETIME(),
               existing_nullable=True)
        batch_op.alter_column('check_in_date',
               existing_type=sa.Date(),
               type_=mysql.DATETIME(),
               existing_nullable=False)

    # ### end Alembic commands ###