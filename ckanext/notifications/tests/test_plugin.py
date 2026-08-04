"""
Tests for plugin.py - Plugin initialization and lifecycle.

Tests verify that the plugin loads correctly, registers blueprints,
configures properly, and applies patches as expected.
"""

from unittest.mock import patch

import pytest

import ckanext.notifications.plugin as plugin_module


@pytest.mark.ckan_config("ckan.plugins", "notifications")
@pytest.mark.ckan_config(
    "ckanext.notifications.email_interception", True
)
@pytest.mark.usefixtures("with_plugins")
class TestPluginEmailInterception:
    """Test plugin email interception patching."""

    @patch("ckanext.notifications.plugin.patch_ckan_mailer")
    @patch("ckanext.notifications.plugin.patch_ckan_flash")
    @patch("ckanext.notifications.plugin.tk.add_template_directory")
    @patch("ckanext.notifications.plugin.tk.add_public_directory")
    @patch("ckanext.notifications.plugin.tk.add_resource")
    def test_plugin_patches_mailer_when_enabled(
        self,
        mock_add_resource,
        mock_add_public,
        mock_add_templates,
        mock_patch_flash,
        mock_patch_mailer
    ):
        """Plugin should patch mailer when email interception enabled."""
        plugin_obj = plugin_module.NotificationsPlugin()
        config = {}
        plugin_obj.update_config(config) # type: ignore
        
        # patch_ckan_mailer should be called
        assert mock_patch_mailer.called

    @patch("ckanext.notifications.plugin.patch_ckan_mailer")
    @patch("ckanext.notifications.plugin.patch_ckan_flash")
    @patch("ckanext.notifications.plugin.tk.add_template_directory")
    @patch("ckanext.notifications.plugin.tk.add_public_directory")
    @patch("ckanext.notifications.plugin.tk.add_resource")
    @pytest.mark.ckan_config(
        "ckanext.notifications.email_interception", False
    )
    def test_plugin_skips_mailer_patch_when_disabled(
        self,
        mock_add_resource,
        mock_add_public,
        mock_add_templates,
        mock_patch_flash,
        mock_patch_mailer
    ):
        """Plugin should not patch mailer when email interception disabled."""
        plugin_obj = plugin_module.NotificationsPlugin()
        config = {}
        plugin_obj.update_config(config) # type: ignore
        
        # patch_ckan_mailer should not be called
        assert not mock_patch_mailer.called


@pytest.mark.ckan_config("ckan.plugins", "notifications")
@pytest.mark.ckan_config(
    "ckanext.notifications.flash_interception", True
)
@pytest.mark.usefixtures("with_plugins")
class TestPluginFlashInterception:
    """Test plugin flash message interception patching."""

    @patch("ckanext.notifications.plugin.patch_ckan_mailer")
    @patch("ckanext.notifications.plugin.patch_ckan_flash")
    @patch("ckanext.notifications.plugin.tk.add_template_directory")
    @patch("ckanext.notifications.plugin.tk.add_public_directory")
    @patch("ckanext.notifications.plugin.tk.add_resource")
    def test_plugin_patches_flash_when_enabled(
        self,
        mock_add_resource,
        mock_add_public,
        mock_add_templates,
        mock_patch_flash,
        mock_patch_mailer
    ):
        """Plugin should patch flask.flash when flash interception enabled."""
        plugin_obj = plugin_module.NotificationsPlugin()
        config = {}
        plugin_obj.update_config(config) # type: ignore
        
        # patch_ckan_flash should be called
        assert mock_patch_flash.called

    @patch("ckanext.notifications.plugin.patch_ckan_mailer")
    @patch("ckanext.notifications.plugin.patch_ckan_flash")
    @patch("ckanext.notifications.plugin.tk.add_template_directory")
    @patch("ckanext.notifications.plugin.tk.add_public_directory")
    @patch("ckanext.notifications.plugin.tk.add_resource")
    @pytest.mark.ckan_config(
        "ckanext.notifications.flash_interception", False
    )
    def test_plugin_skips_flash_patch_when_disabled(
        self,
        mock_add_resource,
        mock_add_public,
        mock_add_templates,
        mock_patch_flash,
        mock_patch_mailer
    ):
        """Plugin should not patch flash when flash interception disabled."""
        plugin_obj = plugin_module.NotificationsPlugin()
        config = {}
        plugin_obj.update_config(config) # type: ignore
        
        # patch_ckan_flash should not be called
        assert not mock_patch_flash.called
