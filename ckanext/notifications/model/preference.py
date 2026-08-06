from __future__ import annotations

import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint

from .base import Base


class NotificationPreference(Base):
    __tablename__ = "notifications_preferences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(100), ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)

    # global / organization / dataset
    scope_type = Column(String(32), nullable=False, index=True)
    # For global settings this stores "__global__"
    scope_id = Column(String(100), nullable=False)

    enabled = Column(Boolean, nullable=False, default=True)
    email_enabled = Column(Boolean, nullable=False, default=True)
    in_app_enabled = Column(Boolean, nullable=False, default=True)
    mandatory = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    __table_args__ = (UniqueConstraint("user_id", "scope_type", "scope_id", name="uq_notifications_preferences_scope"),)
