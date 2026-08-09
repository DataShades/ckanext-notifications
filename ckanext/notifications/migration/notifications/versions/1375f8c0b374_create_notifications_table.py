"""Create notifications table

Revision ID: 1375f8c0b374
Revises:
Create Date: 2026-06-10 13:16:40.910040

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1375f8c0b374"
down_revision = None
branch_labels = ("notifications",)
depends_on = None


def upgrade():
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=False),
        sa.Column("notification_type", sa.String(length=50), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("subject", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    # Creating indexes for efficient UI filtering
    op.create_index("idx_notification_user_id", "notifications", ["user_id"], unique=False)
    op.create_index("idx_notification_is_read", "notifications", ["is_read"], unique=False)
    op.create_index("idx_notification_created_at", "notifications", ["created_at"], unique=False)


def downgrade():
    op.drop_index("idx_notification_created_at", table_name="notifications")
    op.drop_index("idx_notification_is_read", table_name="notifications")
    op.drop_index("idx_notification_user_id", table_name="notifications")
    op.drop_table("notifications")
