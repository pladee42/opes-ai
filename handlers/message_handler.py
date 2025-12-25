"""Message handler for processing text messages."""

from services.line_service import line_service
from services.sheets_service import sheets_service
from utils.flex_messages import FlexMessages


class MessageHandler:
    """Handler for processing text messages."""

    # Command keywords (includes Rich Menu # commands)
    COMMANDS = {
        "help": ["help", "ช่วยเหลือ", "วิธีใช้", "?", "#help"],
        "status": ["status", "สถานะ", "portfolio", "พอร์ต", "#status"],
        "plan": ["plan", "แผน", "dca", "ซื้อ", "#dca"],
        "record": ["#record"],
        "report": ["#report", "report"],
        "settings": ["#settings", "settings", "ตั้งค่า", "budget", "งบ"],
    }

    def handle(self, event) -> None:
        """Process a text message event.

        Args:
            event: LINE MessageEvent with text content
        """
        reply_token = event.reply_token
        user_id = event.source.user_id
        text = event.message.text.strip().lower()

        # Check for commands
        if self._is_command(text, "help"):
            self._reply_help(reply_token)
        elif self._is_command(text, "status"):
            self._reply_status(reply_token, user_id)
        elif self._is_command(text, "plan"):
            self._reply_dca(reply_token, user_id)
        elif self._is_command(text, "record"):
            self._reply_record_tip(reply_token)
        elif self._is_command(text, "report"):
            self._reply_report_coming_soon(reply_token)
        elif self._is_command(text, "settings"):
            self._reply_settings(reply_token)
        else:
            # Default: greet and explain
            self._reply_default(reply_token, user_id)

    def _is_command(self, text: str, command: str) -> bool:
        """Check if text matches a command."""
        keywords = self.COMMANDS.get(command, [])
        return any(kw in text for kw in keywords)

    def _reply_help(self, reply_token: str) -> None:
        """Reply with help information."""
        help_text = """📚 **วิธีใช้ Family Wealth AI**

📸 **บันทึกรายการ**
ส่งรูปหน้าจอการซื้อขายจาก Dime! หรือ Binance มาได้เลย

📊 **ดูสถานะ**
พิมพ์ "สถานะ" หรือ "portfolio"

📋 **แผนการซื้อ (เร็วๆนี้)**
พิมพ์ "แผน" หรือ "dca"

❓ **ความช่วยเหลือ**
พิมพ์ "help" หรือ "ช่วยเหลือ"
"""
        line_service.reply_text(reply_token, help_text)

    def _reply_status(self, reply_token: str, user_id: str) -> None:
        """Reply with portfolio status."""
        holdings = sheets_service.get_holdings(user_id)

        if not holdings:
            line_service.reply_text(
                reply_token,
                "📊 ยังไม่มีข้อมูลการลงทุน\n\nส่งรูปหน้าจอการซื้อขายมาเพื่อเริ่มบันทึกได้เลย 📸",
            )
            return

        # Format holdings
        holdings_text = "📊 **สถานะพอร์ตการลงทุน**\n\n"
        for asset, amount in holdings.items():
            holdings_text += f"• {asset}: {amount:,.4f}\n"

        holdings_text += "\n💡 ฟีเจอร์ดูมูลค่าปัจจุบันจะมาเร็วๆนี้!"
        line_service.reply_text(reply_token, holdings_text)

    def _reply_dca(self, reply_token: str, user_id: str) -> None:
        """Reply with Smart DCA plan using rebalance-by-buying logic."""
        from utils.dca_calculator import calculate_dca_rebalance, format_dca_message
        
        user = sheets_service.get_user(user_id)
        
        if not user or not user.get("target_allocation"):
            line_service.reply_text(
                reply_token,
                "📋 ยังไม่ได้ตั้งค่าแผนลงทุน\n\nพิมพ์ #settings เพื่อตั้งค่างบและแผน",
            )
            return

        budget = user.get("monthly_budget", 10000)
        allocation = user.get("target_allocation", {})

        if not allocation:
            line_service.reply_text(
                reply_token,
                "📋 ยังไม่ได้ตั้งค่าสัดส่วนการลงทุน\n\nพิมพ์ #settings เพื่อตั้งค่า",
            )
            return

        # Get current holdings value (simplified - using quantity for now)
        # TODO: Integrate with price_service for real-time values
        holdings = sheets_service.get_holdings(user_id)
        
        # For now, treat holdings as values (will add price lookup later)
        # This is a placeholder - in production, multiply quantity by current price
        current_values = {}
        for asset, qty in holdings.items():
            # Placeholder: assume 1000 THB per unit for demo
            current_values[asset] = qty * 1000
        
        # Calculate Smart DCA
        result = calculate_dca_rebalance(
            monthly_budget=budget,
            target_allocation=allocation,
            current_holdings=current_values,
        )
        
        # Format and send
        message = format_dca_message(result)
        line_service.reply_text(reply_token, message)

    def _reply_record_tip(self, reply_token: str) -> None:
        """Reply with tip to send image."""
        line_service.reply_text(
            reply_token,
            "📸 **บันทึกรายการ**\n\nส่งรูปหน้าจอการซื้อขายจาก:\n• Dime! (หุ้น US, ทอง)\n• Binance (คริปโต)\n\nมาได้เลย!",
        )

    def _reply_report_coming_soon(self, reply_token: str) -> None:
        """Reply that report feature is coming soon."""
        line_service.reply_text(
            reply_token,
            "📈 **Performance Report**\n\nฟีเจอร์รายงานกำไรขาดทุนกำลังพัฒนาอยู่\n\n⏳ เร็วๆนี้!",
        )

    def _reply_settings(self, reply_token: str) -> None:
        """Reply with budget selection."""
        line_service.reply_flex(
            reply_token,
            "ตั้งค่างบลงทุน",
            FlexMessages.budget_question(),
        )

    def _reply_default(self, reply_token: str, user_id: str) -> None:
        """Reply with default greeting."""
        # Check if user is new
        user = sheets_service.get_user(user_id)

        if user is None:
            # New user - get profile and create
            profile = line_service.get_profile(user_id)
            display_name = profile.get("display_name", "User") if profile else "User"
            sheets_service.create_user(user_id, display_name)

            # Send welcome message
            flex_content = FlexMessages.welcome_message(display_name)
            line_service.reply_flex(
                reply_token,
                f"ยินดีต้อนรับ {display_name}!",
                flex_content,
            )
        else:
            # Existing user - remind how to use
            line_service.reply_text(
                reply_token,
                "👋 สวัสดี!\n\n📸 ส่งรูปหน้าจอการซื้อขายมาได้เลย\n\nหรือพิมพ์ 'help' เพื่อดูคำสั่งทั้งหมด",
            )


# Singleton instance
message_handler = MessageHandler()
