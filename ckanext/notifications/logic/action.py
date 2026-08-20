import logging
from collections import defaultdict
from typing import Any, cast

from sqlalchemy import desc

from ckan import model, types
from ckan.logic import validate
from ckan.plugins import toolkit as tk

from ckanext.notifications.config import (
    notifications_get_activity_interception,
    notifications_get_organization_followee_list,
)
from ckanext.notifications.interceptor import intercept_activity
from ckanext.notifications.logic import schema
from ckanext.notifications.model import Notification, NotificationPreference

NotificationModel = cast(Any, Notification)
NotificationPreferenceModel = cast(Any, NotificationPreference)

GLOBAL_SCOPE_ID = "__global__"
MANDATORY_SYSTEM_SCOPE_ID = "__system_mandatory__"

log = logging.getLogger(__name__)


@tk.side_effect_free
@validate(schema.notification_list_schema)
def notification_list(context: types.Context, data_dict: types.DataDict) -> types.DataDict:
    """Retrieves a filtered, ordered, paginated list of notifications for a specific user.

    Supported filters in data_dict: 'notification_type', 'sort_order' (asc/desc),
    'page', and 'limit'. Returns a CKAN Page object.
    """
    tk.check_access("notification_list_auth", context, data_dict)

    user_id = data_dict["user_id"]
    noti_type = data_dict["notification_type"]
    sort_order = data_dict["sort_order"]
    page = data_dict["page"]
    limit = data_dict["limit"]

    offset = (page - 1) * limit

    query = model.Session.query(Notification).filter(NotificationModel.user_id == user_id)

    if noti_type == "marked_read":
        query = query.filter(NotificationModel.is_read == True)  # noqa: E712
    elif noti_type == "marked_unread":
        query = query.filter(NotificationModel.is_read == False)  # noqa: E712
    elif noti_type:
        query = query.filter(NotificationModel.notification_type == noti_type)

    if sort_order == "desc":
        query = query.order_by(desc(NotificationModel.created_at))
    else:
        query = query.order_by(NotificationModel.created_at)

    total_count = query.count()
    items = [n.dictize() for n in query.offset(offset).limit(limit).all()]

    return {
        "items": items,
        "page": page,
        "total_items": total_count,
    }

@validate(schema.notification_patch_schema)
def notification_patch(context: types.Context, data_dict: types.DataDict) -> types.DataDict:
    """Updates status properties ('is_read') or completely removes records.

    Handles bulk requests by processing an array of string 'ids'.
    """
    tk.check_access("notification_modify_auth", context, data_dict)

    notification_ids = data_dict["ids"]
    action_type = data_dict["action_type"]
    user_id = data_dict["user_id"]

    query = model.Session.query(Notification).filter(
        NotificationModel.id.in_(notification_ids), NotificationModel.user_id == user_id
    )

    if action_type == "delete":
        query.delete(synchronize_session=False)
    elif action_type == "read":
        query.update({NotificationModel.is_read: True}, synchronize_session=False)
    elif action_type == "unread":
        query.update({NotificationModel.is_read: False}, synchronize_session=False)

    model.Session.commit()
    return {"success": True, "count": len(notification_ids)}


@validate(schema.notification_global_action_schema)
def notification_global_action(context: types.Context, data_dict: types.DataDict) -> types.DataDict:
    """Applies massive transformations targeting an entire collection scope.

    Options: 'mark_all_read' or 'delete_all'
    """
    tk.check_access("notification_modify_auth", context, data_dict)

    user_id = data_dict["user_id"]
    action_type = data_dict["action_type"]

    query = model.Session.query(Notification).filter(NotificationModel.user_id == user_id)

    if action_type == "delete_all":
        query.delete(synchronize_session=False)
    elif action_type == "mark_all_read":
        query.filter(NotificationModel.is_read == False).update(  # noqa: E712
            {NotificationModel.is_read: True}, synchronize_session=False
        )

    model.Session.commit()
    return {"success": True}


@tk.side_effect_free
@validate(schema.notification_unread_count_schema)
def notification_unread_count(context: types.Context, data_dict: types.DataDict) -> int:
    """Returns a simplified total integer count of unread items."""
    tk.check_access("notification_list_auth", context, data_dict)
    user_id = data_dict["user_id"]

    return (
        model.Session.query(Notification)
        .filter(
            NotificationModel.user_id == user_id,
            NotificationModel.is_read == False,  # noqa: E712
        )
        .count()
    )


