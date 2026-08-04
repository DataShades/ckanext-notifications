#########
Changelog
#########

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <http://keepachangelog.com>`_
and this project adheres to `Semantic Versioning <http://semver.org/>`_.

***********
1.1.0 - 2026-08-04
***********

Added
-----

- New config option ``ckanext.notifications.organization_followee_list`` to control
  which organizations are shown in notification preferences:
  followed organizations (``true``) vs organization membership list (``false``).
- Config declaration entry and README documentation for
  ``ckanext.notifications.organization_followee_list``.

Changed
-------

- Notification preferences organization source is now configurable via
  ``organization_followee_list``.
- Dataset-group organization metadata is resolved via ``organization_show`` when
  building preference payloads for followed datasets.

Fixed
-----

- Preferences UI now enforces global opt-out semantics client-side:
  enabling global opt-out disables and clears other preference switches/channels,
  and restores their disabled state when opt-out is turned off.
- Project version bumped from ``1.0.0`` to ``1.1.0``.
