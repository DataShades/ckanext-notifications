[![Tests](https://github.com/Datashades/ckanext-notifications/workflows/Tests/badge.svg?branch=main)](https://github.com/Datashades/ckanext-notifications/actions)
[![License](https://img.shields.io/badge/license-AGPL%203-blue.svg)](LICENSE)

# ckanext-notifications

A CKAN extension that provides a centralized notification center for users, intercepting and storing email and flash messages for easy access and management. This extension enables organizations to maintain a complete audit trail of user notifications while providing a unified dashboard for notification management.

## Features

- **Email Interception**: Automatically capture and store email messages sent to users
- **Flash Message Interception**: Intercept CKAN flash notifications for archival
- **Notification Classification**: Intelligent categorization based on endpoint and content keywords
- **Notification Dashboard**: User-friendly interface to view and manage notifications
- **Batch Operations**: Mark as read/unread or delete notifications in bulk
- **Automatic Cleanup**: Configurable retention policies with automatic old notification removal
- **RESTful API**: Full programmatic access to notification data
- **Flexible Configuration**: Extensive customization options for keywords and endpoints

## Requirements

- CKAN >= 2.9
- Python >= 3.7

### Compatibility with CKAN Versions

| CKAN version | Status              | Notes                                                    |
|--------------|---------------------|----------------------------------------------------------|
| 2.9          | Tested              | Full compatibility                                       |
| 2.10         | Tested              | Full compatibility                                       |
| 2.11         | Fully Compatible    | Latest tested version with all features supported        |

## Installation

### Prerequisites

Before installing, ensure you have:
- An active CKAN instance (version 2.9 or later)
- Access to your CKAN virtual environment
- Appropriate file system permissions for the installation directory

### Step-by-Step Installation

1. **Activate your CKAN virtual environment**:

   ```bash
   . /usr/lib/ckan/default/bin/activate
   ```

2. **Clone the source code**:

   ```bash
   git clone https://github.com/Datashades/ckanext-notifications.git
   cd ckanext-notifications
   ```

3. **Install the extension and dependencies**:

   ```bash
   pip install -e .
   pip install -r requirements.txt
   ```

4. **Add the plugin to your CKAN configuration**:

   Edit your CKAN configuration file (typically `/etc/ckan/default/ckan.ini` or `development.ini`):

   ```ini
   # Add notifications to the list of plugins
   ckan.plugins = ... notifications
   ```

5. **Restart CKAN**:

   For Apache/Supervisor deployments:
   ```bash
   sudo service apache2 reload
   # or
   sudo supervisorctl restart all
   ```

   For development mode:
   ```bash
   ckan run
   ```

## Configuration Settings

All configuration options are optional and use sensible defaults. Add these settings to your CKAN configuration file to customize the behavior.

### Email and Flash Interception

#### `ckanext.notifications.email_interception`

**Type**: Boolean  
**Default**: `true`  
**Description**: Enable or disable automatic interception and storage of email messages sent by CKAN.

```ini
# Example: Disable email interception
ckanext.notifications.email_interception = false
```

#### `ckanext.notifications.flash_interception`

**Type**: Boolean  
**Default**: `true`  
**Description**: Enable or disable automatic interception and storage of CKAN flash notifications.

```ini
# Example: Disable flash message interception
ckanext.notifications.flash_interception = false
```

### Content Classification

Notifications are automatically classified based on endpoint routing and keyword matching in message content. Configure these settings to customize the classification behavior.

#### `ckanext.notifications.dataset_keywords`

**Type**: Space-separated list  
**Default**: `dataset package resource`  
**Description**: Keywords used to identify dataset-related notifications when endpoint routing cannot determine the type.

```ini
# Example: Add custom dataset keywords
ckanext.notifications.dataset_keywords = dataset package resource data publication
```

#### `ckanext.notifications.organization_keywords`

**Type**: Space-separated list  
**Default**: `organization organisation`  
**Description**: Keywords used to identify organization-related notifications.

```ini
ckanext.notifications.organization_keywords = organization organisation team agency
```

#### `ckanext.notifications.group_keywords`

**Type**: Space-separated list  
**Default**: `group`  
**Description**: Keywords used to identify group-related notifications.

```ini
ckanext.notifications.group_keywords = group collection project category
```

### Endpoint-Based Classification

Notifications can be classified based on CKAN API endpoints. Configure these prefixes to match your routing setup.

#### `ckanext.notifications.dataset_endpoint_startswith`

**Type**: String  
**Default**: `dataset`  
**Description**: Endpoint prefix for dataset notifications.

```ini
ckanext.notifications.dataset_endpoint_startswith = dataset
```

#### `ckanext.notifications.resource_endpoint_startswith`

**Type**: String  
**Default**: `resource`  
**Description**: Endpoint prefix for resource (dataset file) notifications.

```ini
ckanext.notifications.resource_endpoint_startswith = resource
```

#### `ckanext.notifications.organization_endpoint_startswith`

**Type**: String  
**Default**: `organization`  
**Description**: Endpoint prefix for organization notifications.

```ini
ckanext.notifications.organization_endpoint_startswith = organization
```

#### `ckanext.notifications.group_endpoint_startswith`

**Type**: String  
**Default**: `group`  
**Description**: Endpoint prefix for group notifications.

```ini
ckanext.notifications.group_endpoint_startswith = group
```

### Display and Storage

#### `ckanext.notifications.notifications_per_page`

**Type**: Integer  
**Default**: `20`  
**Constraints**: Must be greater than 0  
**Description**: Maximum number of notifications displayed per page in the dashboard.

```ini
# Example: Show 50 notifications per page
ckanext.notifications.notifications_per_page = 50
```

#### `ckanext.notifications.max_notifications_per_user`

**Type**: Integer  
**Default**: `1000`  
**Description**: Maximum number of notifications to store per user. Oldest notifications beyond this limit are automatically deleted.

```ini
# Example: Keep maximum 5000 notifications per user
ckanext.notifications.max_notifications_per_user = 5000
```

#### `ckanext.notifications.cleanup_days`

**Type**: Integer  
**Default**: `90`  
**Description**: Number of days to retain notifications before automatic deletion. Notifications older than this threshold are automatically removed.

```ini
# Example: Keep notifications for 180 days (6 months)
ckanext.notifications.cleanup_days = 180
```

### Complete Configuration Example

Add this to your CKAN configuration file for full customization:

```ini
# Notification center configuration
ckanext.notifications.email_interception = true
ckanext.notifications.flash_interception = true

# Content classification keywords
ckanext.notifications.dataset_keywords = dataset package resource data
ckanext.notifications.organization_keywords = organization organisation team
ckanext.notifications.group_keywords = group collection project

# Endpoint-based classification
ckanext.notifications.dataset_endpoint_startswith = dataset
ckanext.notifications.resource_endpoint_startswith = resource
ckanext.notifications.organization_endpoint_startswith = organization
ckanext.notifications.group_endpoint_startswith = group

# Display and retention settings
ckanext.notifications.notifications_per_page = 20
ckanext.notifications.max_notifications_per_user = 1000
ckanext.notifications.cleanup_days = 90
```


## Usage

### Accessing the Notification Dashboard

Once installed and configured, users can access their notifications dashboard at:

```
http://your-ckan-instance/user/<username>/notifications
```

The dashboard provides:
- **Notification List**: View all intercepted email and flash messages
- **Filtering**: Filter notifications by type (email, flash, system)
- **Sorting**: Sort by date (ascending/descending)
- **Pagination**: Navigate through large notification lists
- **Bulk Actions**: Mark multiple notifications as read/unread or delete in bulk

### Notification Classification

Notifications are automatically classified into the following types:

| Type         | Source                                      | Classification Method                |
|--------------|---------------------------------------------|--------------------------------------|
| `dataset`    | Dataset/resource operations                 | Endpoint prefix or keyword matching  |
| `organization` | Organization operations                   | Endpoint prefix or keyword matching  |
| `group`      | Group/collection operations                 | Endpoint prefix or keyword matching  |
| `system`     | Other system notifications                  | Default classification              |

## API Reference

### Notification List Action

**Endpoint**: `POST /api/3/action/notification_list`

Retrieve a paginated list of notifications for a user.

**Parameters**:
- `user_id` (required): CKAN user ID or username
- `notification_type` (optional): Filter by type ('dataset', 'organization', 'group', 'marked_read', 'marked_unread')
- `sort_order` (optional): 'asc' or 'desc' (default: 'desc')
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: from config)

**Response**:
```json
{
  "items": [
    {
      "id": "uuid-string",
      "user_id": "user-uuid",
      "notification_type": "dataset",
      "source": "email",
      "subject": "Dataset Updated",
      "body": "The dataset has been successfully updated",
      "is_read": false,
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "page": 1,
  "total_items": 150
}
```

### Mark Notifications Action

**Endpoint**: `POST /api/3/action/notification_patch`

Update notification status or delete notifications.

**Parameters**:
- `user_id` (required): CKAN user ID
- `ids` (required): List of notification IDs to update
- `action_type` (required): 'read', 'unread', or 'delete'

**Request Example**:
```json
{
  "user_id": "user-uuid",
  "ids": ["notif-uuid-1", "notif-uuid-2"],
  "action_type": "read"
}
```

**Response**:
```json
{
  "success": true,
  "count": 2
}
```

### Global Notification Action

**Endpoint**: `POST /api/3/action/notification_global_action`

Apply bulk actions to all notifications for a user.

**Parameters**:
- `user_id` (required): CKAN user ID
- `action_type` (required): 'mark_all_read' or 'delete_all'

**Request Example**:
```json
{
  "user_id": "user-uuid",
  "action_type": "mark_all_read"
}
```

### Get Unread Count

**Endpoint**: `POST /api/3/action/notification_unread_count`

Get the count of unread notifications for a user.

**Parameters**:
- `user_id` (required): CKAN user ID

**Response**:
```json
25
```

## Developer Installation

### Prerequisites

- CKAN source code and virtual environment
- Git
- Python 3.7 or later
- PostgreSQL (for development database)

### Setup Steps

1. **Activate your CKAN development virtual environment**:

   ```bash
   . /path/to/ckan/venv/bin/activate
   ```

2. **Clone the repository**:

   ```bash
   git clone https://github.com/Datashades/ckanext-notifications.git
   cd ckanext-notifications
   ```

3. **Install in development mode**:

   ```bash
   pip install -e .
   pip install -r dev-requirements.txt
   ```

4. **Link to your CKAN installation**:

   Ensure the plugin is discoverable by CKAN:
   ```bash
   mkdir -p /path/to/ckan/src
   ln -s /path/to/ckanext-notifications /path/to/ckan/src/ckanext-notifications
   ```

5. **Configure for development**:

   Update your test configuration file to include the plugin and adjust settings as needed.

### Project Structure

```
ckanext-notifications/
├── ckanext/
│   └── notifications/
│       ├── config.py              # Configuration constants and getters
│       ├── plugin.py              # Main plugin class
│       ├── cli.py                 # CLI commands
│       ├── views.py               # Flask blueprints and routes
│       ├── helpers.py             # Template helper functions
│       ├── interceptor.py         # Email/flash message interception
│       ├── config_declaration.yaml # Configuration schema
│       ├── logic/
│       │   ├── action.py          # Action functions (API endpoints)
│       │   └── validators.py      # Input validation
│       ├── model.py               # Database model
│       ├── templates/
│       │   └── notifications/
│       │       └── dashboard.html # Main dashboard template
│       ├── public/
│       │   ├── css/               # Stylesheets
│       │   └── js/                # JavaScript files
│       ├── tests/                 # Test suite
│       └── assets/
│           └── webassets.yml      # Asset compilation config
├── README.md                        # This file
├── setup.py                         # Package setup
├── pyproject.toml                   # Project metadata
├── requirements.txt                 # Runtime dependencies
├── dev-requirements.txt             # Development dependencies
└── test.ini                         # Test configuration
```

## Testing

### Running Tests

Execute the test suite with pytest:

```bash
# Run all tests
pytest --ckan-ini=test.ini

# Run specific test file
pytest --ckan-ini=test.ini ckanext/notifications/tests/test_plugin.py

# Run with verbose output
pytest --ckan-ini=test.ini -v

# Run with code coverage
pytest --ckan-ini=test.ini --cov=ckanext.notifications --cov-report=html
```

### Test Organization

Tests are organized by functionality:

- `tests/test_plugin.py`: Plugin lifecycle and configuration
- `tests/test_views.py`: Dashboard views and routes
- `tests/logic/test_validators.py`: Input validation logic
- `tests/test_helpers.py`: Template helper functions

### Writing Tests

When adding new features, include tests that cover:

1. **Happy Path**: Normal operation with valid inputs
2. **Error Handling**: Invalid inputs and edge cases
3. **Authorization**: Permission checks and access control
4. **Integration**: Interaction with other CKAN components

Example test structure:

```python
"""Test notification listing functionality."""

import pytest
from ckan.plugins import toolkit as tk
from ckanext.notifications.tests.utils import factories


@pytest.mark.ckan_config('ckanext.notifications.notifications_per_page', 10)
def test_notification_list_respects_per_page_config(app, user):
    """Test that notifications_per_page config is respected."""
    # Arrange
    notifications = factories.create_notifications(user, count=25)
    
    # Act
    result = tk.get_action('notification_list')(
        {'user': user['id']},
        {'user_id': user['id'], 'limit': 10}
    )
    
    # Assert
    assert len(result['items']) == 10
    assert result['total_items'] == 25
```

## Contributing

Contributions are welcome! Please follow these guidelines:

### Code Style

- Follow PEP 8 conventions
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep lines under 100 characters where possible

### Documentation Comments

All functions should include descriptive docstrings following Google style:

```python
def classify_notification_type(subject='', body='', endpoint=None):
    """
    Determines the notification type based on endpoint and text content.
    
    Prioritizes endpoint-based classification over text-based keyword matching
    for more accurate categorization.
    
    Args:
        subject (str): Notification subject line. Defaults to empty string.
        body (str): Notification message body. Defaults to empty string.
        endpoint (str, optional): CKAN request endpoint name. Defaults to None.
    
    Returns:
        str: Notification type ('dataset', 'organization', 'group', or 'system').
    
    Example:
        >>> classify_notification_type(
        ...     subject='Dataset Updated',
        ...     endpoint='dataset_show'
        ... )
        'dataset'
    """
```

### Committing Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/description`
3. Make your changes and commit with clear messages:
   ```bash
   git commit -m "Add feature: clear description of changes"
   ```
4. Push to your fork
5. Create a Pull Request with a detailed description

### Pull Request Requirements

- Include tests for new functionality
- Update documentation and README if applicable
- Ensure all tests pass
- Update CHANGELOG if significant changes

## Troubleshooting

### Issue: Notifications not appearing in dashboard

**Symptoms**: Dashboard loads but shows no notifications despite recent actions

**Solutions**:
1. Check if interception is enabled:
   ```bash
   ckan config-tool /etc/ckan/default/ckan.ini ckanext.notifications.email_interception
   ```
2. Verify plugin is in `ckan.plugins` setting
3. Check logs for errors: `tail -f /var/log/ckan/ckan.log`
4. Ensure database tables exist: run any pending migrations

### Issue: Performance degradation with large notification volumes

**Symptoms**: Dashboard becomes slow when user has many notifications

**Solutions**:
1. Reduce `ckanext.notifications.cleanup_days` to remove old notifications quickly
2. Lower `ckanext.notifications.max_notifications_per_user` to enforce stricter limits
3. Increase `ckanext.notifications.notifications_per_page` to reduce queries
4. Add a database index on notifications table:
   ```sql
   CREATE INDEX idx_notifications_user_id_created_at 
   ON notifications(user_id, created_at DESC);
   ```

### Issue: Email notifications not intercepted

**Symptoms**: Email interception enabled but emails not captured

**Solutions**:
1. Verify `ckanext.notifications.email_interception = true` is set
2. Check CKAN mail configuration is working: `ckan mail-test`
3. Review CKAN logs for email sending errors
4. Check that users have valid email addresses

### Issue: Flash messages not captured

**Symptoms**: Flash messages not appearing in notification center

**Solutions**:
1. Verify `ckanext.notifications.flash_interception = true` is set
2. Ensure you're logged in as the target user
3. Check that flash messages are being generated (they appear in the web UI)
4. Review browser console for JavaScript errors

## Support and Community

- **Issues**: Report bugs on [GitHub Issues](https://github.com/Datashades/ckanext-notifications/issues)
- **Discussions**: Join conversations on [GitHub Discussions](https://github.com/Datashades/ckanext-notifications/discussions)
- **CKAN Community**: Visit [CKAN.org](https://ckan.org) for general CKAN support

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed release notes and version history.

## License

This project is licensed under the [AGPL 3.0 License](LICENSE) - see the LICENSE file for details.

### Attribution

This extension was developed to improve notification management in CKAN instances, providing users with a centralized point to review and manage all system communications.

---

**Last Updated**: 2024  
**Tested with CKAN**: 2.9, 2.10, 2.11
