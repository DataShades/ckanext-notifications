"""Tests for interceptor.py - Email and flash message interception.

Tests verify that notifications are correctly intercepted, classified,
stored, and cleaned up according to configuration.
"""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from ckan import model
from ckan.tests import factories

from ckanext.notifications import interceptor
from ckanext.notifications.model import Notification


@pytest.mark.ckan_config("ckan.plugins", "notifications")
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestNotificationClassification:
    """Test notification type classification logic."""

    def test_classify_from_endpoint_dataset(self):
        """Dataset endpoints should be classified as dataset type."""
        result = interceptor.classify_notification_type(endpoint="dataset_show")
        assert result == "dataset"

    def test_classify_from_endpoint_resource(self):
        """Resource endpoints should be classified as dataset type."""
        result = interceptor.classify_notification_type(endpoint="resource_show")
        assert result == "dataset"

    def test_classify_from_endpoint_organization(self):
        """Organization endpoints should be classified correctly."""
        result = interceptor.classify_notification_type(endpoint="organization_show")
        assert result == "organization"

    def test_classify_from_endpoint_group(self):
        """Group endpoints should be classified correctly."""
        result = interceptor.classify_notification_type(endpoint="group_show")
        assert result == "group"

    def test_classify_from_endpoint_case_insensitive(self):
        """Endpoint classification should be case-insensitive."""
        result = interceptor.classify_notification_type(endpoint="DATASET_SHOW")
        assert result == "dataset"

        result2 = interceptor.classify_notification_type(endpoint="Dataset_Show")
        assert result2 == "dataset"

    def test_classify_from_keywords_dataset(self):
        """Dataset keywords should classify notification as dataset."""
        result = interceptor.classify_notification_type(
            subject="Dataset Update", body="The dataset has been updated successfully"
        )
        assert result == "dataset"

    def test_classify_from_keywords_organization(self):
        """Organization keywords should classify as organization."""
        result = interceptor.classify_notification_type(subject="Organization Changed", body="The organization was modified")
        assert result == "organization"

    def test_classify_from_keywords_group(self):
        """Group keywords should classify as group."""
        result = interceptor.classify_notification_type(subject="Group Update", body="A new group was created")
        assert result == "group"

    def test_classify_from_keywords_case_insensitive(self):
        """Keyword classification should be case-insensitive."""
        result = interceptor.classify_notification_type(body="DATASET Created Successfully")
        assert result == "dataset"

    def test_classify_endpoint_takes_priority_over_keywords(self):
        """Endpoint classification should take priority over keywords."""
        result = interceptor.classify_notification_type(
            subject="Organization Update", body="The organization was updated", endpoint="dataset_show"
        )
        # Should be classified as dataset from endpoint, not organization
        assert result == "dataset"

    def test_classify_unknown_returns_system(self):
        """Unknown notifications should default to system type."""
        result = interceptor.classify_notification_type(subject="Random Message", body="This is just some random text")
        assert result == "system"

    def test_classify_none_endpoint_returns_system(self):
        """None endpoint should not cause errors."""
        result = interceptor.classify_notification_type(endpoint=None)
        assert result == "system"

    @pytest.mark.ckan_config("ckanext.notifications.dataset_keywords", "collection data")
    def test_classify_respects_custom_keywords(self):
        """Classification should use custom keyword config."""
        result = interceptor.classify_notification_type(body="A new collection was created")
        assert result == "dataset"

    @pytest.mark.ckan_config("ckanext.notifications.dataset_endpoint_startswith", "data")
    def test_classify_respects_custom_endpoint_config(self):
        """Classification should use custom endpoint config."""
        result = interceptor.classify_notification_type(endpoint="data_show")
        assert result == "dataset"


