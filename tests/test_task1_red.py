"""TDD RED: Failing tests for content_brief.py and sheets_reader.py (Task 1 behaviors)."""

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import tempfile


def main():
    errors = []
    passed = 0
    failed = 0

    # ---------------------------------------------------------------
    # 1. load_content_brief() returns formatted text from valid YAML
    # ---------------------------------------------------------------
    try:
        from research_sources.content_brief import load_content_brief

        result = load_content_brief()
        assert isinstance(result, str), f"Expected str, got {type(result)}"
        assert len(result) > 0, "Expected non-empty string"
        assert "Batik" in result, "Expected 'Batik' in output"
        assert "SMEs" in result or "SME" in result, "Expected SME-related content"
        print("[OK]  1. load_content_brief returns formatted text from valid YAML")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 1. load_content_brief valid YAML - {e}")
        errors.append(f"load_content_brief valid YAML: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 2. load_content_brief() returns empty string when file does not exist
    # ---------------------------------------------------------------
    try:
        from research_sources.content_brief import load_content_brief

        result = load_content_brief(filepath="nonexistent_file_xyz.yaml")
        assert result == "", f"Expected empty string, got: {repr(result)}"
        print("[OK]  2. load_content_brief returns '' for nonexistent file")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 2. load_content_brief nonexistent file - {e}")
        errors.append(f"load_content_brief nonexistent: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 3. load_content_brief() returns empty string when YAML is empty
    # ---------------------------------------------------------------
    try:
        from research_sources.content_brief import load_content_brief

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            tmp_path = f.name
        try:
            result = load_content_brief(filepath=tmp_path)
            assert result == "", f"Expected empty string for empty YAML, got: {repr(result)}"
            print("[OK]  3. load_content_brief returns '' for empty YAML")
            passed += 1
        finally:
            os.unlink(tmp_path)
    except Exception as e:
        print(f"[FAIL] 3. load_content_brief empty YAML - {e}")
        errors.append(f"load_content_brief empty YAML: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 4. load_content_brief() handles missing sections gracefully
    # ---------------------------------------------------------------
    try:
        from research_sources.content_brief import load_content_brief

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("stats:\n  - number: '50'\n    context: 'projects completed'\n")
            tmp_path = f.name
        try:
            result = load_content_brief(filepath=tmp_path)
            assert isinstance(result, str), f"Expected str, got {type(result)}"
            assert "50" in result, "Expected stats number in output"
            assert "Story Ideas" not in result, "Should not have Story Ideas section"
            print("[OK]  4. load_content_brief handles missing sections (only stats)")
            passed += 1
        finally:
            os.unlink(tmp_path)
    except Exception as e:
        print(f"[FAIL] 4. load_content_brief missing sections - {e}")
        errors.append(f"load_content_brief missing sections: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 5. read_content_sheet() returns empty string when GSHEET_CREDENTIALS not set
    # ---------------------------------------------------------------
    try:
        from research_sources.sheets_reader import read_content_sheet

        saved = os.environ.pop("GSHEET_CREDENTIALS", None)
        try:
            result = read_content_sheet("fake-sheet-id")
            assert result == "", f"Expected empty string, got: {repr(result)}"
            print("[OK]  5. read_content_sheet returns '' when GSHEET_CREDENTIALS not set")
            passed += 1
        finally:
            if saved:
                os.environ["GSHEET_CREDENTIALS"] = saved
    except Exception as e:
        print(f"[FAIL] 5. read_content_sheet no credentials - {e}")
        errors.append(f"read_content_sheet no credentials: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 6. read_content_sheet() returns empty string on auth failure
    # ---------------------------------------------------------------
    try:
        from research_sources.sheets_reader import read_content_sheet

        os.environ["GSHEET_CREDENTIALS"] = "not-valid-json"
        try:
            result = read_content_sheet("fake-sheet-id")
            assert result == "", f"Expected empty string on bad JSON, got: {repr(result)}"
            print("[OK]  6. read_content_sheet returns '' on auth failure (bad JSON)")
            passed += 1
        finally:
            os.environ.pop("GSHEET_CREDENTIALS", None)
    except Exception as e:
        print(f"[FAIL] 6. read_content_sheet auth failure - {e}")
        errors.append(f"read_content_sheet auth failure: {e}")
        failed += 1

    # ---------------------------------------------------------------
    # 7. read_content_sheet() formats spreadsheet rows as readable text (mocked)
    # ---------------------------------------------------------------
    try:
        from unittest.mock import patch, MagicMock
        from research_sources.sheets_reader import read_content_sheet
        import json

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
            with patch("research_sources.sheets_reader.gspread") as mock_gspread:
                mock_gspread.service_account_from_dict.return_value = mock_gc
                result = read_content_sheet("test-sheet-id")
                assert isinstance(result, str), f"Expected str, got {type(result)}"
                assert "PUM Impact" in result, f"Expected 'PUM Impact' in output, got: {repr(result)}"
                assert "200 SMEs" in result, f"Expected '200 SMEs' in output"
                print("[OK]  7. read_content_sheet formats spreadsheet rows correctly")
                passed += 1
        finally:
            os.environ.pop("GSHEET_CREDENTIALS", None)
    except Exception as e:
        print(f"[FAIL] 7. read_content_sheet format rows - {e}")
        errors.append(f"read_content_sheet format rows: {e}")
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
        print("All checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
