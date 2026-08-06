import logging
from typing import Any

from flask import Blueprint, Response, redirect, render_template, request
from flask.views import MethodView
from werkzeug.datastructures import ImmutableMultiDict

from ckan import model
from ckan.lib.pagination import Page
from ckan.plugins import toolkit as tk
from ckan.types import Context

from ckanext.notifications.config import notifications_get_notifications_per_page

log = logging.getLogger(__name__)

notifications_blueprint = Blueprint("notifications", __name__)


def _get_user_or_404(user_id: str) -> model.User:
    """Safely resolves an active CKAN User object or errors out."""
    user = model.User.get(user_id)
    if not user:
        return tk.abort(404, "User account not found.")
    return user


def _is_checked(data: ImmutableMultiDict[str, str], key: str) -> bool:
    values = data.getlist(key)

    if not values:
        return False

    return any(value in ("1", "true", "True", "on", "yes") for value in values)


def _get_context() -> Context:
    return {
        "model": model,
        "session": model.Session,
        "user": tk.c.user or tk.c.author,
        "auth_user_obj": tk.c.userobj,
    }


class DashboardView(MethodView):
    """Renders the custom 'Notifications' management tab on a user's profile.

    Processes sorting and filtering metrics alongside massive bulk mutations.
    """

    def _check_access(self, context: Context, user_obj: model.User) -> None:
        try:
            tk.check_access("notification_list_auth", context, {"user_id": user_obj.id})
        except tk.NotAuthorized:
            tk.abort(403, "Unauthorized to view this dashboard.")

    def _apply_bulk_action(self, context: Context, user_obj: model.User) -> None:
        action_type_values = request.form.getlist("action_type")
        action_type = action_type_values[-1] if action_type_values else request.form.get("bulk_action_type")
        selected_ids = request.form.getlist("notification_ids")

        try:
            if action_type in ["read", "unread", "delete"]:
                if selected_ids:
                    tk.get_action("notification_patch")(
                        context,
                        {
                            "user_id": user_obj.id,
                            "ids": selected_ids,
                            "action_type": action_type,
                        },
                    )
            elif action_type in ["mark_all_read", "delete_all"]:
                tk.get_action("notification_global_action")(context, {"user_id": user_obj.id, "action_type": action_type})
        except Exception:
            log.exception("Failed to execute UI bulk action request.")

    def _redirect_to_dashboard(self, user_id: str) -> Response:
        # Redirect clean to strip POST payload from navigation reloads
        redirect_params = {
            "type": request.form.get("type", ""),
            "sort": request.form.get("sort", "desc"),
            "page": request.form.get("page", 1),
            "limit": request.form.get("limit", 20),
        }
        redirect_params = {key: value for key, value in redirect_params.items() if value not in (None, "")}
        return redirect(tk.url_for("notifications.dashboard", user_id=user_id, **redirect_params))

    def _fetch_notifications_page(self, context: Context, user_obj: model.User) -> tuple[Page, str, str, int]:
        filter_type = request.args.get("type", "")
        sort_order = request.args.get("sort", "desc")
        default_limit = notifications_get_notifications_per_page()
        page = max(int(request.args.get("page", 1) or 1), 1)
        limit = max(int(request.args.get("limit", default_limit) or default_limit), 1)
        limit = min(limit, default_limit)

        action_params = {
            "user_id": user_obj.id,
            "sort_order": sort_order,
            "page": page,
            "limit": limit,
        }

        if filter_type:
            action_params["notification_type"] = filter_type

        try:
            notifications_page = tk.get_action("notification_list")(context, action_params)
        except tk.ValidationError:
            log.exception("Failed to fetch notifications list for a user.")
            notifications_page = Page([], page=page, items_per_page=limit)

        return notifications_page, filter_type, sort_order, limit

    def get(self, user_id: str) -> str:
        context = _get_context()
        user_obj = _get_user_or_404(user_id)
        self._check_access(context, user_obj)

        notifications_page, filter_type, sort_order, limit = self._fetch_notifications_page(context, user_obj)

        return render_template(
            "notifications/dashboard.html",
            extra_vars={
                "user_id": user_obj.id,
                "user_dict": tk.get_action("user_show")(context, {"id": user_obj.id}),
                "page": notifications_page,
                "notifications": notifications_page.items,
                "current_filter_type": filter_type,
                "current_sort_order": sort_order,
                "current_page": notifications_page.page,
                "current_limit": limit,
            },
        )

    def post(self, user_id: str) -> Response:
        context = _get_context()
        user_obj = _get_user_or_404(user_id)
        self._check_access(context, user_obj)

        self._apply_bulk_action(context, user_obj)

        return self._redirect_to_dashboard(user_id)