def _normalize_channels(enabled: bool, email_enabled: bool, in_app_enabled: bool):
    if not enabled:
        return False, False, False

    # If the master toggle is on, and both channels are off, re-enable both.
    if not email_enabled and not in_app_enabled:
        return True, True, True

    return (
        bool(email_enabled or in_app_enabled),
        bool(email_enabled),
        bool(in_app_enabled),
    )


def _serialize_preference(user_id: str, scope_type: str, scope_id: str, mandatory: bool = False):
    return _get_or_create_preference(user_id, scope_type, scope_id, mandatory=mandatory).dictize()


def _get_or_create_preference(user_id: str, scope_type: str, scope_id: str, mandatory: bool = False) -> Any:
    for pref in list(model.Session.new) + list(model.Session.identity_map.values()):
        if not isinstance(pref, NotificationPreference):
            continue
        if pref.user_id == user_id and pref.scope_type == scope_type and pref.scope_id == scope_id:
            return pref

    pref = (
        model.Session.query(NotificationPreference)
        .filter(
            NotificationPreferenceModel.user_id == user_id,
            NotificationPreferenceModel.scope_type == scope_type,
            NotificationPreferenceModel.scope_id == scope_id,
        )
        .first()
    )

    if pref:
        return pref

    default_enabled = mandatory or scope_type != "global" or scope_id != GLOBAL_SCOPE_ID

    pref = NotificationPreference(
        user_id=user_id,
        scope_type=scope_type,
        scope_id=scope_id,
        enabled=default_enabled,
        email_enabled=default_enabled,
        in_app_enabled=default_enabled,
        mandatory=mandatory,
    )
    model.Session.add(pref)
    return pref


@tk.side_effect_free
@validate(schema.notification_preferences_show_schema)
def notification_preferences_show(context: types.Context, data_dict: types.DataDict) -> types.DataDict:
    tk.check_access("notification_preferences_show_auth", context, data_dict)

    user_id = data_dict["user_id"]
    action_context = types.Context(
        model=model,
        session=model.Session,
        user=context.get("user", ""),
        auth_user_obj=context.get("auth_user_obj"),
    )

    if notifications_get_organization_followee_list():
        organizations = tk.get_action('organization_followee_list')(
            action_context,
            {
                'id': user_id,
            },
        )
    else:
        organizations = tk.get_action('organization_list_for_user')(
            action_context,
            {
                'id': user_id,
                'permission': 'read',
                'include_dataset_count': False,
            },
        )

    followed_datasets: list[dict[str, Any]] = tk.get_action("dataset_followee_list")(
        types.Context(
            action_context,
            for_view=True,
            with_capacity=False,
        ),
        {"id": user_id},
    )

    grouped_datasets: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for dataset in followed_datasets:
        if dataset.get("state") != model.State.ACTIVE:
            continue

        owner_org = dataset.get("owner_org") or "__no_org__"
        grouped_datasets[owner_org].append(dataset)

    global_settings = _serialize_preference(user_id, "global", GLOBAL_SCOPE_ID)
    mandatory_system = _serialize_preference(
        user_id,
        "global",
        MANDATORY_SYSTEM_SCOPE_ID,
        mandatory=True,
    )

    organizations_payload: list[dict[str, Any]] = [
        {
            "id": org["id"],
            "name": org.get("name"),
            "title": org.get("title") or org.get("display_name") or org.get("name"),
            "description": org.get("description") or "",
            "preference": _serialize_preference(user_id, "organization", org["id"]),
        }
        for org in organizations
    ]

    dataset_groups = []

    for org_id, datasets in grouped_datasets.items():
        org = tk.get_action("organization_show")(
            action_context,
            {
                "id": org_id,
                "include_datasets": False,
            },
        )
        org_pref = _serialize_preference(user_id, "organization", org_id)
        dataset_org_pref = _serialize_preference(user_id, "dataset_organization", org_id)

        dataset_entries = []

        for dataset in datasets:
            dataset_pref = _serialize_preference(user_id, "dataset", dataset["id"])
            dataset_effective = {
                "enabled": bool(dataset_pref["enabled"] and org_pref["enabled"]),
                "email_enabled": bool(dataset_pref["email_enabled"] and org_pref["email_enabled"]),
                "in_app_enabled": bool(dataset_pref["in_app_enabled"] and org_pref["in_app_enabled"]),
                "mandatory": False,
            }

            dataset_entries.append(
                {
                    "id": dataset["id"],
                    "name": dataset.get("name"),
                    "title": dataset.get("title") or dataset.get("name"),
                    "notes": dataset.get("notes") or "",
                    "preference": dataset_pref,
                    "effective_preference": dataset_effective,
                }
            )

        dataset_groups.append(
            {
                "organization": {
                    "id": org_id,
                    "name": org.get("name") or org_id,
                    "title": org.get("title")
                    or org.get("display_name")
                    or org.get("name")
                    or tk._("Unknown organization"),
                },
                "organization_preference": org_pref,
                "preference": dataset_org_pref,
                "datasets": dataset_entries,
            }
        )

    return {
        "global_settings": global_settings,
        "mandatory_system": mandatory_system,
        "organizations": organizations_payload,
        "dataset_groups": dataset_groups,
    }


