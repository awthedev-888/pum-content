"""Google Sheets reader for PUM Indonesia content generation.

Reads content input rows from a shared Google Sheet using service account
authentication via the gspread library.

Follows the source module interface: returns str, never raises.
"""

import json
import logging
import os

import gspread

logger = logging.getLogger(__name__)


def read_content_sheet(sheet_id: str) -> str:
    """Read content rows from a Google Sheet and format as readable text.

    Authenticates using service account credentials stored in the
    GSHEET_CREDENTIALS environment variable (JSON string).

    Args:
        sheet_id: The Google Sheets spreadsheet ID (from the URL).

    Returns:
        Formatted text with each row as "key: value" pairs.
        Returns empty string if credentials are missing, auth fails,
        or on any error.
    """
    try:
        credentials_json = os.environ.get("GSHEET_CREDENTIALS")
        if not credentials_json:
            logger.warning("GSHEET_CREDENTIALS environment variable not set")
            return ""

        try:
            credentials_dict = json.loads(credentials_json)
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse GSHEET_CREDENTIALS JSON: %s", e)
            return ""

        gc = gspread.service_account_from_dict(credentials_dict)
        spreadsheet = gc.open_by_key(sheet_id)
        worksheet = spreadsheet.sheet1
        records = worksheet.get_all_records()

        if not records:
            logger.info("No records found in spreadsheet %s", sheet_id)
            return ""

        rows = []
        for record in records:
            pairs = []
            for key, value in record.items():
                if value != "" and value is not None:
                    pairs.append(f"{key}: {value}")
            if pairs:
                rows.append("; ".join(pairs))

        return "\n".join(rows)

    except Exception as e:
        logger.warning("Failed to read Google Sheet %s: %s", sheet_id, e)
        return ""
