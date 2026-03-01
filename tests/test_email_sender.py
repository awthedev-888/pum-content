"""Offline test suite for PUM email_sender SMTP client.

Tests Gmail SMTP client with fully mocked smtplib to ensure:
- Credential validation from environment variables
- SMTP connection to smtp.gmail.com:587 with STARTTLS
- App Password space stripping
- Correct call order (starttls before login)
- Message sending via send_message

Usage:
    python3 tests/test_email_sender.py
"""

import os
import sys

# Ensure project root is on sys.path for reliable imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import logging
from unittest.mock import patch, MagicMock, call
from email.mime.text import MIMEText

from email_sender.smtp_client import send_email, GMAIL_SMTP_HOST, GMAIL_SMTP_PORT


def clear_email_env():
    """Remove email env vars if set, return originals for restore."""
    saved = {}
    for key in ["GMAIL_ADDRESS", "GMAIL_APP_PASSWORD", "RECIPIENT_EMAIL"]:
        saved[key] = os.environ.pop(key, None)
    return saved


def restore_env(saved):
    """Restore previously saved env vars."""
    for key, val in saved.items():
        if val is not None:
            os.environ[key] = val
        else:
            os.environ.pop(key, None)


def make_test_msg():
    """Create a simple test email message."""
    msg = MIMEText("test body")
    msg["To"] = "recv@gmail.com"
    msg["From"] = "send@gmail.com"
    msg["Subject"] = "Test"
    return msg


def setup_smtp_mock(mock_smtp_class):
    """Configure SMTP mock for context manager usage."""
    mock_server = MagicMock()
    mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)
    return mock_server


