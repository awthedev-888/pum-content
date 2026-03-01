"""Gmail SMTP client for PUM content email delivery.

Connects to smtp.gmail.com:587 with STARTTLS encryption and
authenticates using App Password from environment variables.
"""

import os
import ssl
import smtplib
import logging

GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587
SMTP_TIMEOUT = 30

logger = logging.getLogger(__name__)


def send_email(msg):
    """Send a composed email message via Gmail SMTP.

    Connects to smtp.gmail.com:587 with STARTTLS encryption and
    authenticates using App Password from environment variables.

    Args:
        msg: email.mime.multipart.MIMEMultipart message object.

    Raises:
        ValueError: If GMAIL_ADDRESS or GMAIL_APP_PASSWORD not set.
        smtplib.SMTPAuthenticationError: If credentials are invalid.
        smtplib.SMTPException: If send fails after authentication.
    """
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")

    missing = []
    if not gmail_address:
        missing.append("GMAIL_ADDRESS")
    if not gmail_password:
        missing.append("GMAIL_APP_PASSWORD")
    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")

    # Google displays App Passwords as "abcd efgh ijkl mnop" with spaces
    # for readability, but the actual password is the 16 chars without spaces
    gmail_password = gmail_password.replace(" ", "")

    context = ssl.create_default_context()

    with smtplib.SMTP(GMAIL_SMTP_HOST, GMAIL_SMTP_PORT, timeout=SMTP_TIMEOUT) as server:
        server.starttls(context=context)
        server.login(gmail_address, gmail_password)
        server.send_message(msg)

    logger.info("Email sent successfully to %s", msg["To"])
