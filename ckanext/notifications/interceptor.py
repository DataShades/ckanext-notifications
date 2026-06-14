import flask
from flask import has_request_context, session

import html
import logging
import re
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, cast

from ckan import model
from ckan.common import g
from ckan.lib import helpers as ckan_helpers, mailer as ckan_mailer
from ckan.plugins import toolkit as tk

from ckanext.notifications import config
from ckanext.notifications.model import Notification

log = logging.getLogger(__name__)
NotificationModel = cast(Any, Notification)
URL_PATTERN = re.compile(r'https?://[^\s<>"\']+', flags=re.IGNORECASE)


def _format_email_body_for_notification(body, body_html):
    """
    Return HTML content suitable for notification rendering.
    - Use existing HTML email body when available.
    - Otherwise escape text, linkify plain URLs and preserve line breaks.
    """
    if body_html:
        return str(body_html)

    text = str(body or '')
    if not text:
        return ''

    chunks = []
    cursor = 0

    for match in URL_PATTERN.finditer(text):
        start, end = match.span()
        raw_url = match.group(0)
        trimmed_url = raw_url.rstrip('.,);]')
        trailing = raw_url[len(trimmed_url):]

        chunks.append(html.escape(text[cursor:start]))

        if trimmed_url:
            href = html.escape(trimmed_url, quote=True)
            label = html.escape(trimmed_url)
            chunks.append(
                f'<a href="{href}" target="_blank" rel="noopener noreferrer">{label}</a>'
            )

        if trailing:
            chunks.append(html.escape(trailing))

        cursor = end

    chunks.append(html.escape(text[cursor:]))
    return ''.join(chunks).replace('\n', '<br>')


def _cleanup_notifications_for_user(user_id):
    max_notifications = config.notifications_get_max_notifications_per_user()
    cleanup_days = config.notifications_get_cleanup_days()

    if cleanup_days > 0:
        cutoff = datetime.utcnow() - timedelta(days=cleanup_days)
        model.Session.query(Notification).filter(
            NotificationModel.user_id == user_id,
            NotificationModel.created_at < cutoff
        ).delete(synchronize_session=False)

    if max_notifications > 0:
        excess_ids_query = model.Session.query(Notification.id).filter(
            NotificationModel.user_id == user_id
        ).order_by(NotificationModel.created_at.desc()).offset(max_notifications)
        excess_ids = [row[0] for row in excess_ids_query.all()]
        if excess_ids:
            model.Session.query(Notification).filter(
                NotificationModel.id.in_(excess_ids)
            ).delete(synchronize_session=False)


def create_notification_record(user_id, notification_type, source, subject, body):
    """Safely writes an intercepted notification item to the database."""
    try:
        # Open an isolated session or use the contextual model.Session
        session = model.Session
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            source=source,
            subject=subject,
            body=body
        )
        session.add(notification)
        _cleanup_notifications_for_user(user_id)
        session.commit()
    except Exception as e:
        log.error(f"Failed to save intercepted notification to DB: {str(e)}")
        model.Session.rollback()


def _classify_from_endpoint(endpoint):
    """Infers the notification type based on the CKAN request endpoint."""
    if not endpoint:
        return None

    dataset_endpoint_prefix = config.notifications_get_dataset_endpoint_startswith()
    resource_endpoint_prefix = config.notifications_get_resource_endpoint_startswith()
    organization_endpoint_prefix = config.notifications_get_organization_endpoint_startswith()
    group_endpoint_prefix = config.notifications_get_group_endpoint_startswith()

    endpoint_lc = str(endpoint).lower()

    if endpoint_lc.startswith(dataset_endpoint_prefix) or endpoint_lc.startswith(resource_endpoint_prefix):
        return 'dataset'

    if endpoint_lc.startswith(organization_endpoint_prefix):
        return 'organization'

    if endpoint_lc.startswith(group_endpoint_prefix):
        return 'group'

    return None


def _classify_from_text(*parts):
    """Infers the notification type by scanning subject and body text for keywords."""
    text = ' '.join(str(part).lower() for part in parts if part)
    if not text:
        return None

    organization_keywords = config.notifications_get_organization_keywords()
    group_keywords = config.notifications_get_group_keywords()
    dataset_keywords = config.notifications_get_dataset_keywords()

    if any(keyword in text for keyword in organization_keywords):
        return 'organization'

    if any(keyword in text for keyword in group_keywords):
        return 'group'

    if any(keyword in text for keyword in dataset_keywords):
        return 'dataset'

    return None


