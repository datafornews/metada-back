"""empty message

Revision ID: 78b6eab1a1a1
Revises: 39b09b7019e4
Create Date: 2017-11-15 17:38:05.651872

"""

# revision identifiers, used by Alembic.
revision = '78b6eab1a1a1'
down_revision = '39b09b7019e4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('wikidatas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('entity_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('lang', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['entity_id'], ['entities.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_column('entities', 'wiki')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('entities', sa.Column('wiki', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_table('wikidatas')
    # ### end Alembic commands ###