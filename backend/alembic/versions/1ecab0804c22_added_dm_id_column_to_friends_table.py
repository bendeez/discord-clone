"""added dm id column to friends table

Revision ID: 1ecab0804c22
Revises: 3c7eeaa0751d
Create Date: 2024-05-31 20:59:33.844196

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ecab0804c22'
down_revision: Union[str, None] = '3c7eeaa0751d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('friends', sa.Column('dm_id', sa.Integer(), nullable=True))
    op.execute("""UPDATE friends AS f SET dm_id = d.id FROM dms d 
                WHERE (f.sender = d.sender AND f.receiver = d.receiver) 
                OR (f.sender = d.receiver AND f.receiver = d.sender)""")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('friends', 'dm_id')
    # ### end Alembic commands ###