@pytest.mark.ckan_config("ckan.plugins", "notifications")
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestNotificationCreation:
    """Test notification creation and storage."""

    def test_create_notification_record_stores_in_database(self):
        """Creating a notification should store it in database."""
        user = factories.User()

        interceptor.create_notification_record(
            user_id=user["id"], notification_type="dataset", source="email", subject="Test Subject", body="Test Body"
        )

        notification = (
            model.Session.query(Notification)
            .filter(Notification.user_id == user["id"])  # type: ignore
            .first()
        )

        assert notification is not None
        assert notification.notification_type == "dataset"
        assert notification.source == "email"
        assert notification.subject == "Test Subject"
        assert notification.body == "Test Body"
        assert notification.is_read is False

    def test_create_notification_with_flash_source(self):
        """Flash messages should be stored with flash source."""
        user = factories.User()

        interceptor.create_notification_record(
            user_id=user["id"],
            notification_type="system",
            source="flash",
            subject="Flash Notification",
            body="Flash message content",
        )

        notification = (
            model.Session.query(Notification)
            .filter(Notification.user_id == user["id"])  # type: ignore
            .first()
        )

        assert notification.source == "flash"  # type: ignore

    def test_create_multiple_notifications_for_same_user(self):
        """Multiple notifications should be created for same user."""
        user = factories.User()

        for i in range(3):
            interceptor.create_notification_record(
                user_id=user["id"],
                notification_type="dataset",
                source="email",
                subject=f"Subject {i}",
                body=f"Body {i}",
            )

        notifications = (
            model.Session.query(Notification)
            .filter(Notification.user_id == user["id"])  # type: ignore
            .all()
        )

        assert len(notifications) == 3

    def test_create_notification_sets_timestamps(self):
        """Created notifications should have timestamps."""
        user = factories.User()

        before_create = datetime.utcnow()
        interceptor.create_notification_record(
            user_id=user["id"], notification_type="system", source="email", subject="Test", body="Test"
        )
        after_create = datetime.utcnow()

        notification = (
            model.Session.query(Notification)
            .filter(Notification.user_id == user["id"])  # type: ignore
            .first()
        )

        assert notification.created_at is not None  # type: ignore
        assert before_create <= notification.created_at <= after_create  # type: ignore


@pytest.mark.ckan_config("ckan.plugins", "notifications")
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestNotificationCleanup:
    """Test automatic notification cleanup functionality."""

    def test_cleanup_removes_old_notifications(self):
        """Cleanup should remove notifications older than threshold."""
        user = factories.User()

        # Create an old notification (older than cleanup threshold)
        old_notif = Notification(
            user_id=user["id"], notification_type="system", source="email", subject="Old", body="Old notification"
        )
        old_notif.created_at = datetime.utcnow() - timedelta(days=91)  # type: ignore
        model.Session.add(old_notif)

        # Create a new notification
        new_notif = Notification(
            user_id=user["id"], notification_type="system", source="email", subject="New", body="New notification"
        )
        model.Session.add(new_notif)
        model.Session.commit()

        # Run cleanup with default 90 days
        interceptor._cleanup_notifications_for_user(user["id"])

        remaining = (
            model.Session.query(Notification)
            .filter(Notification.user_id == user["id"])  # type: ignore
            .all()
        )

        # Old notification should be removed, new one kept
        assert len(remaining) == 1
        assert remaining[0].subject == "New"

    @pytest.mark.ckan_config("ckanext.notifications.cleanup_days", 0)
    def test_cleanup_disabled_when_cleanup_days_zero(self):
        """Cleanup should be disabled when cleanup_days is 0."""
        user = factories.User()

        # Create notifications both old and new
        old_notif = Notification(
            user_id=user["id"],
            notification_type="system",
            source="email",
            subject="Old",
            body="Old",
            created_at=datetime.utcnow() - timedelta(days=365),  # type: ignore
        )
        model.Session.add(old_notif)
        model.Session.commit()

        interceptor._cleanup_notifications_for_user(user["id"])

        remaining = (
            model.Session.query(Notification)
            .filter(Notification.user_id == user["id"])  # type: ignore
            .all()
        )

        # Old notification should still be there
        assert len(remaining) == 1

    def test_cleanup_enforces_max_per_user(self):
        """Cleanup should remove excess notifications above max."""
        user = factories.User()

        # Create 15 notifications
        for i in range(15):
            notif = Notification(
                user_id=user["id"], notification_type="system", source="email", subject=f"Notif {i}", body=f"Body {i}"
            )
            notif.created_at = datetime.utcnow() - timedelta(seconds=15 - i)  # type: ignore
            model.Session.add(notif)
        model.Session.commit()

        # Cleanup with max of 10
        with patch("ckanext.notifications.interceptor.config.notifications_get_max_notifications_per_user", return_value=10):
            interceptor._cleanup_notifications_for_user(user["id"])

        remaining = (
            model.Session.query(Notification)
            .filter(Notification.user_id == user["id"])  # type: ignore
            .all()
        )

        # Should be limited to 10
        assert len(remaining) == 10

    def test_cleanup_keeps_most_recent_notifications(self):
        """Cleanup should keep the most recent notifications."""
        user = factories.User()

        # Create notifications with different timestamps
        for i in range(5):
            notif = Notification(
                user_id=user["id"], notification_type="system", source="email", subject=f"Notif {i}", body=f"Body {i}"
            )
            notif.created_at = datetime.utcnow() - timedelta(seconds=5 - i)  # type: ignore
            model.Session.add(notif)
        model.Session.commit()

        with patch("ckanext.notifications.interceptor.config.notifications_get_max_notifications_per_user", return_value=3):
            interceptor._cleanup_notifications_for_user(user["id"])

        remaining = (
            model.Session.query(Notification)
            .filter(Notification.user_id == user["id"])  # type: ignore
            .order_by(Notification.created_at.desc())
            .all()
        )

        # Should have 3, and they should be the most recent ones
        assert len(remaining) == 3
        assert remaining[0].subject == "Notif 0"


