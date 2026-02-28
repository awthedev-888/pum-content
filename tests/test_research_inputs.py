"""Offline test suite for content brief loader and Google Sheets reader.

Tests both modules with real files, temp files, and mocked dependencies.
No network calls are made during these tests.

Usage:
    python3 tests/test_research_inputs.py
"""

import json
import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

# Ensure project root is on sys.path for reliable imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from research_sources.content_brief import load_content_brief
from research_sources.sheets_reader import read_content_sheet


def main():
    errors = []
    passed = 0
    failed = 0

    # ---------------------------------------------------------------
    # 1. load_content_brief with real sample file returns text
    #    containing "Batik" and "SMEs"
    # ---------------------------------------------------------------
    try:
        result = load_content_brief()
        assert isinstance(result, str), f"Expected str, got {type(result)}"
        assert len(result) > 0, "Expected non-empty string from sample file"
        assert "Batik" in result, f"Expected 'Batik' in output, got: {result[:200]}"
        assert "SMEs supported" in result, f"Expected 'SMEs supported' in output"
        assert "Story Ideas:" in result, "Expected 'Story Ideas:' section header"
        assert "Key Statistics:" in result, "Expected 'Key Statistics:' section header"
        assert "Upcoming Events:" in result, "Expected 'Upcoming Events:' section header"
        print("[OK]  1. load_content_brief with real sample - contains Batik and SMEs")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 1. load_content_brief real sample - {e}")
        errors.append(f"Real sample: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 2. load_content_brief with nonexistent file returns ""
    # ---------------------------------------------------------------
    try:
        result = load_content_brief(filepath="nonexistent_file_xyz_42.yaml")
        assert result == "", f"Expected empty string, got: {repr(result[:100])}"
        print("[OK]  2. load_content_brief nonexistent file returns ''")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 2. load_content_brief nonexistent - {e}")
        errors.append(f"Nonexistent file: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 3. load_content_brief with empty YAML file returns ""
    # ---------------------------------------------------------------
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write("")
            tmp_path = f.name
        try:
            result = load_content_brief(filepath=tmp_path)
            assert result == "", f"Expected '' for empty YAML, got: {repr(result[:100])}"
            print("[OK]  3. load_content_brief empty YAML file returns ''")
            passed += 1
        finally:
            os.unlink(tmp_path)
    except Exception as e:
        print(f"[FAIL] 3. load_content_brief empty YAML - {e}")
        errors.append(f"Empty YAML: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 4. load_content_brief with partial sections (only stats) returns
    #    stats text but not Story Ideas
    # ---------------------------------------------------------------
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(
                "stats:\n"
                "  - number: '50'\n"
                "    context: 'projects completed'\n"
                "  - number: '12'\n"
                "    context: 'provinces reached'\n"
            )
            tmp_path = f.name
        try:
            result = load_content_brief(filepath=tmp_path)
            assert isinstance(result, str), f"Expected str, got {type(result)}"
            assert "Key Statistics:" in result, "Expected 'Key Statistics:' header"
            assert "50" in result, "Expected stat number '50' in output"
            assert "12" in result, "Expected stat number '12' in output"
            assert "Story Ideas:" not in result, "Should not have Story Ideas section"
            assert "Upcoming Events:" not in result, "Should not have Events section"
            print("[OK]  4. load_content_brief partial sections (only stats)")
            passed += 1
        finally:
            os.unlink(tmp_path)
    except Exception as e:
        print(f"[FAIL] 4. load_content_brief partial sections - {e}")
        errors.append(f"Partial sections: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 5. load_content_brief always returns str type
    # ---------------------------------------------------------------
    try:
        r1 = load_content_brief()
        r2 = load_content_brief(filepath="nonexistent.yaml")
        assert isinstance(r1, str), f"Expected str, got {type(r1)}"
        assert isinstance(r2, str), f"Expected str, got {type(r2)}"
        print("[OK]  5. load_content_brief always returns str")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 5. load_content_brief return type - {e}")
        errors.append(f"Return type: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 6. read_content_sheet returns "" when GSHEET_CREDENTIALS not set
    # ---------------------------------------------------------------
    try:
        saved = os.environ.pop("GSHEET_CREDENTIALS", None)
        try:
            result = read_content_sheet("fake-id")
            assert result == "", f"Expected '', got: {repr(result[:100])}"
            print("[OK]  6. read_content_sheet returns '' without GSHEET_CREDENTIALS")
            passed += 1
        finally:
            if saved:
                os.environ["GSHEET_CREDENTIALS"] = saved
    except Exception as e:
        print(f"[FAIL] 6. read_content_sheet no credentials - {e}")
        errors.append(f"No credentials: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 7. read_content_sheet returns "" when credentials JSON is malformed
    # ---------------------------------------------------------------
    try:
        os.environ["GSHEET_CREDENTIALS"] = "not-valid-json"
        try:
            result = read_content_sheet("fake-id")
            assert result == "", f"Expected '' on bad JSON, got: {repr(result[:100])}"
            print("[OK]  7. read_content_sheet returns '' on malformed JSON")
            passed += 1
        finally:
            os.environ.pop("GSHEET_CREDENTIALS", None)
    except Exception as e:
        print(f"[FAIL] 7. read_content_sheet bad JSON - {e}")
        errors.append(f"Bad JSON: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 8. read_content_sheet formats mocked spreadsheet data correctly
    # ---------------------------------------------------------------
    try:
        fake_creds = json.dumps({
            "type": "service_account",
            "project_id": "test",
            "private_key_id": "test",
            "private_key": "-----BEGIN RSA PRIVATE KEY-----\ntest\n-----END RSA PRIVATE KEY-----\n",
            "client_email": "test@test.iam.gserviceaccount.com",
            "client_id": "123",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        })
        os.environ["GSHEET_CREDENTIALS"] = fake_creds

        mock_worksheet = MagicMock()
        mock_worksheet.get_all_records.return_value = [
            {"Topic": "PUM Impact", "Detail": "200 SMEs supported"},
            {"Topic": "Agriculture", "Detail": "New farming techniques"},
        ]
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.sheet1 = mock_worksheet
        mock_gc = MagicMock()
        mock_gc.open_by_key.return_value = mock_spreadsheet

        try:
            with patch(
                "research_sources.sheets_reader.gspread"
            ) as mock_gspread:
                mock_gspread.service_account_from_dict.return_value = mock_gc
                result = read_content_sheet("test-sheet-id")
                assert isinstance(result, str), f"Expected str, got {type(result)}"
                assert "Topic: PUM Impact" in result, (
                    f"Expected 'Topic: PUM Impact' in output, got: {repr(result)}"
                )
                assert "Detail: 200 SMEs supported" in result, (
                    "Expected 'Detail: 200 SMEs supported'"
                )
                assert "Agriculture" in result, "Expected 'Agriculture' in output"
                # Verify row separator is newline
                assert "\n" in result, "Expected newline between rows"
                print("[OK]  8. read_content_sheet formats mocked spreadsheet data")
                passed += 1
        finally:
            os.environ.pop("GSHEET_CREDENTIALS", None)
    except Exception as e:
        print(f"[FAIL] 8. read_content_sheet mocked data - {e}")
        errors.append(f"Mocked data: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 9. read_content_sheet returns "" on SpreadsheetNotFound (mocked)
    # ---------------------------------------------------------------
    try:
        import gspread.exceptions

        fake_creds = json.dumps({
            "type": "service_account",
            "project_id": "test",
            "private_key_id": "test",
            "private_key": "-----BEGIN RSA PRIVATE KEY-----\ntest\n-----END RSA PRIVATE KEY-----\n",
            "client_email": "test@test.iam.gserviceaccount.com",
            "client_id": "123",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        })
        os.environ["GSHEET_CREDENTIALS"] = fake_creds

        mock_gc = MagicMock()
        mock_gc.open_by_key.side_effect = gspread.exceptions.SpreadsheetNotFound

        try:
            with patch(
                "research_sources.sheets_reader.gspread"
            ) as mock_gspread:
                mock_gspread.service_account_from_dict.return_value = mock_gc
                result = read_content_sheet("nonexistent-sheet-id")
                assert result == "", (
                    f"Expected '' on SpreadsheetNotFound, got: {repr(result)}"
                )
                print("[OK]  9. read_content_sheet returns '' on SpreadsheetNotFound")
                passed += 1
        finally:
            os.environ.pop("GSHEET_CREDENTIALS", None)
    except Exception as e:
        print(f"[FAIL] 9. read_content_sheet SpreadsheetNotFound - {e}")
        errors.append(f"SpreadsheetNotFound: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 10. Both functions never raise exceptions (always return str)
    # ---------------------------------------------------------------
    try:
        # Test content_brief with corrupted YAML
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write("invalid: yaml: [unclosed")
            tmp_path = f.name
        try:
            r1 = load_content_brief(filepath=tmp_path)
            assert isinstance(r1, str), f"Expected str, got {type(r1)}"
        finally:
            os.unlink(tmp_path)

        # Test sheets_reader without env var
        saved = os.environ.pop("GSHEET_CREDENTIALS", None)
        try:
            r2 = read_content_sheet("any-id")
            assert isinstance(r2, str), f"Expected str, got {type(r2)}"
        finally:
            if saved:
                os.environ["GSHEET_CREDENTIALS"] = saved

        print("[OK]  10. Both functions never raise (always return str)")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 10. Never raise check - {e}")
        errors.append(f"Never raise: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------
    total = passed + failed
    print(f"\n{passed}/{total} checks passed")

    if errors:
        print("\nFailures:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("All offline checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
