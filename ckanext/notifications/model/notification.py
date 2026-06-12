from __future__ import annotations

import uuid
import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text

from .base import Base


class Notification(Base):
    """
    SQLAlchemy model representing the `notifications` table.
    Stores copies of all internal notifications and outgoing emails.
    """
    __tablename__ = 'notifications'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(100), ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Types: 'dataset_update', 'organization_update', 'system'
    notification_type = Column(String(50), nullable=False)
    
    # Sources: 'internal_notification', 'email'
    source = Column(String(50), nullable=False)
    
    subject = Column(Text, nullable=False)
    body = Column(Text, nullable=False)  # Stores the full text or HTML content
    
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)

    def __init__(self, user_id, notification_type, source, subject, body):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.notification_type = notification_type
        self.source = source
        self.subject = subject
        self.body = body

    @classmethod
    def get(cls, notification_id):
        """Helper to fetch a single notification by ID using the current session."""
        from ckan.model import meta
        return meta.Session.query(cls).filter(cls.id == notification_id).first()