def main():
    errors = []

    # ===== Test 1: Missing GMAIL_ADDRESS raises ValueError =====
    saved = clear_email_env()
    try:
        os.environ["GMAIL_APP_PASSWORD"] = "testpass"
        try:
            send_email(make_test_msg())
            errors.append("Test 1 (missing GMAIL_ADDRESS): No ValueError raised")
        except ValueError as e:
            if "GMAIL_ADDRESS" not in str(e):
                errors.append(
                    f"Test 1 (missing GMAIL_ADDRESS): "
                    f"ValueError does not mention GMAIL_ADDRESS: {e}"
                )
        except Exception as e:
            errors.append(
                f"Test 1 (missing GMAIL_ADDRESS): "
                f"Wrong exception {type(e).__name__}: {e}"
            )
    finally:
        restore_env(saved)

    # ===== Test 2: Missing GMAIL_APP_PASSWORD raises ValueError =====
    saved = clear_email_env()
    try:
        os.environ["GMAIL_ADDRESS"] = "test@gmail.com"
        try:
            send_email(make_test_msg())
            errors.append("Test 2 (missing GMAIL_APP_PASSWORD): No ValueError raised")
        except ValueError as e:
            if "GMAIL_APP_PASSWORD" not in str(e):
                errors.append(
                    f"Test 2 (missing GMAIL_APP_PASSWORD): "
                    f"ValueError does not mention GMAIL_APP_PASSWORD: {e}"
                )
        except Exception as e:
            errors.append(
                f"Test 2 (missing GMAIL_APP_PASSWORD): "
                f"Wrong exception {type(e).__name__}: {e}"
            )
    finally:
        restore_env(saved)

    # ===== Test 3: Both variables missing lists both in ValueError =====
    saved = clear_email_env()
    try:
        try:
            send_email(make_test_msg())
            errors.append("Test 3 (both missing): No ValueError raised")
        except ValueError as e:
            error_msg = str(e)
            if "GMAIL_ADDRESS" not in error_msg:
                errors.append(
                    f"Test 3 (both missing): "
                    f"ValueError does not mention GMAIL_ADDRESS: {e}"
                )
            if "GMAIL_APP_PASSWORD" not in error_msg:
                errors.append(
                    f"Test 3 (both missing): "
                    f"ValueError does not mention GMAIL_APP_PASSWORD: {e}"
                )
        except Exception as e:
            errors.append(
                f"Test 3 (both missing): "
                f"Wrong exception {type(e).__name__}: {e}"
            )
    finally:
        restore_env(saved)

    # ===== Test 4: SMTP called with correct host, port, timeout =====
    saved = clear_email_env()
    try:
        os.environ["GMAIL_ADDRESS"] = "test@gmail.com"
        os.environ["GMAIL_APP_PASSWORD"] = "testpassword123x"
        msg = make_test_msg()

        with patch("email_sender.smtp_client.smtplib.SMTP") as mock_smtp_class:
            mock_server = setup_smtp_mock(mock_smtp_class)
            send_email(msg)

            mock_smtp_class.assert_called_once()
            args, kwargs = mock_smtp_class.call_args
            if args[0] != "smtp.gmail.com":
                errors.append(f"Test 4 (SMTP host): Expected smtp.gmail.com, got {args[0]}")
            if args[1] != 587:
                errors.append(f"Test 4 (SMTP port): Expected 587, got {args[1]}")
            if kwargs.get("timeout") != 30:
                errors.append(f"Test 4 (SMTP timeout): Expected 30, got {kwargs.get('timeout')}")
    except Exception as e:
        errors.append(f"Test 4 (SMTP connection args): {type(e).__name__}: {e}")
    finally:
        restore_env(saved)

    # ===== Test 5: starttls called before login (call order) =====
    saved = clear_email_env()
    try:
        os.environ["GMAIL_ADDRESS"] = "test@gmail.com"
        os.environ["GMAIL_APP_PASSWORD"] = "testpassword123x"

        with patch("email_sender.smtp_client.smtplib.SMTP") as mock_smtp_class:
            mock_server = setup_smtp_mock(mock_smtp_class)
            send_email(make_test_msg())

            # Get method call names in order
            call_names = [c[0] for c in mock_server.method_calls]
            if "starttls" not in call_names:
                errors.append("Test 5 (call order): starttls was not called")
            elif "login" not in call_names:
                errors.append("Test 5 (call order): login was not called")
            else:
                tls_idx = call_names.index("starttls")
                login_idx = call_names.index("login")
                if tls_idx >= login_idx:
                    errors.append(
                        f"Test 5 (call order): starttls (idx={tls_idx}) "
                        f"not before login (idx={login_idx})"
                    )
    except Exception as e:
        errors.append(f"Test 5 (call order): {type(e).__name__}: {e}")
    finally:
        restore_env(saved)

    # ===== Test 6: login called with address and password =====
    saved = clear_email_env()
    try:
        os.environ["GMAIL_ADDRESS"] = "sender@gmail.com"
        os.environ["GMAIL_APP_PASSWORD"] = "myapppassword16c"

        with patch("email_sender.smtp_client.smtplib.SMTP") as mock_smtp_class:
            mock_server = setup_smtp_mock(mock_smtp_class)
            send_email(make_test_msg())

            mock_server.login.assert_called_once_with("sender@gmail.com", "myapppassword16c")
    except Exception as e:
        errors.append(f"Test 6 (login credentials): {type(e).__name__}: {e}")
    finally:
        restore_env(saved)

    # ===== Test 7: App Password spaces stripped before login =====
    saved = clear_email_env()
    try:
        os.environ["GMAIL_ADDRESS"] = "test@gmail.com"
        os.environ["GMAIL_APP_PASSWORD"] = "abcd efgh ijkl mnop"

        with patch("email_sender.smtp_client.smtplib.SMTP") as mock_smtp_class:
            mock_server = setup_smtp_mock(mock_smtp_class)
            send_email(make_test_msg())

            login_args = mock_server.login.call_args[0]
            if login_args[1] != "abcdefghijklmnop":
                errors.append(
                    f"Test 7 (space stripping): "
                    f"Expected 'abcdefghijklmnop', got '{login_args[1]}'"
                )
    except Exception as e:
        errors.append(f"Test 7 (space stripping): {type(e).__name__}: {e}")
    finally:
        restore_env(saved)

    # ===== Test 8: send_message called with provided message =====
    saved = clear_email_env()
    try:
        os.environ["GMAIL_ADDRESS"] = "test@gmail.com"
        os.environ["GMAIL_APP_PASSWORD"] = "testpassword123x"
        msg = make_test_msg()

        with patch("email_sender.smtp_client.smtplib.SMTP") as mock_smtp_class:
            mock_server = setup_smtp_mock(mock_smtp_class)
            send_email(msg)

            mock_server.send_message.assert_called_once_with(msg)
    except Exception as e:
        errors.append(f"Test 8 (send_message): {type(e).__name__}: {e}")
    finally:
        restore_env(saved)

    # ===== Test 9: Success logged =====
    saved = clear_email_env()
    try:
        os.environ["GMAIL_ADDRESS"] = "test@gmail.com"
        os.environ["GMAIL_APP_PASSWORD"] = "testpassword123x"

        with patch("email_sender.smtp_client.smtplib.SMTP") as mock_smtp_class:
            mock_server = setup_smtp_mock(mock_smtp_class)
            with patch("email_sender.smtp_client.logger") as mock_logger:
                send_email(make_test_msg())
                mock_logger.info.assert_called_once()
                log_msg = mock_logger.info.call_args[0][0]
                if "sent" not in log_msg.lower() and "success" not in log_msg.lower():
                    errors.append(
                        f"Test 9 (log message): "
                        f"Expected success-related log, got: {log_msg}"
                    )
    except Exception as e:
        errors.append(f"Test 9 (success log): {type(e).__name__}: {e}")
    finally:
        restore_env(saved)

    # ===== Test 10: starttls called with ssl context =====
    saved = clear_email_env()
    try:
        os.environ["GMAIL_ADDRESS"] = "test@gmail.com"
        os.environ["GMAIL_APP_PASSWORD"] = "testpassword123x"

        with patch("email_sender.smtp_client.smtplib.SMTP") as mock_smtp_class:
            mock_server = setup_smtp_mock(mock_smtp_class)
            send_email(make_test_msg())

            mock_server.starttls.assert_called_once()
            starttls_kwargs = mock_server.starttls.call_args
            # Check that context= keyword argument was passed
            if starttls_kwargs[1].get("context") is None and \
               (not starttls_kwargs[0] or starttls_kwargs[0][0] is None):
                errors.append("Test 10 (starttls context): No SSL context passed to starttls")
    except Exception as e:
        errors.append(f"Test 10 (starttls context): {type(e).__name__}: {e}")
    finally:
        restore_env(saved)

    # ===== Results =====
    total_tests = 10
    passed = total_tests - len(errors)
    print(f"\nEmail Sender SMTP Client Tests: {passed}/{total_tests} passed")

    if errors:
        print(f"\nFAILED: {len(errors)} error(s)")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
