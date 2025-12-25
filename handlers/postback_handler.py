"""Postback handler for Rich Menu actions."""

from services.line_service import line_service
from services.sheets_service import sheets_service
from utils.flex_messages import FlexMessages


class PostbackHandler:
    """Handler for postback events from Rich Menu and buttons."""

    def handle(self, event) -> None:
        """Handle postback event.

        Args:
            event: LINE PostbackEvent
        """
        user_id = event.source.user_id
        reply_token = event.reply_token
        data = event.postback.data

        print(f"📬 Postback: {data} from {user_id}")

        # Parse action from postback data
        action = data.split("=")[0] if "=" in data else data

        if action == "start_onboarding":
            self._start_onboarding(user_id, reply_token)
        elif action == "set_budget":
            self._handle_budget_selection(user_id, reply_token, data)
        elif action == "skip_onboarding":
            self._skip_onboarding(user_id, reply_token)
        else:
            print(f"⚠️ Unknown postback action: {action}")

    def _start_onboarding(self, user_id: str, reply_token: str) -> None:
        """Start the onboarding flow - go directly to LIFF."""
        # Update user status
        sheets_service.update_user(user_id, {"onboarding_status": "SETUP"})
        
        # Send LIFF link for setup (budget + allocation in one page)
        line_service.reply_flex(
            reply_token,
            "ตั้งค่าแผนลงทุน",
            FlexMessages.setup_plan_prompt(),
        )

    def _handle_budget_selection(self, user_id: str, reply_token: str, data: str) -> None:
        """Handle budget selection (legacy - kept for compatibility)."""
        # Parse budget from data: "set_budget=10000"
        try:
            budget = int(data.split("=")[1])
        except (IndexError, ValueError):
            budget = 10000

        # Update user with budget
        sheets_service.update_user(user_id, {
            "monthly_budget": budget,
            "onboarding_status": "ALLOCATION",
        })

        # Send LIFF link for allocation setup
        line_service.reply_flex(
            reply_token,
            "ตั้งค่าแผนการลงทุน",
            FlexMessages.setup_plan_prompt(),
        )

    def _skip_onboarding(self, user_id: str, reply_token: str) -> None:
        """Skip onboarding for now."""
        sheets_service.update_user(user_id, {"onboarding_status": "ACTIVE"})
        
        line_service.reply_text(
            reply_token,
            "✅ ข้ามการตั้งค่าแล้ว ส่งรูปสลิปมาได้เลย! 📸"
        )


# Singleton instance
postback_handler = PostbackHandler()
