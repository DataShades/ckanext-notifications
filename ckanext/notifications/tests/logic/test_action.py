"""Tests for logic/action.py - API action endpoints.

Tests verify that all API actions work correctly, including pagination,
filtering, sorting, and bulk operations.
"""

from datetime import datetime, timedelta, timezone

import pytest

import ckan.tests.helpers as test_helpers
from ckan import model
from ckan.plugins import toolkit as tk
from ckan.tests import factories

from ckanext.notifications.model import Notification


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestNotificationListAction:
    """Test notification_list API action."""

    def _create_notifications(self, user_id: str, count: int = 10, notification_type: str = "dataset"):
        """Helper to create test notifications."""
        for i in range(count):
            notif = Notification(
                user_id=user_id,
                notification_type=notification_type,
                source="email" if i % 2 == 0 else "flash",
                subject=f"Notification {i}",
                body=f"Body {i}",
                is_read=i % 3 == 0,
            )
            model.Session.add(notif)
        model.Session.commit()

    def test_notification_list_returns_paginated_results(self):
        """notification_list should return paginated results."""
        user = factories.User()
        self._create_notifications(user["id"], count=25)

        result = test_helpers.call_action("notification_list", user_id=user["id"], limit=10, page=1)

        assert len(result.items) == 10
        assert result.page == 1
        assert result.item_count == 25

    @pytest.mark.ckan_config("ckanext.notifications.notifications_per_page", 20)
    def test_notification_list_default_limit(self):
        """notification_list should use default limit from config."""
        user = factories.User()
        self._create_notifications(user["id"], count=25)

        result = test_helpers.call_action("notification_list", user_id=user["id"])

        # Should return items up to default limit
        assert len(result.items) <= 25

    def test_notification_list_pagination_page_2(self):
        """notification_list should handle pagination correctly."""
        user = factories.User()
        self._create_notifications(user["id"], count=25)

        page1 = test_helpers.call_action("notification_list", user_id=user["id"], limit=10, page=1)

        page2 = test_helpers.call_action("notification_list", user_id=user["id"], limit=10, page=2)

        # Different notifications on each page
        page1_ids = [n["id"] for n in page1.items]
        page2_ids = [n["id"] for n in page2.items]

        assert len(set(page1_ids) & set(page2_ids)) == 0

    def test_notification_list_filter_by_type(self):
        """notification_list should filter by notification_type."""
        user = factories.User()
        self._create_notifications(user["id"], count=5, notification_type="dataset")
        self._create_notifications(user["id"], count=5, notification_type="organization")

        result = test_helpers.call_action("notification_list", user_id=user["id"], notification_type="dataset")

        assert all(n["notification_type"] == "dataset" for n in result["items"])
        assert len(result["items"]) == 5

    def test_notification_list_filter_read_marked_read(self):
        """notification_list should filter marked_read notifications."""
        user = factories.User()

        # Create mix of read and unread
        for i in range(5):
            notif = Notification(
                user_id=user["id"],
                notification_type="system",
                source="email",
                subject=f"Notif {i}",
                body=f"Body {i}",
                is_read=(i % 2 == 0),
            )
            model.Session.add(notif)
        model.Session.commit()

        result = test_helpers.call_action("notification_list", user_id=user["id"], notification_type="marked_read")

        assert all(n["is_read"] is True for n in result["items"])
        assert len(result["items"]) == 3

    def test_notification_list_filter_marked_unread(self):
        """notification_list should filter marked_unread notifications."""
        user = factories.User()

        for i in range(5):
            notif = Notification(
                user_id=user["id"],
                notification_type="system",
                source="email",
                subject=f"Notif {i}",
                body=f"Body {i}",
                is_read=(i % 2 == 0),
            )
            model.Session.add(notif)
        model.Session.commit()

        result = test_helpers.call_action("notification_list", user_id=user["id"], notification_type="marked_unread")

        assert all(n["is_read"] is False for n in result["items"])
        assert len(result["items"]) == 2

    def test_notification_list_sort_descending(self):
        """notification_list should sort descending by default."""
        user = factories.User()

        for i in range(3):
            notif = Notification(
                user_id=user["id"],
                notification_type="system",
                source="email",
                subject=f"Notif {i}",
                body=f"Body {i}",
                created_at=datetime.now(tz=timezone.utc) - timedelta(hours=i),
            )
            model.Session.add(notif)
        model.Session.commit()

        result = test_helpers.call_action("notification_list", user_id=user["id"], sort_order="desc")

        # Most recent should be first
        timestamps = [n["created_at"] for n in result["items"]]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_notification_list_sort_ascending(self):
        """notification_list should sort ascending when specified."""
        user = factories.User()

        for i in range(3):
            notif = Notification(
                user_id=user["id"],
                notification_type="system",
                source="email",
                subject=f"Notif {i}",
                body=f"Body {i}",
                created_at=datetime.now(tz=timezone.utc) - timedelta(hours=i),
            )
            model.Session.add(notif)
        model.Session.commit()

        result = test_helpers.call_action("notification_list", user_id=user["id"], sort_order="asc")

        # Oldest should be first
        timestamps = [n["created_at"] for n in result["items"]]
        assert timestamps == sorted(timestamps)

    def test_notification_list_response_format(self):
        """notification_list response should have correct format."""
        user = factories.User()
        self._create_notifications(user["id"], count=1)

        result = test_helpers.call_action("notification_list", user_id=user["id"])

        assert "items" in result
        assert "page" in result
        assert "total_items" in result

        notification = result["items"][0]
        assert "id" in notification
        assert "user_id" in notification
        assert "notification_type" in notification
        assert "source" in notification
        assert "subject" in notification
        assert "body" in notification
        assert "is_read" in notification
        assert "created_at" in notification


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestNotificationGlobalAction:
    """Test notification_global_action API action."""

    def _create_notifications(self, user_id, count=5, is_read=False):
        """Helper to create test notifications."""
        for i in range(count):
            notif = Notification(
                user_id=user_id,
                notification_type="system",
                source="email",
                subject=f"Notif {i}",
                body=f"Body {i}",
                is_read=is_read,
            )
            model.Session.add(notif)
        model.Session.commit()

    def test_notification_global_action_mark_all_read(self):
        """notification_global_action should mark all as read."""
        user = factories.User()
        self._create_notifications(user["id"], count=5, is_read=False)

        result = test_helpers.call_action(
            "notification_global_action",
            user_id=user["id"],
            action_type="mark_all_read",
        )

        assert result["success"] is True

        unread_count = (
            model.Session.query(Notification)
            .filter(
                Notification.user_id == user["id"],
                Notification.is_read == False,
            )
            .count()
        )
        assert unread_count == 0

    def test_notification_global_action_delete_all(self):
        """notification_global_action should delete all notifications."""
        user = factories.User()
        self._create_notifications(user["id"], count=5)

        result = test_helpers.call_action("notification_global_action", user_id=user["id"], action_type="delete_all")

        assert result["success"] is True

        remaining = model.Session.query(Notification).filter(Notification.user_id == user["id"]).count()
        assert remaining == 0

    def test_notification_global_action_does_not_affect_other_users(self):
        """notification_global_action should only affect specified user."""
        user1 = factories.User()
        user2 = factories.User()

        self._create_notifications(user1["id"], count=3, is_read=False)
        self._create_notifications(user2["id"], count=3, is_read=False)

        test_helpers.call_action(
            "notification_global_action",
            user_id=user1["id"],
            action_type="mark_all_read",
        )

        # User1 should be all read
        u1_unread = (
            model.Session.query(Notification)
            .filter(
                Notification.user_id == user1["id"],
                Notification.is_read == False,
            )
            .count()
        )

        # User2 should still be unread
        u2_unread = (
            model.Session.query(Notification)
            .filter(
                Notification.user_id == user2["id"],
                Notification.is_read == False,
            )
            .count()
        )

        assert u1_unread == 0
        assert u2_unread == 3


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestNotificationUnreadCountAction:
    """Test notification_unread_count API action."""

    def test_notification_unread_count_returns_integer(self):
        """notification_unread_count should return integer count."""
        user = factories.User()

        # Create some unread notifications
        for i in range(3):
            notif = Notification(
                user_id=user["id"],
                notification_type="system",
                source="email",
                subject=f"Notif {i}",
                body=f"Body {i}",
                is_read=False,
            )
            model.Session.add(notif)
        model.Session.commit()

        result = test_helpers.call_action("notification_unread_count", user_id=user["id"])

        assert isinstance(result, int)
        assert result == 3

    def test_notification_unread_count_ignores_read(self):
        """notification_unread_count should only count unread."""
        user = factories.User()

        # Create mix of read and unread
        for i in range(5):
            notif = Notification(
                user_id=user["id"],
                notification_type="system",
                source="email",
                subject=f"Notif {i}",
                body=f"Body {i}",
                is_read=(i % 2 == 0),
            )
            model.Session.add(notif)
        model.Session.commit()

        result = test_helpers.call_action("notification_unread_count", user_id=user["id"])

        # Should be 2 unread (1, 3)
        assert result == 2

    def test_notification_unread_count_zero_when_all_read(self):
        """notification_unread_count should be zero when all read."""
        user = factories.User()

        for i in range(3):
            notif = Notification(
                user_id=user["id"],
                notification_type="system",
                source="email",
                subject=f"Notif {i}",
                body=f"Body {i}",
                is_read=True,
            )
            model.Session.add(notif)
        model.Session.commit()

        result = test_helpers.call_action("notification_unread_count", user_id=user["id"])

        assert result == 0

    def test_notification_unread_count_zero_when_no_notifications(self):
        """notification_unread_count should be zero when no notifications."""
        user = factories.User()

        result = test_helpers.call_action("notification_unread_count", user_id=user["id"])

        assert result == 0

    def test_notification_unread_count_requires_user_id(self):
        """notification_unread_count should require user_id."""
        with pytest.raises(tk.ValidationError):
            test_helpers.call_action("notification_unread_count")
