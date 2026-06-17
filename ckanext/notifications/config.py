from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk


NOTIFICATIONS_EMAIL_INTERCEPTION = "ckanext.notifications.email_interception"
NOTIFICATIONS_FLASH_INTERCEPTION = "ckanext.notifications.flash_interception"
NOTIFICATIONS_ACTIVITY_INTERCEPTION = "ckanext.notifications.activity_interception"
NOTIFICATIONS_DATASET_KEYWORDS = "ckanext.notifications.dataset_keywords"
NOTIFICATIONS_ORGANIZATION_KEYWORDS = "ckanext.notifications.organization_keywords"
NOTIFICATIONS_GROUP_KEYWORDS = "ckanext.notifications.group_keywords"
NOTIFICATIONS_DATASET_ENDPOINT_STARTSWITH = "ckanext.notifications.dataset_endpoint_startswith"
NOTIFICATIONS_RESOURCE_ENDPOINT_STARTSWITH = "ckanext.notifications.resource_endpoint_startswith"
NOTIFICATIONS_ORGANIZATION_ENDPOINT_STARTSWITH = "ckanext.notifications.organization_endpoint_startswith"
NOTIFICATIONS_GROUP_ENDPOINT_STARTSWITH = "ckanext.notifications.group_endpoint_startswith"
NOTIFICATIONS_PER_PAGE = "ckanext.notifications.notifications_per_page"
NOTIFICATIONS_MAX_PER_USER = "ckanext.notifications.max_notifications_per_user"
NOTIFICATIONS_CLEANUP_DAYS = "ckanext.notifications.cleanup_days"

NOTIFICATIONS_DEFAULT_EMAIL_INTERCEPTION = True
NOTIFICATIONS_DEFAULT_FLASH_INTERCEPTION = True
NOTIFICATIONS_DEFAULT_ACTIVITY_INTERCEPTION = False
NOTIFICATIONS_DEFAULT_DATASET_KEYWORDS = "dataset package resource"
NOTIFICATIONS_DEFAULT_ORGANIZATION_KEYWORDS = "organization organisation"
NOTIFICATIONS_DEFAULT_GROUP_KEYWORDS = "group"
NOTIFICATIONS_DEFAULT_DATASET_ENDPOINT_STARTSWITH = "dataset"
NOTIFICATIONS_DEFAULT_RESOURCE_ENDPOINT_STARTSWITH = "resource"
NOTIFICATIONS_DEFAULT_ORGANIZATION_ENDPOINT_STARTSWITH = "organization"
NOTIFICATIONS_DEFAULT_GROUP_ENDPOINT_STARTSWITH = "group"
NOTIFICATIONS_DEFAULT_PER_PAGE = 20
NOTIFICATIONS_DEFAULT_MAX_PER_USER = 1000
NOTIFICATIONS_DEFAULT_CLEANUP_DAYS = 90


def _get_config_list(key: str, default: Any) -> list[str]:
	value = tk.config.get(key, default)
	if isinstance(value, (list, tuple)):
		return [str(item).strip().lower() for item in value if str(item).strip()]
	return [item.strip().lower() for item in str(value).split() if item.strip()]


def _get_config_str(key: str, default: str) -> str:
	return str(tk.config.get(key, default) or default).strip().lower()


def _get_config_int(key: str, default: int) -> int:
	try:
		return int(tk.config.get(key, default))
	except (TypeError, ValueError):
		return default


def notifications_get_email_interception() -> bool:
	return tk.asbool(
		tk.config.get(
			NOTIFICATIONS_EMAIL_INTERCEPTION,
			NOTIFICATIONS_DEFAULT_EMAIL_INTERCEPTION,
		)
	)


def notifications_get_flash_interception() -> bool:
	return tk.asbool(
		tk.config.get(
			NOTIFICATIONS_FLASH_INTERCEPTION,
			NOTIFICATIONS_DEFAULT_FLASH_INTERCEPTION,
		)
	)


def notifications_get_activity_interception() -> bool:
	return tk.asbool(
		tk.config.get(
			NOTIFICATIONS_ACTIVITY_INTERCEPTION,
			NOTIFICATIONS_DEFAULT_ACTIVITY_INTERCEPTION,
		)
	)


def notifications_get_dataset_keywords() -> list[str]:
	return _get_config_list(
		NOTIFICATIONS_DATASET_KEYWORDS,
		NOTIFICATIONS_DEFAULT_DATASET_KEYWORDS,
	)


def notifications_get_organization_keywords() -> list[str]:
	return _get_config_list(
		NOTIFICATIONS_ORGANIZATION_KEYWORDS,
		NOTIFICATIONS_DEFAULT_ORGANIZATION_KEYWORDS,
	)


def notifications_get_group_keywords() -> list[str]:
	return _get_config_list(
		NOTIFICATIONS_GROUP_KEYWORDS,
		NOTIFICATIONS_DEFAULT_GROUP_KEYWORDS,
	)


def notifications_get_dataset_endpoint_startswith() -> str:
	return _get_config_str(
		NOTIFICATIONS_DATASET_ENDPOINT_STARTSWITH,
		NOTIFICATIONS_DEFAULT_DATASET_ENDPOINT_STARTSWITH,
	)


def notifications_get_resource_endpoint_startswith() -> str:
	return _get_config_str(
		NOTIFICATIONS_RESOURCE_ENDPOINT_STARTSWITH,
		NOTIFICATIONS_DEFAULT_RESOURCE_ENDPOINT_STARTSWITH,
	)


def notifications_get_organization_endpoint_startswith() -> str:
	return _get_config_str(
		NOTIFICATIONS_ORGANIZATION_ENDPOINT_STARTSWITH,
		NOTIFICATIONS_DEFAULT_ORGANIZATION_ENDPOINT_STARTSWITH,
	)


def notifications_get_group_endpoint_startswith() -> str:
	return _get_config_str(
		NOTIFICATIONS_GROUP_ENDPOINT_STARTSWITH,
		NOTIFICATIONS_DEFAULT_GROUP_ENDPOINT_STARTSWITH,
	)


def notifications_get_notifications_per_page() -> int:
	return max(
		_get_config_int(
			NOTIFICATIONS_PER_PAGE,
			NOTIFICATIONS_DEFAULT_PER_PAGE,
		),
		1,
	)


def notifications_get_max_notifications_per_user() -> int:
	return _get_config_int(
		NOTIFICATIONS_MAX_PER_USER,
		NOTIFICATIONS_DEFAULT_MAX_PER_USER,
	)


def notifications_get_cleanup_days() -> int:
	return _get_config_int(
		NOTIFICATIONS_CLEANUP_DAYS,
		NOTIFICATIONS_DEFAULT_CLEANUP_DAYS,
	)
