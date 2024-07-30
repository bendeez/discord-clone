"""added models

Revision ID: 3c7eeaa0751d
Revises:
Create Date: 2024-04-18 20:33:30.098579

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3c7eeaa0751d"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=True),
        sa.Column("profile", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "dms",
        sa.Column("sender", sa.String(), nullable=False),
        sa.Column("receiver", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["receiver"], ["users.username"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sender"], ["users.username"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "friendrequests",
        sa.Column("sender", sa.String(), nullable=False),
        sa.Column("receiver", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["receiver"], ["users.username"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sender"], ["users.username"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "friends",
        sa.Column("sender", sa.String(), nullable=False),
        sa.Column("receiver", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["receiver"], ["users.username"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sender"], ["users.username"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "server",
        sa.Column("owner", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("profile", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["owner"], ["users.username"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "dm_messages",
        sa.Column("link", sa.String(), nullable=True),
        sa.Column("text", sa.String(), nullable=True),
        sa.Column("file", sa.String(), nullable=True),
        sa.Column("filetype", sa.String(), nullable=True),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("dm", sa.Integer(), nullable=False),
        sa.Column("serverinviteid", sa.Integer(), nullable=True),
        sa.Column("created_date", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["dm"], ["dms.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["serverinviteid"],
            ["server.id"],
        ),
        sa.ForeignKeyConstraint(["username"], ["users.username"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "notifications",
        sa.Column("sender", sa.String(), nullable=False),
        sa.Column("receiver", sa.String(), nullable=False),
        sa.Column("dm", sa.Integer(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["dm"], ["dms.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["receiver"], ["users.username"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sender"], ["users.username"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "server_messages",
        sa.Column("announcement", sa.String(), nullable=True),
        sa.Column("text", sa.String(), nullable=True),
        sa.Column("file", sa.String(), nullable=True),
        sa.Column("filetype", sa.String(), nullable=True),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("server", sa.Integer(), nullable=False),
        sa.Column("created_date", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["server"], ["server.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["username"], ["users.username"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "server_user",
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["server_id"],
            ["server.id"],
        ),
        sa.ForeignKeyConstraint(["username"], ["users.username"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("server_user")
    op.drop_table("server_messages")
    op.drop_table("notifications")
    op.drop_table("dm_messages")
    op.drop_table("server")
    op.drop_table("friends")
    op.drop_table("friendrequests")
    op.drop_table("dms")
    op.drop_table("users")
    # ### end Alembic commands ###
