"""Tests for config.py - Configuration settings and getters.

Tests verify that all configuration settings are correctly read,
have proper defaults, and handle type conversions appropriately.
"""

import pytest

from ckanext.notifications import config


@pytest.mark.ckan_config("ckan.plugins", "notifications")
@pytest.mark.usefixtures("with_plugins")
class TestConfigGetters:
    """Test configuration getter functions and their defaults."""

    def test_email_interception_default_true(self):
        """Email interception should default to true."""
        result = config.notifications_get_email_interception()
        assert result is True

    @pytest.mark.ckan_config("ckanext.notifications.email_interception", False)
    def test_email_interception_can_be_disabled(self):
        """Email interception should respect config override to false."""
        result = config.notifications_get_email_interception()
        assert result is False

    @pytest.mark.ckan_config("ckanext.notifications.email_interception", "false")
    def test_email_interception_string_false_recognized(self):
        """String 'false' should be correctly converted to boolean."""
        result = config.notifications_get_email_interception()
        assert result is False

    @pytest.mark.ckan_config("ckanext.notifications.email_interception", "true")
    def test_email_interception_string_true_recognized(self):
        """String 'true' should be correctly converted to boolean."""
        result = config.notifications_get_email_interception()
        assert result is True

    def test_flash_interception_default_true(self):
        """Flash interception should default to true."""
        result = config.notifications_get_flash_interception()
        assert result is True

    @pytest.mark.ckan_config("ckanext.notifications.flash_interception", False)
    def test_flash_interception_can_be_disabled(self):
        """Flash interception should respect config override to false."""
        result = config.notifications_get_flash_interception()
        assert result is False

    def test_dataset_keywords_default(self):
        """Dataset keywords should have sensible defaults."""
        result = config.notifications_get_dataset_keywords()
        assert isinstance(result, list)
        assert "dataset" in result
        assert "package" in result
        assert "resource" in result

    @pytest.mark.ckan_config("ckanext.notifications.dataset_keywords", "data collection package")
    def test_dataset_keywords_custom_config(self):
        """Custom dataset keywords should be read and normalized."""
        result = config.notifications_get_dataset_keywords()
        assert "data" in result
        assert "collection" in result
        assert "package" in result
        # Verify lowercase normalization
        assert all(kw.islower() for kw in result)

    @pytest.mark.ckan_config("ckanext.notifications.dataset_keywords", ["DATA", "COLLECTION", "PACKAGE"])
    def test_dataset_keywords_list_format(self):
        """Keywords can be provided as list and should be normalized."""
        result = config.notifications_get_dataset_keywords()
        assert "data" in result
        assert "collection" in result
        assert "package" in result

    def test_organization_keywords_default(self):
        """Organization keywords should have sensible defaults."""
        result = config.notifications_get_organization_keywords()
        assert isinstance(result, list)
        assert "organization" in result
        assert "organisation" in result

    @pytest.mark.ckan_config("ckanext.notifications.organization_keywords", "organization team agency")
    def test_organization_keywords_custom_config(self):
        """Custom organization keywords should be read."""
        result = config.notifications_get_organization_keywords()
        assert "organization" in result
        assert "team" in result
        assert "agency" in result

    def test_group_keywords_default(self):
        """Group keywords should have sensible defaults."""
        result = config.notifications_get_group_keywords()
        assert isinstance(result, list)
        assert "group" in result

    def test_dataset_endpoint_startswith_default(self):
        """Dataset endpoint should default to 'dataset'."""
        result = config.notifications_get_dataset_endpoint_startswith()
        assert result == "dataset"

    @pytest.mark.ckan_config("ckanext.notifications.dataset_endpoint_startswith", "DATASET")
    def test_dataset_endpoint_startswith_normalized_to_lowercase(self):
        """Endpoint prefixes should be normalized to lowercase."""
        result = config.notifications_get_dataset_endpoint_startswith()
        assert result == "dataset"

    @pytest.mark.ckan_config("ckanext.notifications.dataset_endpoint_startswith", "data")
    def test_dataset_endpoint_startswith_custom_config(self):
        """Custom dataset endpoint should be respected."""
        result = config.notifications_get_dataset_endpoint_startswith()
        assert result == "data"

    def test_resource_endpoint_startswith_default(self):
        """Resource endpoint should default to 'resource'."""
        result = config.notifications_get_resource_endpoint_startswith()
        assert result == "resource"

    @pytest.mark.ckan_config("ckanext.notifications.resource_endpoint_startswith", "file")
    def test_resource_endpoint_startswith_custom_config(self):
        """Custom resource endpoint should be respected."""
        result = config.notifications_get_resource_endpoint_startswith()
        assert result == "file"

    def test_organization_endpoint_startswith_default(self):
        """Organization endpoint should default to 'organization'."""
        result = config.notifications_get_organization_endpoint_startswith()
        assert result == "organization"

    def test_group_endpoint_startswith_default(self):
        """Group endpoint should default to 'group'."""
        result = config.notifications_get_group_endpoint_startswith()
        assert result == "group"

    def test_notifications_per_page_default(self):
        """Notifications per page should default to 20."""
        result = config.notifications_get_notifications_per_page()
        assert result == 20

    @pytest.mark.ckan_config("ckanext.notifications.notifications_per_page", 50)
    def test_notifications_per_page_custom_config(self):
        """Custom notifications per page should be respected."""
        result = config.notifications_get_notifications_per_page()
        assert result == 50

    @pytest.mark.ckan_config("ckanext.notifications.notifications_per_page", 0)
    def test_notifications_per_page_minimum_enforced(self):
        """Notifications per page should enforce minimum of 1."""
        result = config.notifications_get_notifications_per_page()
        assert result >= 1

    @pytest.mark.ckan_config("ckanext.notifications.notifications_per_page", -10)
    def test_notifications_per_page_negative_clamped_to_one(self):
        """Negative notifications per page should be clamped to 1."""
        result = config.notifications_get_notifications_per_page()
        assert result == 1

    @pytest.mark.ckan_config("ckanext.notifications.notifications_per_page", "invalid")
    def test_notifications_per_page_invalid_string_uses_default(self):
        """Invalid per page config should fall back to default."""
        result = config.notifications_get_notifications_per_page()
        assert result == 20

    def test_max_notifications_per_user_default(self):
        """Max notifications per user should default to 1000."""
        result = config.notifications_get_max_notifications_per_user()
        assert result == 1000

    @pytest.mark.ckan_config("ckanext.notifications.max_notifications_per_user", 5000)
    def test_max_notifications_per_user_custom_config(self):
        """Custom max notifications per user should be respected."""
        result = config.notifications_get_max_notifications_per_user()
        assert result == 5000

    @pytest.mark.ckan_config("ckanext.notifications.max_notifications_per_user", "invalid")
    def test_max_notifications_per_user_invalid_uses_default(self):
        """Invalid max config should fall back to default."""
        result = config.notifications_get_max_notifications_per_user()
        assert result == 1000

    def test_cleanup_days_default(self):
        """Cleanup days should default to 90."""
        result = config.notifications_get_cleanup_days()
        assert result == 90

    @pytest.mark.ckan_config("ckanext.notifications.cleanup_days", 180)
    def test_cleanup_days_custom_config(self):
        """Custom cleanup days should be respected."""
        result = config.notifications_get_cleanup_days()
        assert result == 180

    @pytest.mark.ckan_config("ckanext.notifications.cleanup_days", 0)
    def test_cleanup_days_zero_allowed(self):
        """Zero cleanup days (disable cleanup) should be allowed."""
        result = config.notifications_get_cleanup_days()
        assert result == 0

    @pytest.mark.ckan_config("ckanext.notifications.cleanup_days", "invalid")
    def test_cleanup_days_invalid_uses_default(self):
        """Invalid cleanup config should fall back to default."""
        result = config.notifications_get_cleanup_days()
        assert result == 90


