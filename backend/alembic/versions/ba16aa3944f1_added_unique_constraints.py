"""added unique constraints

Revision ID: ba16aa3944f1
Revises: 3db608281b6d
Create Date: 2024-06-04 15:25:38.811616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba16aa3944f1'
down_revision: Union[str, None] = '3db608281b6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'dms', ['sender', 'receiver'])
    op.create_unique_constraint(None, 'friendrequests', ['sender', 'receiver'])
    op.create_unique_constraint(None, 'friends', ['sender', 'receiver'])
    op.create_unique_constraint(None, 'notifications', ['sender', 'receiver'])
    op.create_unique_constraint(None, 'server_user', ['username', 'server_id'])
    op.drop_constraint('server_user_server_id_fkey', 'server_user', type_='foreignkey')
    op.create_foreign_key(None, 'server_user', 'server', ['server_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'server_user', type_='foreignkey')
    op.create_foreign_key('server_user_server_id_fkey', 'server_user', 'server', ['server_id'], ['id'])
    op.drop_constraint(None, 'server_user', type_='unique')
    op.drop_constraint(None, 'notifications', type_='unique')
    op.drop_constraint(None, 'friends', type_='unique')
    op.drop_constraint(None, 'friendrequests', type_='unique')
    op.drop_constraint(None, 'dms', type_='unique')
    # ### end Alembic commands ###
