"""Make timestamp columns timezone-aware

Revision ID: d4e5f6a7b8c9
Revises: cab01a9e2a14
Create Date: 2026-08-06 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d4e5f6a7b8c9"
down_revision = "cab01a9e2a14"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "notifications",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "notifications_preferences",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "notifications_preferences",
        "updated_at",
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
    )


def downgrade():
    op.alter_column(
        "notifications_preferences",
        "updated_at",
        type_=sa.DateTime(),
        existing_nullable=False,
    )
    op.alter_column(
        "notifications_preferences",
        "created_at",
        type_=sa.DateTime(),
        existing_nullable=False,
    )
    op.alter_column(
        "notifications",
        "created_at",
        type_=sa.DateTime(),
        existing_nullable=False,
    )
