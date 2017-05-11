"""empty message

Revision ID: 623bfd3769bf
Revises: 7a5738e173a4
Create Date: 2017-05-10 07:24:26.109918

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '623bfd3769bf'
down_revision = '7a5738e173a4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('roles', sa.Column('privilege_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'roles', 'privileges', ['privilege_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'roles', type_='foreignkey')
    op.drop_column('roles', 'privilege_id')
    # ### end Alembic commands ###