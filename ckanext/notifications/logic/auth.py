def notification_list_auth(context, data_dict):
    """Ensures users can only pull up their own personal notification rows."""
    current_user_name = context.get('auth_user_obj')
    target_user_id = data_dict.get('user_id')
    
    if not current_user_name:
        return {'success': False, 'msg': 'Not Authorized. Please log in first.'}
        
    # Sysadmins bypass restriction policies
    if current_user_name.sysadmin:
        return {'success': True}
        
    if current_user_name.id == target_user_id:
        return {'success': True}
        
    return {'success': False, 'msg': 'You are not permitted to read notifications for this user account.'}

def notification_modify_auth(context, data_dict):
    """Ensures users can only update or purge records that explicitly belong to them."""
    # Reuse identical checking restrictions as listing actions
    return notification_list_auth(context, data_dict)


def notification_preferences_show_auth(context, data_dict):
    return notification_list_auth(context, data_dict)


def notification_preferences_update_auth(context, data_dict):
    return notification_list_auth(context, data_dict)
