import logging
from collections.abc import Callable
from typing import Any

from ckan import model, types
from ckan.plugins import toolkit as tk

from ckanext.notifications.config import notifications_get_activity_interception

log = logging.getLogger(__name__)


def get_unread_count_for_current_user():
    """Retrieves the count of unread notifications for the currently logged-in user.

    Safely used across templates like header navigation bars.
    """
    context = types.Context(
        model=model,
        session=model.Session,
        user=tk.g.user,
        auth_user_obj=tk.g.userobj,
    )

    if not tk.g.userobj:
        return 0

    try:
        return tk.get_action("notification_unread_count")(context, {"user_id": tk.g.userobj.id})
    except (KeyError, ValueError, TypeError) as e:
        log.warning("Failed to execute template helper unread count query: %s", e)
        return 0


def activity_interception_enabled():
    """Check if activity interception is enabled.

    Used in templates to conditionally show activity-related notification preferences.
    """
    return notifications_get_activity_interception()


def get_helpers() -> dict[str, Callable[..., Any]]:
    return {
        "get_unread_notification_count": get_unread_count_for_current_user,
        "activity_interception_enabled": activity_interception_enabled,
    }
