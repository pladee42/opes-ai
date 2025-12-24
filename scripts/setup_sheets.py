"""Setup script to initialize Google Sheets structure."""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from services.sheets_service import SheetsService


# Sheet structures
SHEETS_CONFIG = {
    "Users": [
        "user_id",
        "display_name", 
        "monthly_budget",
        "target_allocation",
        "risk_profile",
        "created_at",
    ],
    "Transactions": [
        "tx_id",
        "user_id",
        "date",
        "asset",
        "side",
        "amount",
        "price",
        "total_thb",
        "source_app",
        "created_at",
    ],
    "Asset_Reference": [
        "asset_symbol",
        "asset_name",
        "current_price_thb",
        "last_updated",
    ],
    "Watchlist_Alerts": [
        "asset_symbol",
        "last_checked",
        "risk_status",
        "alert_sent",
    ],
}


def setup_sheets():
    """Set up the Google Sheets structure."""
    print("🔧 Setting up Google Sheets structure...\n")

    try:
        service = SheetsService()
        spreadsheet = service.spreadsheet

        print(f"📊 Connected to: {spreadsheet.title}\n")

        existing_sheets = {ws.title: ws for ws in spreadsheet.worksheets()}

        for sheet_name, headers in SHEETS_CONFIG.items():
            print(f"📋 Setting up '{sheet_name}'...")

            if sheet_name in existing_sheets:
                # Sheet exists, just update headers
                sheet = existing_sheets[sheet_name]
                print(f"   ✓ Sheet exists, updating headers...")
            else:
                # Create new sheet
                sheet = spreadsheet.add_worksheet(
                    title=sheet_name, rows=1000, cols=len(headers)
                )
                print(f"   ✓ Created new sheet")

            # Set headers in row 1
            sheet.update("A1", [headers])

            # Format header row (bold)
            sheet.format("A1:Z1", {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9},
            })

            print(f"   ✓ Headers: {', '.join(headers)}")

        # Remove default Sheet1 if it exists and is empty
        if "Sheet1" in existing_sheets:
            sheet1 = existing_sheets["Sheet1"]
            if sheet1.row_count <= 1 or not sheet1.get_all_values():
                try:
                    spreadsheet.del_worksheet(sheet1)
                    print("\n🗑️  Removed empty 'Sheet1'")
                except Exception:
                    pass  # Can't delete if it's the only sheet

        print("\n✅ Google Sheets setup complete!")
        print(f"\n📎 Sheet URL: https://docs.google.com/spreadsheets/d/{Config.GOOGLE_SHEETS_ID}")

        return True

    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        return False


if __name__ == "__main__":
    setup_sheets()
