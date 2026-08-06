from __future__ import annotations

from typing import Any

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text

from ckan.model import meta
from ckan.model.types import make_uuid

from .base import Base, now


class Notification(Base):
    """SQLAlchemy model representing the `notifications` table.

    Stores copies of all internal notifications and outgoing emails.
    """

    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=make_uuid)
    user_id = Column(
        String(100),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Types: 'dataset_update', 'organization_update', 'system'
    notification_type = Column(String(50), nullable=False)

    # Sources: 'internal_notification', 'email'
    source = Column(String(50), nullable=False)

    subject = Column(Text, nullable=False)
    body = Column(Text, nullable=False)  # Stores the full text or HTML content

    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=now, nullable=False, index=True)

    @classmethod
    def get(cls, notification_id: str) -> Notification | None:
        """Helper to fetch a single notification by ID using the current session."""
        return meta.Session.query(cls).filter(cls.id == notification_id).first()

    def dictize(self) -> dict[str, Any]:
        """Converts a SQLAlchemy notification instance into a plain dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "notification_type": self.notification_type,
            "source": self.source,
            "subject": self.subject,
            "body": self.body,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat(),
        }