@validate(schema.notification_preferences_update_schema)
def notification_preferences_update(context: types.Context, data_dict: types.DataDict) -> types.DataDict:
    tk.check_access("notification_preferences_update_auth", context, data_dict)

    user_id = data_dict["user_id"]

    global_settings = data_dict.get("global_settings", {})
    enabled = bool(global_settings.get("enabled", True))
    global_pref = _get_or_create_preference(user_id, "global", GLOBAL_SCOPE_ID)
    global_pref.enabled = enabled
    global_pref.email_enabled = enabled
    global_pref.in_app_enabled = enabled

    mandatory_payload = data_dict.get("mandatory_system", {})
    mandatory_pref = _get_or_create_preference(
        user_id,
        "global",
        MANDATORY_SYSTEM_SCOPE_ID,
        mandatory=True,
    )

    auth_user = context.get("auth_user_obj")
    is_sysadmin = bool(auth_user and getattr(auth_user, "sysadmin", False))
    if is_sysadmin and mandatory_payload:
        m_enabled = bool(mandatory_payload.get("enabled", True))
        mandatory_pref.enabled = m_enabled
        mandatory_pref.email_enabled = m_enabled
        mandatory_pref.in_app_enabled = m_enabled

    for organization in data_dict.get("organizations", []):
        org_id = organization.get("id")
        if not org_id:
            continue

        org_enabled = bool(organization.get("enabled", True))
        org_email_enabled = bool(organization.get("email_enabled", org_enabled))
        org_in_app_enabled = bool(organization.get("in_app_enabled", org_enabled))

        if not org_enabled:
            org_email_enabled = False
            org_in_app_enabled = False

        org_pref = _get_or_create_preference(user_id, "organization", org_id)
        org_pref.enabled = org_enabled
        org_pref.email_enabled = org_email_enabled
        org_pref.in_app_enabled = org_in_app_enabled

    for dataset_org in data_dict.get("dataset_organizations", []):
        org_id = dataset_org.get("id")
        if not org_id:
            continue

        org_enabled = bool(dataset_org.get("enabled", True))
        org_pref = _get_or_create_preference(user_id, "dataset_organization", org_id)
        org_pref.enabled = org_enabled
        org_pref.email_enabled = org_enabled
        org_pref.in_app_enabled = org_enabled

    for dataset in data_dict.get("datasets", []):
        dataset_id = dataset.get("id")
        if not dataset_id:
            continue

        ds_enabled, ds_email, ds_in_app = _normalize_channels(
            bool(dataset.get("enabled", True)),
            bool(dataset.get("email_enabled", True)),
            bool(dataset.get("in_app_enabled", True)),
        )
        ds_pref = _get_or_create_preference(user_id, "dataset", dataset_id)
        ds_pref.enabled = ds_enabled
        ds_pref.email_enabled = ds_email
        ds_pref.in_app_enabled = ds_in_app

    model.Session.commit()
    return {"success": True}


@tk.chained_action
def activity_create(original_action: types.Action, context: types.Context, data_dict: types.DataDict) -> types.DataDict:
    """Chained action that intercepts 'activity_create' executions for the notifications dashboard."""
    # Execute core function first to ensure data validation passes
    executed_activity = original_action(context, data_dict)

    if notifications_get_activity_interception():
        try:
            intercept_activity(executed_activity, context)
        except (OSError, ValueError, KeyError):
            log.exception("Failed to process activity logging")

    return executed_activity


def get_actions() -> dict[str, types.Action | types.ChainedAction]:
    return {
        "notification_list": notification_list,
        "notification_patch": notification_patch,
        "notification_global_action": notification_global_action,
        "notification_unread_count": notification_unread_count,
        "notification_preferences_show": notification_preferences_show,
        "notification_preferences_update": notification_preferences_update,
        "activity_create": activity_create,
    }
