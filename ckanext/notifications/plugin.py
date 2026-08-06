import ckan.plugins.toolkit as tk
from ckan import plugins as p
from ckan.common import CKANConfig

from ckanext.notifications.config import (
    notifications_get_email_interception,
    notifications_get_flash_interception,
)
from ckanext.notifications.helpers import get_helpers
from ckanext.notifications.interceptor import patch_ckan_flash, patch_ckan_mailer
from ckanext.notifications.logic.action import get_actions
from ckanext.notifications.views import get_blueprints


@tk.blanket.auth_functions
@tk.blanket.actions(get_actions)
@tk.blanket.blueprints(get_blueprints)
@tk.blanket.helpers(get_helpers)
class NotificationsPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)

    # IConfigurer

    def update_config(self, config_: CKANConfig):
        tk.add_template_directory(config_, "templates")
        tk.add_resource("assets", "notifications")

        if notifications_get_email_interception():
            patch_ckan_mailer()

        if notifications_get_flash_interception():
            patch_ckan_flash()