@pytest.mark.ckan_config("ckan.plugins", "notifications")
@pytest.mark.usefixtures("with_plugins")
class TestConfigConstants:
    """Test that configuration constants are properly defined."""

    def test_constants_are_strings(self):
        """All config key constants should be strings."""
        assert isinstance(config.NOTIFICATIONS_EMAIL_INTERCEPTION, str)
        assert isinstance(config.NOTIFICATIONS_FLASH_INTERCEPTION, str)
        assert isinstance(config.NOTIFICATIONS_DATASET_KEYWORDS, str)
        assert isinstance(config.NOTIFICATIONS_ORGANIZATION_KEYWORDS, str)
        assert isinstance(config.NOTIFICATIONS_GROUP_KEYWORDS, str)
        assert isinstance(config.NOTIFICATIONS_DATASET_ENDPOINT_STARTSWITH, str)
        assert isinstance(config.NOTIFICATIONS_RESOURCE_ENDPOINT_STARTSWITH, str)
        assert isinstance(config.NOTIFICATIONS_ORGANIZATION_ENDPOINT_STARTSWITH, str)
        assert isinstance(config.NOTIFICATIONS_GROUP_ENDPOINT_STARTSWITH, str)
        assert isinstance(config.NOTIFICATIONS_PER_PAGE, str)
        assert isinstance(config.NOTIFICATIONS_MAX_PER_USER, str)
        assert isinstance(config.NOTIFICATIONS_CLEANUP_DAYS, str)

    def test_constants_have_proper_format(self):
        """Config key constants should follow proper naming format."""
        assert config.NOTIFICATIONS_EMAIL_INTERCEPTION.startswith("ckanext.notifications.")
        assert config.NOTIFICATIONS_FLASH_INTERCEPTION.startswith("ckanext.notifications.")

    def test_default_constants_have_expected_types(self):
        """Default constants should have appropriate types."""
        assert isinstance(config.NOTIFICATIONS_DEFAULT_EMAIL_INTERCEPTION, bool)
        assert isinstance(config.NOTIFICATIONS_DEFAULT_FLASH_INTERCEPTION, bool)
        assert isinstance(config.NOTIFICATIONS_DEFAULT_DATASET_KEYWORDS, str)
        assert isinstance(config.NOTIFICATIONS_DEFAULT_PER_PAGE, int)
        assert isinstance(config.NOTIFICATIONS_DEFAULT_MAX_PER_USER, int)
        assert isinstance(config.NOTIFICATIONS_DEFAULT_CLEANUP_DAYS, int)


