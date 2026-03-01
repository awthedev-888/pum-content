"""Offline test suite for PUM email_sender package.

Tests Gmail SMTP client and email composer with fully mocked smtplib to ensure:
- Credential validation from environment variables
- SMTP connection to smtp.gmail.com:587 with STARTTLS
- App Password space stripping
- Correct call order (starttls before login)
- Message sending via send_message
- Email body formatting with bilingual captions and hashtags
- MIME composition with text body and PNG attachment
- Top-level send_post_email integration

Usage:
    python3 tests/test_email_sender.py
"""

import os
import sys
import tempfile

# Ensure project root is on sys.path for reliable imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import logging
from unittest.mock import patch, MagicMock, call
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from email_sender.smtp_client import send_email, GMAIL_SMTP_HOST, GMAIL_SMTP_PORT
from email_sender.composer import compose_email, format_email_body, send_post_email


class MockPost:
    """Mock GeneratedPost for testing without content_generator dependency."""
    caption_id = "Kisah sukses UMKM batik di Yogyakarta dengan bantuan ahli PUM."
    caption_en = "Success story of batik SME in Yogyakarta with PUM expert assistance."
    hashtags = ["PUMIndonesia", "UMKM", "BatikYogya", "ExpertVolunteers"]
    posting_suggestion = "Best time: 10:00 WIB - Success story theme"
    content_pillar = "success_stories"
    template_type = "quote_story"
    template_data = {}


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

    # ===================================================================
    # COMPOSER TESTS (Task 1 TDD - basic behavior)
    # ===================================================================

    # ===== Test 11: format_email_body contains posting suggestion =====
    try:
        body = format_email_body(MockPost())
        if "POSTING SUGGESTION" not in body:
            errors.append("Test 11 (posting suggestion header): 'POSTING SUGGESTION' not in body")
        if "Best time: 10:00 WIB" not in body:
            errors.append("Test 11 (posting suggestion value): 'Best time: 10:00 WIB' not in body")
    except Exception as e:
        errors.append(f"Test 11 (posting suggestion): {type(e).__name__}: {e}")

    # ===== Test 12: format_email_body contains Bahasa Indonesia caption =====
    try:
        body = format_email_body(MockPost())
        if "CAPTION (Bahasa Indonesia)" not in body:
            errors.append("Test 12 (caption ID header): 'CAPTION (Bahasa Indonesia)' not in body")
        if "Kisah sukses" not in body:
            errors.append("Test 12 (caption ID text): 'Kisah sukses' not in body")
    except Exception as e:
        errors.append(f"Test 12 (caption ID): {type(e).__name__}: {e}")

    # ===== Test 13: format_email_body contains English caption =====
    try:
        body = format_email_body(MockPost())
        if "CAPTION (English)" not in body:
            errors.append("Test 13 (caption EN header): 'CAPTION (English)' not in body")
        if "Success story" not in body:
            errors.append("Test 13 (caption EN text): 'Success story' not in body")
    except Exception as e:
        errors.append(f"Test 13 (caption EN): {type(e).__name__}: {e}")

    # ===== Test 14: format_email_body contains hashtags with # prefix =====
    try:
        body = format_email_body(MockPost())
        if "#PUMIndonesia" not in body:
            errors.append("Test 14 (hashtags): '#PUMIndonesia' not in body")
        if "#UMKM" not in body:
            errors.append("Test 14 (hashtags): '#UMKM' not in body")
        if "#BatikYogya" not in body:
            errors.append("Test 14 (hashtags): '#BatikYogya' not in body")
    except Exception as e:
        errors.append(f"Test 14 (hashtags): {type(e).__name__}: {e}")

    # ===== Test 15: format_email_body contains content pillar and template type =====
    try:
        body = format_email_body(MockPost())
        if "success_stories" not in body:
            errors.append("Test 15 (metadata): 'success_stories' not in body")
        if "quote_story" not in body:
            errors.append("Test 15 (metadata): 'quote_story' not in body")
    except Exception as e:
        errors.append(f"Test 15 (metadata): {type(e).__name__}: {e}")

    # ===== Test 16: format_email_body handles Indonesian Unicode =====
    try:
        class UnicodePost(MockPost):
            caption_id = "Pelatihan pengusaha kopi di daerah pegunungan"
        body = format_email_body(UnicodePost())
        if not isinstance(body, str):
            errors.append(f"Test 16 (unicode): Expected str, got {type(body).__name__}")
        if "Pelatihan pengusaha kopi" not in body:
            errors.append("Test 16 (unicode): Indonesian text not in body")
    except UnicodeError as e:
        errors.append(f"Test 16 (unicode): UnicodeError: {e}")
    except Exception as e:
        errors.append(f"Test 16 (unicode): {type(e).__name__}: {e}")

    # ===== Test 17: compose_email returns MIMEMultipart('mixed') =====
    tmp_img = None
    try:
        tmp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp_img.write(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        tmp_img.close()

        msg = compose_email(MockPost(), tmp_img.name, "test@gmail.com", "recv@gmail.com")
        if not isinstance(msg, MIMEMultipart):
            errors.append(f"Test 17 (MIMEMultipart): Expected MIMEMultipart, got {type(msg).__name__}")
        elif msg.get_content_subtype() != "mixed":
            errors.append(f"Test 17 (subtype): Expected 'mixed', got '{msg.get_content_subtype()}'")
    except Exception as e:
        errors.append(f"Test 17 (MIMEMultipart): {type(e).__name__}: {e}")
    finally:
        if tmp_img and os.path.exists(tmp_img.name):
            os.unlink(tmp_img.name)

    # ===== Test 18: compose_email sets From with display name =====
    tmp_img = None
    try:
        tmp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp_img.write(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        tmp_img.close()

        msg = compose_email(MockPost(), tmp_img.name, "test@gmail.com", "recv@gmail.com")
        if "PUM Content Generator" not in msg["From"]:
            errors.append(f"Test 18 (From header): 'PUM Content Generator' not in '{msg['From']}'")
    except Exception as e:
        errors.append(f"Test 18 (From header): {type(e).__name__}: {e}")
    finally:
        if tmp_img and os.path.exists(tmp_img.name):
            os.unlink(tmp_img.name)

    # ===== Test 19: compose_email sets To, Subject, Date headers =====
    tmp_img = None
    try:
        tmp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp_img.write(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        tmp_img.close()

        msg = compose_email(MockPost(), tmp_img.name, "test@gmail.com", "recv@gmail.com")
        if msg["To"] != "recv@gmail.com":
            errors.append(f"Test 19 (To): Expected 'recv@gmail.com', got '{msg['To']}'")
        if not msg["Subject"] or not msg["Subject"].startswith("PUM Instagram Post -"):
            errors.append(f"Test 19 (Subject): Expected 'PUM Instagram Post -...', got '{msg['Subject']}'")
        if msg["Date"] is None:
            errors.append("Test 19 (Date): Date header is None")
    except Exception as e:
        errors.append(f"Test 19 (headers): {type(e).__name__}: {e}")
    finally:
        if tmp_img and os.path.exists(tmp_img.name):
            os.unlink(tmp_img.name)

    # ===== Test 20: compose_email attaches text/plain with utf-8 =====
    tmp_img = None
    try:
        tmp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp_img.write(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        tmp_img.close()

        msg = compose_email(MockPost(), tmp_img.name, "test@gmail.com", "recv@gmail.com")
        payloads = msg.get_payload()
        if len(payloads) < 2:
            errors.append(f"Test 20 (payload count): Expected 2 payloads, got {len(payloads)}")
        else:
            text_part = payloads[0]
            if text_part.get_content_type() != "text/plain":
                errors.append(f"Test 20 (text type): Expected text/plain, got {text_part.get_content_type()}")
            charset = text_part.get_param("charset")
            if charset and charset.lower() != "utf-8":
                errors.append(f"Test 20 (charset): Expected utf-8, got {charset}")
    except Exception as e:
        errors.append(f"Test 20 (text payload): {type(e).__name__}: {e}")
    finally:
        if tmp_img and os.path.exists(tmp_img.name):
            os.unlink(tmp_img.name)

    # ===== Test 21: compose_email attaches image/png with pum_post_ filename =====
    tmp_img = None
    try:
        tmp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp_img.write(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        tmp_img.close()

        msg = compose_email(MockPost(), tmp_img.name, "test@gmail.com", "recv@gmail.com")
        payloads = msg.get_payload()
        if len(payloads) >= 2:
            img_part = payloads[1]
            if img_part.get_content_type() != "image/png":
                errors.append(f"Test 21 (image type): Expected image/png, got {img_part.get_content_type()}")
            content_disp = img_part.get("Content-Disposition", "")
            if "pum_post_" not in content_disp:
                errors.append(f"Test 21 (filename): 'pum_post_' not in Content-Disposition: {content_disp}")
        else:
            errors.append(f"Test 21 (image payload): Not enough payloads: {len(payloads)}")
    except Exception as e:
        errors.append(f"Test 21 (image payload): {type(e).__name__}: {e}")
    finally:
        if tmp_img and os.path.exists(tmp_img.name):
            os.unlink(tmp_img.name)

    # ===== Test 22: compose_email raises FileNotFoundError for missing image =====
    try:
        compose_email(MockPost(), "/nonexistent/path/image.png", "a@b.com", "c@d.com")
        errors.append("Test 22 (missing image): No FileNotFoundError raised")
    except FileNotFoundError:
        pass  # Expected
    except Exception as e:
        errors.append(f"Test 22 (missing image): Wrong exception {type(e).__name__}: {e}")

    # ===== Test 23: compose_email raises FileNotFoundError for zero-byte image =====
    tmp_empty = None
    try:
        tmp_empty = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp_empty.close()  # Zero bytes

        compose_email(MockPost(), tmp_empty.name, "a@b.com", "c@d.com")
        errors.append("Test 23 (empty image): No FileNotFoundError raised")
    except FileNotFoundError as e:
        if "empty" not in str(e).lower():
            errors.append(f"Test 23 (empty image): Error message doesn't mention 'empty': {e}")
    except Exception as e:
        errors.append(f"Test 23 (empty image): Wrong exception {type(e).__name__}: {e}")
    finally:
        if tmp_empty and os.path.exists(tmp_empty.name):
            os.unlink(tmp_empty.name)

    # ===== Test 24: send_post_email raises ValueError when RECIPIENT_EMAIL not set =====
    saved = clear_email_env()
    try:
        os.environ["GMAIL_ADDRESS"] = "test@gmail.com"
        os.environ["GMAIL_APP_PASSWORD"] = "testpass1234abcd"
        try:
            send_post_email(MockPost(), "any_path.png")
            errors.append("Test 24 (missing RECIPIENT_EMAIL): No ValueError raised")
        except ValueError as e:
            if "RECIPIENT_EMAIL" not in str(e):
                errors.append(f"Test 24 (missing RECIPIENT_EMAIL): 'RECIPIENT_EMAIL' not in error: {e}")
        except Exception as e:
            errors.append(f"Test 24 (missing RECIPIENT_EMAIL): Wrong exception {type(e).__name__}: {e}")
    finally:
        restore_env(saved)

    # ===== Test 25: send_post_email composes and sends when all env vars set =====
    saved = clear_email_env()
    tmp_img = None
    try:
        os.environ["GMAIL_ADDRESS"] = "test@gmail.com"
        os.environ["GMAIL_APP_PASSWORD"] = "testpass1234abcd"
        os.environ["RECIPIENT_EMAIL"] = "recv@gmail.com"

        tmp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp_img.write(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        tmp_img.close()

        with patch("email_sender.composer.send_email") as mock_send:
            send_post_email(MockPost(), tmp_img.name)

            if mock_send.call_count != 1:
                errors.append(f"Test 25 (send call): Expected 1 call, got {mock_send.call_count}")
            else:
                sent_msg = mock_send.call_args[0][0]
                if not isinstance(sent_msg, MIMEMultipart):
                    errors.append(f"Test 25 (msg type): Expected MIMEMultipart, got {type(sent_msg).__name__}")
                elif sent_msg["To"] != "recv@gmail.com":
                    errors.append(f"Test 25 (msg To): Expected 'recv@gmail.com', got '{sent_msg['To']}'")
    except Exception as e:
        errors.append(f"Test 25 (send_post_email): {type(e).__name__}: {e}")
    finally:
        restore_env(saved)
        if tmp_img and os.path.exists(tmp_img.name):
            os.unlink(tmp_img.name)

    # ===== Results =====
    total_tests = 25
    passed = total_tests - len(errors)
    print(f"\nEmail Sender Tests: {passed}/{total_tests} passed")

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
