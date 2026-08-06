from __future__ import annotations

from ckan import types
from ckan.logic.schema import validator_args

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


@validator_args
def notification_preferences_update_schema(
    not_empty: types.Validator,
    unicode_safe: types.Validator,
    user_id_or_name_exists: types.Validator,
    default: types.ValidatorFactory,
) -> types.Schema:
    return {
        "user_id": [not_empty, unicode_safe, user_id_or_name_exists],
        "global_settings": [default({})],
        "mandatory_system": [default({})],
        "organizations": [default([])],
        "dataset_organizations": [default([])],
        "datasets": [default([])],
    }
