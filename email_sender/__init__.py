"""PUM Indonesia Content Generator - Email Delivery Package.

Provides Gmail SMTP email delivery with PNG image attachment
and copy-paste-ready bilingual captions for Instagram posting.
"""

from email_sender.smtp_client import send_email

__all__ = [
    "send_email",
]
