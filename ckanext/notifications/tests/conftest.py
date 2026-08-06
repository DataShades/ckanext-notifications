"""Test utilities and fixtures for ckanext-notifications.

This module provides common utilities used across test suites.
"""

import pytest

from ckan import model
from ckan.tests import factories

from ckanext.notifications.model import Notification


@pytest.fixture
def user(clean_db):
    """Create a test user."""
    return factories.User()


@pytest.fixture
def user_with_notifications(user):
    """Create a user with sample notifications."""
    for i in range(5):
        notif = Notification(
            user_id=user["id"],
            notification_type="system" if i % 2 == 0 else "dataset",
            source="email" if i % 2 == 0 else "flash",
            subject=f"Test Notification {i}",
            body=f"Test notification body {i}",
            is_read=i % 3 == 0,  # type: ignore
        )
        model.Session.add(notif)
    model.Session.commit()
    return user


@pytest.fixture
def admin_user(clean_db):
    """Create an admin user."""
    return factories.User(sysadmin=True)


class NotificationTestHelper:
    """Helper class for notification tests."""

    @staticmethod
    def create_notification(user_id, **kwargs):
        """Create a single notification with default values."""
        defaults = {
            "notification_type": "system",
            "source": "email",
            "subject": "Test Notification",
            "body": "Test notification body",
        }
        defaults.update(kwargs)

        notif = Notification(user_id=user_id, **defaults)
        model.Session.add(notif)
        model.Session.commit()
        return notif

    @staticmethod
    def create_notifications(user_id, count=5, **kwargs):
        """Create multiple notifications."""
        notifications = []
        for i in range(count):
            notif_kwargs = kwargs.copy()
            notif_kwargs["subject"] = notif_kwargs.get("subject", f"Notification {i}")
            notif = NotificationTestHelper.create_notification(user_id, **notif_kwargs)
            notifications.append(notif)
        return notifications

    @staticmethod
    def get_user_notifications(user_id, is_read=None):
        """Get notifications for a user with optional read filter."""
        query = model.Session.query(Notification).filter(
            Notification.user_id == user_id  # type: ignore
        )
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
        return query.all()

    @staticmethod
    def get_notification_count(user_id, is_read=None):
        """Get count of notifications for a user."""
        return len(NotificationTestHelper.get_user_notifications(user_id, is_read))

    @staticmethod
    def mark_all_read(user_id):
        """Mark all notifications for a user as read."""
        model.Session.query(Notification).filter(
            Notification.user_id == user_id  # type: ignore
        ).update({Notification.is_read: True})
        model.Session.commit()

    @staticmethod
    def delete_all(user_id):
        """Delete all notifications for a user."""
        model.Session.query(Notification).filter(
            Notification.user_id == user_id  # type: ignore
        ).delete()
        model.Session.commit()


@pytest.fixture
def notification_helper():
    """Provide the notification test helper."""
    return NotificationTestHelper()