class PreferencesView(MethodView):
    def _check_access(self, context: Context, user_obj: model.User) -> None:
        try:
            tk.check_access("notification_preferences_show_auth", context, {"user_id": user_obj.id})
        except tk.NotAuthorized:
            tk.abort(
                403,
                tk._("You are not authorized to manage these notification preferences."),
            )

    def _build_organizations_payload(
        self, existing: dict[str, Any], org_has_enabled_dataset: set[str]
    ) -> list[dict[str, Any]]:
        organizations_payload: list[dict[str, Any]] = []

        for organization in existing.get("organizations", []):
            org_id = organization["id"]
            organizations_payload.append(
                {
                    "id": org_id,
                    "enabled": (_is_checked(request.form, f"org_enabled__{org_id}") or org_id in org_has_enabled_dataset),
                    "email_enabled": _is_checked(request.form, f"org_email__{org_id}"),
                    "in_app_enabled": _is_checked(request.form, f"org_in_app__{org_id}"),
                }
            )
        return organizations_payload

    def _build_dataset_organizations_payload(
        self, existing: dict[str, Any], org_has_enabled_dataset: set[str]
    ) -> list[dict[str, Any]]:
        dataset_organizations_payload: list[dict[str, Any]] = []

        for group in existing.get("dataset_groups", []):
            org_id = group["organization"]["id"]
            dataset_organizations_payload.append(
                {
                    "id": org_id,
                    "enabled": (
                        _is_checked(request.form, f"dataset_org_enabled__{org_id}") or org_id in org_has_enabled_dataset
                    ),
                }
            )

        return dataset_organizations_payload

    def _build_datasets_payload(self, existing: dict[str, Any]) -> list[dict[str, Any]]:
        datasets_payload: list[dict[str, Any]] = []

        for group in existing.get("dataset_groups", []):
            for dataset in group.get("datasets", []):
                dataset_id = dataset["id"]

                if not _is_checked(request.form, f"dataset_present__{dataset_id}"):
                    continue

                datasets_payload.append(
                    {
                        "id": dataset_id,
                        "enabled": _is_checked(request.form, f"dataset_enabled__{dataset_id}"),
                        "email_enabled": _is_checked(request.form, f"dataset_email__{dataset_id}"),
                        "in_app_enabled": _is_checked(request.form, f"dataset_in_app__{dataset_id}"),
                    }
                )

        return datasets_payload

    def _get_org_has_enabled_dataset(self, existing: dict[str, Any]) -> set[str]:
        org_has_enabled_dataset: set[str] = set()

        for group in existing.get("dataset_groups", []):
            org_id = group["organization"]["id"]
            for dataset in group.get("datasets", []):
                dataset_id = dataset["id"]
                if _is_checked(request.form, f"dataset_enabled__{dataset_id}"):
                    org_has_enabled_dataset.add(org_id)
                    break

        return org_has_enabled_dataset

    def get(self, user_id: str) -> str:
        context = _get_context()
        user_obj = _get_user_or_404(user_id)
        self._check_access(context, user_obj)

        preferences_data = tk.get_action("notification_preferences_show")(context, {"user_id": user_obj.id})
        user_dict = tk.get_action("user_show")(context, {"id": user_obj.id})

        return render_template(
            "notifications/preferences.html",
            user_dict=user_dict,
            preferences_data=preferences_data,
            can_edit_mandatory=bool(tk.c.userobj and tk.c.userobj.sysadmin),
        )

    def post(self, user_id: str) -> Response:
        context = _get_context()
        user_obj = _get_user_or_404(user_id)
        self._check_access(context, user_obj)

        existing = tk.get_action("notification_preferences_show")(context, {"user_id": user_obj.id})
        org_has_enabled_dataset = self._get_org_has_enabled_dataset(existing)

        tk.get_action("notification_preferences_update")(
            context,
            {
                "user_id": user_obj.id,
                "global_settings": {
                    "enabled": _is_checked(request.form, "global_enabled"),
                },
                "mandatory_system": {
                    "enabled": _is_checked(request.form, "mandatory_enabled"),
                },
                "organizations": self._build_organizations_payload(existing, org_has_enabled_dataset),
                "dataset_organizations": self._build_dataset_organizations_payload(existing, org_has_enabled_dataset),
                "datasets": self._build_datasets_payload(existing),
            },
        )
        tk.h.flash_success(tk._("Notification preferences updated"))
        return redirect(tk.url_for("notifications.preferences", user_id=user_obj.name))


notifications_blueprint.add_url_rule(
    "/user/<user_id>/notifications",
    view_func=DashboardView.as_view("dashboard"),
    methods=["GET", "POST"],
)
notifications_blueprint.add_url_rule(
    "/user/<user_id>/notification-preferences",
    view_func=PreferencesView.as_view("preferences"),
    methods=["GET", "POST"],
)


def get_blueprints():
    """Exposes the Flask Blueprint to CKAN for route registration."""
    return [notifications_blueprint]
