from ckan import types


def notification_list_auth(context: types.Context, data_dict: types.DataDict) -> types.AuthResult:
    """Ensures users can only pull up their own personal notification rows."""
    requested_user = data_dict.get("user_id")
    auth_user_obj = context.get("auth_user_obj")
    authenticated_user = context.get("user")

    if requested_user and auth_user_obj and requested_user in [auth_user_obj.id, auth_user_obj.name]:
        return {"success": True}

    if requested_user and authenticated_user == requested_user:
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
