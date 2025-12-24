"""Google Sheets service for CRUD operations."""

import json
from datetime import datetime
from typing import Optional

import gspread
from google.oauth2.service_account import Credentials

from config import Config


class SheetsService:
    """Service for interacting with Google Sheets database."""

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(self):
        """Initialize the Sheets service with credentials."""
        self._client: Optional[gspread.Client] = None
        self._spreadsheet: Optional[gspread.Spreadsheet] = None

    @property
    def client(self) -> gspread.Client:
        """Lazy-load the gspread client."""
        if self._client is None:
            creds = Credentials.from_service_account_file(
                Config.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=self.SCOPES
            )
            self._client = gspread.authorize(creds)
        return self._client

    @property
    def spreadsheet(self) -> gspread.Spreadsheet:
        """Lazy-load the spreadsheet."""
        if self._spreadsheet is None:
            self._spreadsheet = self.client.open_by_key(Config.GOOGLE_SHEETS_ID)
        return self._spreadsheet

    # ==================== USERS ====================

    def get_user(self, user_id: str) -> Optional[dict]:
        """Get a user by their LINE user ID."""
        sheet = self.spreadsheet.worksheet("Users")
        records = sheet.get_all_records()

        for record in records:
            if record.get("user_id") == user_id:
                # Parse JSON fields
                if record.get("target_allocation"):
                    try:
                        record["target_allocation"] = json.loads(
                            record["target_allocation"]
                        )
                    except json.JSONDecodeError:
                        record["target_allocation"] = {}
                return record
        return None

    def create_user(
        self,
        user_id: str,
        display_name: str,
        monthly_budget: int = 10000,
        target_allocation: Optional[dict] = None,
        risk_profile: str = "moderate",
        onboarding_status: str = "NEW",
    ) -> dict:
        """Create a new user in the Users sheet."""
        sheet = self.spreadsheet.worksheet("Users")

        if target_allocation is None:
            target_allocation = {}  # Empty until user sets custom allocation

        user_data = {
            "user_id": user_id,
            "display_name": display_name,
            "monthly_budget": monthly_budget,
            "target_allocation": json.dumps(target_allocation),
            "risk_profile": risk_profile,
            "onboarding_status": onboarding_status,
            "created_at": datetime.now().isoformat(),
        }

        # Append row to sheet
        sheet.append_row(list(user_data.values()))

        # Return with parsed allocation
        user_data["target_allocation"] = target_allocation
        return user_data

    def update_user(self, user_id: str, updates: dict) -> bool:
        """Update a user's profile."""
        sheet = self.spreadsheet.worksheet("Users")
        records = sheet.get_all_records()

        for idx, record in enumerate(records):
            if record.get("user_id") == user_id:
                row_num = idx + 2  # +1 for header, +1 for 1-indexed

                # Get column indices
                headers = sheet.row_values(1)

                for key, value in updates.items():
                    if key in headers:
                        col_num = headers.index(key) + 1
                        # Serialize JSON fields
                        if key == "target_allocation" and isinstance(value, dict):
                            value = json.dumps(value)
                        sheet.update_cell(row_num, col_num, value)

                return True
        return False

    def get_or_create_user(self, user_id: str, display_name: str) -> dict:
        """Get existing user or create a new one."""
        user = self.get_user(user_id)
        if user is None:
            user = self.create_user(user_id, display_name)
        return user

    # ==================== TRANSACTIONS ====================

    def append_transaction(self, tx_data: dict) -> str:
        """Append a transaction to the Transactions sheet."""
        sheet = self.spreadsheet.worksheet("Transactions")

        # Generate transaction ID
        tx_id = f"TX{datetime.now().strftime('%Y%m%d%H%M%S')}"

        row_data = {
            "tx_id": tx_id,
            "user_id": tx_data.get("user_id", ""),
            "date": tx_data.get("date", datetime.now().strftime("%Y-%m-%d")),
            "asset": tx_data.get("asset", ""),
            "asset_raw": tx_data.get("asset_raw", tx_data.get("asset", "")),
            "asset_type": tx_data.get("asset_type", ""),
            "side": tx_data.get("side", "BUY"),
            "amount": tx_data.get("amount", 0),
            "price": tx_data.get("price", 0),
            "currency": tx_data.get("currency", "THB"),
            "total_thb": tx_data.get("total_thb", 0),
            "source_app": tx_data.get("source_app", ""),
            "created_at": datetime.now().isoformat(),
        }

        sheet.append_row(list(row_data.values()))
        return tx_id

    def get_transactions(self, user_id: str) -> list[dict]:
        """Get all transactions for a user."""
        sheet = self.spreadsheet.worksheet("Transactions")
        records = sheet.get_all_records()

        return [r for r in records if r.get("user_id") == user_id]

    def get_holdings(self, user_id: str) -> dict[str, float]:
        """Calculate current holdings from transactions."""
        transactions = self.get_transactions(user_id)
        holdings: dict[str, float] = {}

        for tx in transactions:
            asset = tx.get("asset", "")
            amount = float(tx.get("amount", 0))
            side = tx.get("side", "BUY").upper()

            if asset not in holdings:
                holdings[asset] = 0

            if side == "BUY":
                holdings[asset] += amount
            elif side == "SELL":
                holdings[asset] -= amount

        return {k: v for k, v in holdings.items() if v > 0}


# Singleton instance
sheets_service = SheetsService()
