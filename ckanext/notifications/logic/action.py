from sqlalchemy import desc
from typing import Any, cast

from ckan import model
from ckan.lib.pagination import Page
from ckan.plugins import toolkit as tk

from ckanext.notifications.config import notifications_get_notifications_per_page
from ckanext.notifications.model import Notification

NotificationModel = cast(Any, Notification)


def _dictize_notification(notification):
    """Converts a SQLAlchemy notification instance into a plain dictionary."""
    if not notification:
        return {}
    return {
        'id': notification.id,
        'user_id': notification.user_id,
        'notification_type': notification.notification_type,
        'source': notification.source,
        'subject': notification.subject,
        'body': notification.body,
        'is_read': notification.is_read,
        'created_at': notification.created_at.isoformat()
    }


@tk.side_effect_free
def notification_list(context, data_dict):
    """
    Retrieves a filtered, ordered, paginated list of notifications for a specific user.
    Supported filters in data_dict: 'notification_type', 'sort_order' (asc/desc),
    'page', and 'limit'. Returns a CKAN Page object.
    """
    tk.check_access('notification_list_auth', context, data_dict)
    
    user_id = data_dict.get('user_id')
    noti_type = data_dict.get('notification_type')
    sort_order = data_dict.get('sort_order', 'desc')
    default_limit = notifications_get_notifications_per_page()
    page = max(int(data_dict.get('page', 1) or 1), 1)
    limit = max(int(data_dict.get('limit', default_limit) or default_limit), 1)
    limit = min(limit, default_limit)
    offset = (page - 1) * limit
    
    query = model.Session.query(Notification).filter(NotificationModel.user_id == user_id)
    
    if noti_type == 'marked_read':
        query = query.filter(NotificationModel.is_read == True)  # noqa: E712
    elif noti_type == 'marked_unread':
        query = query.filter(NotificationModel.is_read == False)  # noqa: E712
    elif noti_type:
        query = query.filter(NotificationModel.notification_type == noti_type)
        
    if sort_order == 'desc':
        query = query.order_by(desc(NotificationModel.created_at))
    else:
        query = query.order_by(NotificationModel.created_at)

    total_count = query.count()
    items = [_dictize_notification(n) for n in query.offset(offset).limit(limit).all()]

    return Page(
        items,
        page=page,
        items_per_page=limit,
        item_count=total_count,
        presliced_list=True,
        user_id=user_id,
    )


def notification_patch(context, data_dict):
    """
    Updates status properties ('is_read') or completely removes records.
    Handles bulk requests by processing an array of string 'ids'.
    """
    tk.check_access('notification_modify_auth', context, data_dict)
    
    notification_ids = data_dict.get('ids', [])
    action_type = data_dict.get('action_type')
    user_id = data_dict.get('user_id')
    
    if not notification_ids or not action_type:
        raise tk.ValidationError({'message': 'Missing target ids or action_type state parameter.'})
        
    query = model.Session.query(Notification).filter(
        NotificationModel.id.in_(notification_ids),
        NotificationModel.user_id == user_id
    )
    
    if action_type == 'delete':
        query.delete(synchronize_session=False)
    elif action_type == 'read':
        query.update({NotificationModel.is_read: True}, synchronize_session=False)
    elif action_type == 'unread':
        query.update({NotificationModel.is_read: False}, synchronize_session=False)
        
    model.Session.commit()
    return {'success': True, 'count': len(notification_ids)}

def notification_global_action(context, data_dict):
    """
    Applies massive transformations targeting an entire collection scope.
    Options: 'mark_all_read' or 'delete_all'
    """
    tk.check_access('notification_modify_auth', context, data_dict)
    
    user_id = data_dict.get('user_id')
    action_type = data_dict.get('action_type')
    
    query = model.Session.query(Notification).filter(NotificationModel.user_id == user_id)
    
    if action_type == 'delete_all':
        query.delete(synchronize_session=False)
    elif action_type == 'mark_all_read':
        query.filter(NotificationModel.is_read == False).update( # noqa: E712
            {NotificationModel.is_read: True},
            synchronize_session=False
        )
        
    model.Session.commit()
    return {'success': True}

@tk.side_effect_free
def notification_unread_count(context, data_dict):
    """Returns a simplified total integer count of unread items."""
    tk.check_access('notification_list_auth', context, data_dict)
    user_id = data_dict.get('user_id')
    
    if not user_id:
        raise tk.ValidationError({'message': 'Missing user_id parameter.'})
    
    count = model.Session.query(Notification).filter(
        NotificationModel.user_id == user_id,
        NotificationModel.is_read == False  # noqa: E712
    ).count()
    
    return count


def get_actions():
    return {
        'notification_list': notification_list,
        'notification_patch': notification_patch,
        'notification_global_action': notification_global_action,
        'notification_unread_count': notification_unread_count
    }