def classify_notification_type(subject='', body='', endpoint=None):
    """Determines the notification type based on endpoint and text content."""
    endpoint_type = _classify_from_endpoint(endpoint)
    if endpoint_type:
        return endpoint_type

    text_type = _classify_from_text(subject, body)
    if text_type:
        return text_type

    return 'system'


def patch_ckan_flash():
    """
    Wraps flask.flash and ckan.lib.helpers.flash to intercept all flash messages.
    Extracts the message content and category to store them as notifications.
    """
    # Prevent double-patching if the extension reloads
    if getattr(flask.flash, "_is_patched_by_ext", False):
        return

    original_flash = flask.flash

    @wraps(original_flash)
    def patched_flash(message, category='message', *args, **kwargs):
        # Invoke the original flash function so functionality doesn't break
        result = original_flash(message, category=category, *args, **kwargs)

        try:
            # Only intercept if we have a request context
            if not has_request_context():
                log.debug("Flash message intercepted but no request context available")
                return result
            
            # Try to get user from g.user (CKAN context)
            user = g.userobj if hasattr(g, 'userobj') else None
            
            # If no user in g, try to get from session
            if not user:
                user_name = session.get('ckan_user')
                if user_name:
                    user = model.User.get(user_name)
            
            if user:
                message_text = str(message)
                endpoint = tk.request.endpoint
                notification_type = classify_notification_type(
                    subject=category,
                    body=message_text,
                    endpoint=endpoint,
                )
                
                create_notification_record(
                    user_id=user.id,
                    notification_type=notification_type,
                    source="flash",
                    subject=f"Flash message: {category.title()}",
                    body=message_text
                )
                log.debug(
                    f"Flash message intercepted for user {user.id}: "
                    f"category={category}, endpoint={endpoint}, type={notification_type}"
                )
            else:
                log.debug(f"Flash message intercepted but no user context: {message}")

        except Exception as e:
            log.error(f"Error intercepting flash message: {str(e)}", exc_info=True)

        return result

    setattr(cast(Any, patched_flash), "_is_patched_by_ext", True)
    
    # Patch in flask module
    flask.flash = patched_flash
    
    # Also patch in ckan.lib.helpers where it's imported
    try:
        ckan_helpers.flash = patched_flash
    except Exception as e:
        log.error(f"Failed to patch ckan.lib.helpers.flash: {str(e)}", exc_info=True)
    
    log.info("Successfully patched Flask flash for notification monitoring.")


def patch_ckan_mailer():
    """
    Wraps ckan.lib.mailer.mail_recipient to intercept all outgoing emails.
    Extracts the user ID, subject, and body to replicate them inside our DB.
    """
    # Prevent double-patching if the extension reloads
    if getattr(ckan_mailer.mail_recipient, "_is_patched_by_ext", False):
        return

    original_mail_recipient = ckan_mailer.mail_recipient

    @wraps(original_mail_recipient)
    def patched_mail_recipient(recipient_name, recipient_email, subject, body, body_html=None, *args, **kwargs):
        # Invoke the original mailing process so functionality doesn't break
        result = original_mail_recipient(
            recipient_name,
            recipient_email,
            subject,
            body,
            body_html=body_html,
            *args,
            **kwargs,
        )

        try:
            # Locate the CKAN User ID matching the recipient email address
            user = model.Session.query(model.User).filter(model.User.email == recipient_email).first()
            if user:
                rendered_body = body_html if body_html else body
                rendered_body_text = str(rendered_body)
                formatted_body = _format_email_body_for_notification(body, body_html)
                endpoint = tk.request.endpoint if has_request_context() else None
                notification_type = classify_notification_type(
                    subject=subject,
                    body=rendered_body_text,
                    endpoint=endpoint,
                )

                create_notification_record(
                    user_id=user.id,
                    notification_type=notification_type,
                    source="email",
                    subject=subject,
                    body=formatted_body
                )
        except Exception as e:
            log.error(f"Error intercepting mail delivery: {str(e)}")

        return result

    setattr(cast(Any, patched_mail_recipient), "_is_patched_by_ext", True)
    ckan_mailer.mail_recipient = patched_mail_recipient
    log.info("Successfully patched CKAN mailer for notification monitoring.")