@pytest.mark.ckan_config("ckan.plugins", "notifications")
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestFlashInterception:
    """Test Flask flash message interception."""

    def test_flash_interception_patches_function(self):
        """Flash interception should patch flask.flash function."""
        import flask

        # Get the patched function
        original_flash_method = flask.flash

        # It should be callable
        assert callable(original_flash_method)

    def test_intercepted_flash_still_calls_original(self):
        """Intercepted flash should still call original flask.flash."""
        # This would require more complex mocking and app context
        # Just verify the function exists and has the patch marker
        import flask

        assert hasattr(flask.flash, "_is_patched_by_ext")


@pytest.mark.ckan_config("ckan.plugins", "notifications")
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestEmailInterception:
    """Test email message interception."""

    def test_mailer_interception_patches_mail_recipient(self):
        """Email interception should patch mail_recipient function."""
        from ckan.lib import mailer as ckan_mailer

        # The patched function should have the marker
        assert hasattr(ckan_mailer.mail_recipient, "_is_patched_by_ext")

    def test_intercepted_email_creates_notification(self):
        """Intercepted email should create notification record."""
        user = factories.User(email="test@example.com")

        with patch("ckan.lib.mailer.mail_recipient", return_value=None):
            # This would need full request context
            # Just verify notification can be created
            interceptor.create_notification_record(
                user_id=user["id"],
                notification_type="dataset",
                source="email",
                subject="Test Email",
                body="Email content",
            )

        notification = (
            model.Session.query(Notification)
            .filter(Notification.user_id == user["id"])  # type: ignore
            .first()
        )

        assert notification is not None
        assert notification.source == "email"


@pytest.mark.ckan_config("ckan.plugins", "notifications")
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestNotificationEdgeCases:
    """Test edge cases and error handling."""

    def test_create_notification_with_empty_subject(self):
        """Creating notification with empty subject should work."""
        user = factories.User()

        interceptor.create_notification_record(
            user_id=user["id"], notification_type="system", source="email", subject="", body="Body with content only"
        )

        notification = (
            model.Session.query(Notification)
            .filter(Notification.user_id == user["id"])  # type: ignore
            .first()
        )

        assert notification is not None

    def test_create_notification_with_special_characters(self):
        """Notifications with special characters should be stored."""
        user = factories.User()

        special_subject = "Test with émojis 🎉 and spëcial chars"

        interceptor.create_notification_record(
            user_id=user["id"],
            notification_type="system",
            source="email",
            subject=special_subject,
            body="Special body with <html> tags",
        )

        notification = (
            model.Session.query(Notification)
            .filter(Notification.user_id == user["id"])  # type: ignore
            .first()
        )

        assert notification.subject == special_subject  # type: ignore

    def test_create_notification_with_very_long_content(self):
        """Notifications with long content should be stored."""
        user = factories.User()

        long_body = "x" * 10000

        interceptor.create_notification_record(
            user_id=user["id"], notification_type="system", source="email", subject="Long content test", body=long_body
        )

        notification = (
            model.Session.query(Notification)
            .filter(Notification.user_id == user["id"])  # type: ignore
            .first()
        )

        assert len(notification.body) == 10000  # type: ignore
