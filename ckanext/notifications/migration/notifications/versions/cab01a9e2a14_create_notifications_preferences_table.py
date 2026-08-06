"""Create notifications preferences table

Revision ID: cab01a9e2a14
Revises: 1375f8c0b374
Create Date: 2026-06-15 11:30:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "cab01a9e2a14"
down_revision = "1375f8c0b374"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "notifications_preferences",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=False),
        sa.Column("scope_type", sa.String(length=32), nullable=False),
        sa.Column("scope_id", sa.String(length=100), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("email_enabled", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("in_app_enabled", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("mandatory", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "scope_type", "scope_id", name="uq_notifications_preferences_scope"),
    )

    op.create_index("idx_notifications_preferences_user_id", "notifications_preferences", ["user_id"], unique=False)
    op.create_index(
        "idx_notifications_preferences_scope_type", "notifications_preferences", ["scope_type"], unique=False
    )


def downgrade():
    op.drop_index("idx_notifications_preferences_scope_type", table_name="notifications_preferences")
    op.drop_index("idx_notifications_preferences_user_id", table_name="notifications_preferences")
    op.drop_table("notifications_preferences")
