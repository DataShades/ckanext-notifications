import ckan.plugins.toolkit as tk
from ckan import types


def notification_list_auth(context: types.Context, data_dict: types.DataDict) -> types.AuthResult:
    """Ensures users can only pull up their own personal notification rows."""
    if tk.check_access("user_edit", context, data_dict):
        return {"success": True}

    return {
        "success": False,
        "msg": "You are not permitted to read notifications for this user account.",
    }


def notification_modify_auth(context: types.Context, data_dict: types.DataDict) -> types.AuthResult:
    """Ensures users can only update or purge records that explicitly belong to them."""
    return notification_list_auth(context, data_dict)


def notification_preferences_show_auth(context: types.Context, data_dict: types.DataDict) -> types.AuthResult:
    return notification_list_auth(context, data_dict)


def notification_preferences_update_auth(context: types.Context, data_dict: types.DataDict) -> types.AuthResult:
    return notification_list_auth(context, data_dict)
