"""Test Google Sheets connection."""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from services.sheets_service import SheetsService


def test_connection():
    """Test the Google Sheets connection."""
    print("🔍 Testing Google Sheets connection...\n")

    # Check config
    print(f"📄 Service Account File: {Config.GOOGLE_SERVICE_ACCOUNT_FILE}")
    print(f"📊 Sheet ID: {Config.GOOGLE_SHEETS_ID}")
    print()

    try:
        # Initialize service
        service = SheetsService()

        # Try to access spreadsheet
        spreadsheet = service.spreadsheet
        print(f"✅ Connected to: {spreadsheet.title}")
        print(f"📋 Worksheets:")

        for sheet in spreadsheet.worksheets():
            print(f"   - {sheet.title} ({sheet.row_count} rows)")

        print("\n🎉 Connection successful!")
        return True

    except FileNotFoundError as e:
        print(f"❌ Service account file not found: {e}")
        print("   Make sure the JSON file exists at the path specified in .env")
        return False

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nCommon issues:")
        print("   1. Service account email not shared with the Sheet")
        print("   2. Wrong GOOGLE_SHEETS_ID in .env")
        print("   3. Google Sheets API not enabled in Cloud Console")
        return False


if __name__ == "__main__":
    test_connection()
