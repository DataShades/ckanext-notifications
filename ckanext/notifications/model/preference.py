from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint

from ckan.model.types import make_uuid

from .base import Base, now


class NotificationPreference(Base):
    __tablename__ = "notifications_preferences"

    id = Column(String(36), primary_key=True, default=make_uuid)
    user_id = Column(
        String(100),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # global / organization / dataset
    scope_type = Column(String(32), nullable=False, index=True)
    # For global settings this stores "__global__"
    scope_id = Column(String(100), nullable=False)

    enabled = Column(Boolean, nullable=False, default=True)
    email_enabled = Column(Boolean, nullable=False, default=True)
    in_app_enabled = Column(Boolean, nullable=False, default=True)
    mandatory = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), nullable=False, default=now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now, onupdate=now)

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "scope_type",
            "scope_id",
            name="uq_notifications_preferences_scope",
        ),
    )

    def dictize(self) -> dict[str, bool]:
        return {
            "enabled": bool(self.enabled),
            "email_enabled": bool(self.email_enabled),
            "in_app_enabled": bool(self.in_app_enabled),
            "mandatory": bool(self.mandatory),
        }
