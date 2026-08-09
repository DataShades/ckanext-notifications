from __future__ import annotations

from typing import cast

from ckan import types
from ckan.logic.schema import validator_args
from ckan.plugins import toolkit as tk

from ckanext.notifications.config import (
    notifications_get_notifications_per_page,
)


@validator_args
def notification_list_schema(
    not_empty: types.Validator,
    unicode_safe: types.Validator,
    user_id_or_name_exists: types.Validator,
    is_positive_integer: types.Validator,
    default: types.ValidatorFactory,
) -> types.Schema:
    return {
        "user_id": [not_empty, unicode_safe, user_id_or_name_exists],
        "notification_type": [default(""), unicode_safe],
        "sort_order": [default("desc"), not_empty, unicode_safe],
        "page": [default(1), not_empty, is_positive_integer],
        "limit": [
            default(notifications_get_notifications_per_page()),
            not_empty,
            is_positive_integer,
        ],
    }


@validator_args
def notification_patch_schema(
    not_empty: types.Validator,
    unicode_safe: types.Validator,
    user_id_or_name_exists: types.Validator,
) -> types.Schema:
    return {
        "user_id": [not_empty, unicode_safe, user_id_or_name_exists],
        "ids": [not_empty],
        "action_type": [not_empty, unicode_safe],
    }


@validator_args
def notification_global_action_schema(
    not_empty: types.Validator,
    unicode_safe: types.Validator,
    user_id_or_name_exists: types.Validator,
) -> types.Schema:
    return {
        "user_id": [not_empty, unicode_safe, user_id_or_name_exists],
        "action_type": [not_empty, unicode_safe],
    }


@validator_args
def notification_unread_count_schema(
    not_empty: types.Validator,
    unicode_safe: types.Validator,
    user_id_or_name_exists: types.Validator,
) -> types.Schema:
    return {
        "user_id": [not_empty, unicode_safe, user_id_or_name_exists],
    }


@validator_args
def notification_preferences_show_schema(
    not_empty: types.Validator,
    unicode_safe: types.Validator,
    user_id_or_name_exists: types.Validator,
) -> types.Schema:
    return {
        "user_id": [not_empty, unicode_safe, user_id_or_name_exists],
    }


def notification_preferences_update_schema() -> types.Schema:
    not_empty = cast(types.Validator, tk.get_validator("not_empty"))
    unicode_safe = cast(types.Validator, tk.get_validator("unicode_safe"))
    user_id_or_name_exists = cast(
        types.Validator, tk.get_validator("user_id_or_name_exists")
    )
    ignore_missing = cast(types.Validator, tk.get_validator("ignore_missing"))
    boolean_validator = cast(
        types.Validator, tk.get_validator("boolean_validator")
    )
    default = cast(types.ValidatorFactory, tk.get_validator("default"))

    return {
        "user_id": [not_empty, unicode_safe, user_id_or_name_exists],
        "global_settings": [default({})],
        "mandatory_system": [default({})],
        "organizations": {
            "id": [ignore_missing, unicode_safe],
            "enabled": [ignore_missing, boolean_validator],
            "email_enabled": [ignore_missing, boolean_validator],
            "in_app_enabled": [ignore_missing, boolean_validator],
        },
        "dataset_organizations": {
            "id": [ignore_missing, unicode_safe],
            "enabled": [ignore_missing, boolean_validator],
        },
        "datasets": {
            "id": [ignore_missing, unicode_safe],
            "enabled": [ignore_missing, boolean_validator],
            "email_enabled": [ignore_missing, boolean_validator],
            "in_app_enabled": [ignore_missing, boolean_validator],
        },
    }