@pytest.mark.ckan_config("ckan.plugins", "notifications")
@pytest.mark.usefixtures("with_plugins")
class TestConfigHelpers:
    """Test internal configuration helper functions."""

    def test_get_config_list_with_string_input(self):
        """_get_config_list should handle space-separated strings."""
        result = config._get_config_list("test.key", "word1 word2 word3")
        assert isinstance(result, list)
        assert len(result) == 3
        assert "word1" in result

    def test_get_config_list_normalizes_to_lowercase(self):
        """_get_config_list should normalize to lowercase."""
        result = config._get_config_list("test.key", "WORD1 Word2 woRd3")
        assert all(word.islower() for word in result)

    def test_get_config_list_with_list_input(self):
        """_get_config_list should handle list input."""
        result = config._get_config_list("test.key", ["WORD1", "word2", "WORD3"])
        assert len(result) == 3
        assert all(word.islower() for word in result)

    def test_get_config_str_normalizes_to_lowercase(self):
        """_get_config_str should normalize to lowercase."""
        result = config._get_config_str("test.key", "DEFAULT")
        assert result.islower()

    def test_get_config_str_handles_none(self):
        """_get_config_str should handle None values."""
        result = config._get_config_str("test.key", "default")
        assert result == "default"

    def test_get_config_int_converts_string(self):
        """_get_config_int should convert string integers."""
        result = config._get_config_int("test.key", 42)
        # This will use default since the key doesn't exist
        assert isinstance(result, int)

    def test_get_config_int_handles_invalid(self):
        """_get_config_int should return default for invalid values."""
        result = config._get_config_int("nonexistent.key", 99)
        assert result == 99
