import logging

import ckan.model as model
from ckan.plugins import toolkit as tk
from ckan.types import Context

from ckanext.notifications.config import notifications_get_activity_interception

log = logging.getLogger(__name__)

def get_unread_count_for_current_user():
    """
    Retrieves the count of unread notifications for the currently logged-in user.
    Safely used across templates like header navigation bars.
    """
    context: Context = {
        'model': model,
        'session': model.Session,
        'user': tk.g.user,
        'auth_user_obj': tk.g.userobj
    }
    
    if not tk.g.userobj:
        return 0
        
    try:
        count = tk.get_action('notification_unread_count')(
            context, 
            {'user_id': tk.g.userobj.id}
        )
        return count
    except (KeyError, ValueError, TypeError) as e:
        log.error(f"Error executing template helper unread count query: {e!s}")
        return 0


def activity_interception_enabled():
    """
    Check if activity interception is enabled.
    
    Used in templates to conditionally show activity-related notification preferences.
    """
    return notifications_get_activity_interception()


def get_helpers():
    return {
        'get_unread_notification_count': get_unread_count_for_current_user,
        'activity_interception_enabled': activity_interception_enabled,
    }
