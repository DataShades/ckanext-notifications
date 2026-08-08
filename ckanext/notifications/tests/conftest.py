from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from alembic.util.exc import CommandError
from pytest_factoryboy import register

from ckan import model
from ckan.common import config as ckan_config
from ckan.tests import factories

from ckanext.notifications.model import Notification


@pytest.fixture
def clean_db(reset_db, migrate_db_for):
    reset_db()

    try:
        migrate_db_for("notifications")
    except CommandError as err:
        # CKAN 2.10 may fail to resolve plugin migration config in some
        # environments. Fall back to explicit alembic.ini path.
        if "No 'script_location' key found in configuration" not in str(err):
            raise

        migration_dir = Path(__file__).resolve().parents[1] / "migration" / "notifications"
        alembic_config = Config(str(migration_dir / "alembic.ini"))
        alembic_config.set_main_option("script_location", str(migration_dir))
        alembic_config.set_main_option("sqlalchemy.url", ckan_config["sqlalchemy.url"])
        command.upgrade(alembic_config, "head")

    try:
        migrate_db_for("activity")
    except CommandError as err:
        # On CKAN 2.10, activity may not expose a plugin migration repo.
        # Core db init already creates activity tables, so this is safe to skip.
        if "No 'script_location' key found in configuration" not in str(err):
            raise


@register(_name="user")
class UserFactory(factories.UserWithToken):
    pass


@pytest.fixture
def user_with_notifications(user: dict[str, Any]) -> dict[str, Any]:
    """Create a user with sample notifications."""
    for i in range(5):
        notif = Notification(
            user_id=user["id"],
            notification_type="system" if i % 2 == 0 else "dataset",
            source="email" if i % 2 == 0 else "flash",
            subject=f"Test Notification {i}",
            body=f"Test notification body {i}",
            is_read=i % 3 == 0,
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
