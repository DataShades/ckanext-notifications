import logging
from flask import Blueprint, render_template, request, redirect
from ckan.plugins import toolkit as tk
import ckan.model as model
from ckan.lib.pagination import Page
from ckan.types import Context

from ckanext.notifications.config import notifications_get_notifications_per_page

log = logging.getLogger(__name__)

notifications_blueprint = Blueprint('notifications', __name__)

def _get_user_or_404(user_id):
    """Safely resolves an active CKAN User object or errors out."""
    user = model.User.get(user_id)
    if not user:
        return tk.abort(404, 'User account not found.')
    return user


def _is_checked(data, key):
    values = data.getlist(key)
    if not values:
        return False
    return any(value in ('1', 'true', 'True', 'on', 'yes') for value in values)

@notifications_blueprint.route('/user/<user_id>/notifications', methods=['GET', 'POST'])
def dashboard(user_id):
    """
    Renders the custom 'Notifications' management tab on a user's profile.
    Processes sorting and filtering metrics alongside massive bulk mutations.
    """
    context: Context = {
        'model': model,
        'session': model.Session,
        'user': tk.c.user or tk.c.author,
        'auth_user_obj': tk.c.userobj
    }
    
    # Resolve targeted identity
    user_obj = _get_user_or_404(user_id)
    
    # Check authorization before executing any view logic
    try:
        tk.check_access('notification_list_auth', context, {'user_id': user_obj.id})
    except tk.NotAuthorized:
        return tk.abort(403, 'Unauthorized to view this dashboard.')

    if request.method == 'POST':
        action_type_values = request.form.getlist('action_type')
        action_type = action_type_values[-1] if action_type_values else request.form.get('bulk_action_type')
        selected_ids = request.form.getlist('notification_ids')
        
        try:
            if action_type in ['read', 'unread', 'delete']:
                if selected_ids:
                    tk.get_action('notification_patch')(
                        context, 
                        {'user_id': user_obj.id, 'ids': selected_ids, 'action_type': action_type}
                    )
            elif action_type in ['mark_all_read', 'delete_all']:
                tk.get_action('notification_global_action')(
                    context, 
                    {'user_id': user_obj.id, 'action_type': action_type}
                )
        except Exception as e:
            log.error(f"Failed to execute UI bulk action request: {str(e)}")
            
        # Redirect clean to strip POST payload from navigation reloads
        redirect_params = {
            'type': request.form.get('type', ''),
            'sort': request.form.get('sort', 'desc'),
            'page': request.form.get('page', 1),
            'limit': request.form.get('limit', 20),
        }
        redirect_params = {key: value for key, value in redirect_params.items() if value not in (None, '')}
        return redirect(tk.url_for('notifications.dashboard', user_id=user_id, **redirect_params))

    # Extract filter components from active URL request parameters
    filter_type = request.args.get('type', '')
    sort_order = request.args.get('sort', 'desc')
    default_limit = notifications_get_notifications_per_page()
    page = max(int(request.args.get('page', 1) or 1), 1)
    limit = max(int(request.args.get('limit', default_limit) or default_limit), 1)
    limit = min(limit, default_limit)

    # Invoke data fetch execution
    action_params = {
        'user_id': user_obj.id,
        'sort_order': sort_order,
        'page': page,
        'limit': limit,
    }
    if filter_type:
        action_params['notification_type'] = filter_type

    try:
        notifications_page = tk.get_action('notification_list')(context, action_params)
    except Exception as e:
        log.error(f"Failed to fetch notifications list: {str(e)}")
        notifications_page = Page([], page=page, items_per_page=limit)

    # 6. Deliver layout package context to Jinja
    extra_vars = {
        'user_id': user_obj.id,
        'user_dict': tk.get_action('user_show')(context, {'id': user_obj.id}),
        'page': notifications_page,
        'notifications': notifications_page.items,
        'current_filter_type': filter_type,
        'current_sort_order': sort_order,
        'current_page': notifications_page.page,
        'current_limit': limit,
    }
    
    return render_template('notifications/dashboard.html', **extra_vars)


@notifications_blueprint.route('/user/<user_id>/notification-preferences', methods=['GET', 'POST'])
def preferences(user_id):
    user_obj = _get_user_or_404(user_id)

    context: Context = {
        'model': model,
        'session': model.Session,
        'user': tk.c.user or tk.c.author,
        'auth_user_obj': tk.c.userobj
    }

    try:
        tk.check_access('notification_preferences_show_auth', context, {'user_id': user_obj.id})
    except tk.NotAuthorized:
        return tk.abort(403, tk._('You are not authorized to manage these notification preferences.'))

    user_id_db = user_obj.id

    if request.method == 'POST':
        existing = tk.get_action('notification_preferences_show')(context, {'user_id': user_id_db})

        org_has_enabled_dataset = set()
        for group in existing.get('dataset_groups', []):
            org_id = group['organization']['id']
            for dataset in group.get('datasets', []):
                dataset_id = dataset['id']
                if _is_checked(request.form, f'dataset_enabled__{dataset_id}'):
                    org_has_enabled_dataset.add(org_id)
                    break

        organizations_payload = []
        for organization in existing.get('organizations', []):
            org_id = organization['id']
            organizations_payload.append({
                'id': org_id,
                'enabled': (
                    _is_checked(request.form, f'org_enabled__{org_id}')
                    or org_id in org_has_enabled_dataset
                ),
                'email_enabled': _is_checked(request.form, f'org_email__{org_id}'),
                'in_app_enabled': _is_checked(request.form, f'org_in_app__{org_id}'),
            })

        dataset_organizations_payload = []
        for group in existing.get('dataset_groups', []):
            org_id = group['organization']['id']
            dataset_organizations_payload.append({
                'id': org_id,
                'enabled': (
                    _is_checked(request.form, f'dataset_org_enabled__{org_id}')
                    or org_id in org_has_enabled_dataset
                ),
            })

        datasets_payload = []
        for group in existing.get('dataset_groups', []):
            for dataset in group.get('datasets', []):
                dataset_id = dataset['id']

                if not _is_checked(request.form, f'dataset_present__{dataset_id}'):
                    continue

                datasets_payload.append({
                    'id': dataset_id,
                    'enabled': _is_checked(request.form, f'dataset_enabled__{dataset_id}'),
                    'email_enabled': _is_checked(request.form, f'dataset_email__{dataset_id}'),
                    'in_app_enabled': _is_checked(request.form, f'dataset_in_app__{dataset_id}'),
                })

        tk.get_action('notification_preferences_update')(context, {
            'user_id': user_id_db,
            'global_settings': {
                'enabled': _is_checked(request.form, 'global_enabled'),
            },
            'mandatory_system': {
                'enabled': _is_checked(request.form, 'mandatory_enabled'),
            },
            'organizations': organizations_payload,
            'dataset_organizations': dataset_organizations_payload,
            'datasets': datasets_payload,
        })
        tk.h.flash_success(tk._('Notification preferences updated'))
        return redirect(tk.url_for('notifications.preferences', user_id=user_obj.name))

    preferences_data = tk.get_action('notification_preferences_show')(context, {'user_id': user_id_db})
    user_dict = tk.get_action('user_show')(context, {'id': user_id_db})

    return render_template(
        'notifications/preferences.html',
        user_dict=user_dict,
        preferences_data=preferences_data,
        can_edit_mandatory=bool(tk.c.userobj and tk.c.userobj.sysadmin),
    )


def get_blueprints():
    """Exposes the Flask Blueprint to CKAN for route registration."""
    return [notifications_blueprint]
