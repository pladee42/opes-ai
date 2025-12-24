"""Image handler for processing transaction screenshots."""

from services.gemini_service import gemini_service
from services.sheets_service import sheets_service
from services.line_service import line_service
from models.transaction import Transaction
from utils.flex_messages import FlexMessages


class ImageHandler:
    """Handler for processing image messages."""

    def handle(self, event) -> None:
        """Process an image message event.

        Args:
            event: LINE MessageEvent with image content
        """
        reply_token = event.reply_token
        message_id = event.message.id
        user_id = event.source.user_id

        # 1. Download image from LINE
        image_bytes = line_service.get_message_content(message_id)
        if not image_bytes:
            self._reply_error(
                reply_token,
                "ดาวน์โหลดรูปไม่สำเร็จ",
                "กรุณาลองส่งรูปใหม่อีกครั้ง",
            )
            return

        # 2. Parse image with Gemini Vision
        parsed = gemini_service.parse_transaction_image(image_bytes)
        if not parsed:
            self._reply_error(
                reply_token,
                "อ่านรูปไม่สำเร็จ",
                "กรุณาส่งรูปหน้าจอการซื้อขายจาก Dime! หรือ Binance ที่ชัดเจน",
            )
            return

        # 3. Ensure user exists
        profile = line_service.get_profile(user_id)
        display_name = profile.get("display_name", "User") if profile else "User"
        sheets_service.get_or_create_user(user_id, display_name)

        # 4. Create transaction and save to sheets
        transaction = Transaction.from_parsed_image(parsed, user_id)
        tx_id = sheets_service.append_transaction(transaction.to_dict())
        transaction.tx_id = tx_id

        # 5. Reply with confirmation
        tx_data = transaction.to_dict()
        flex_content = FlexMessages.transaction_confirmation(tx_data)
        line_service.reply_flex(
            reply_token,
            f"บันทึก {transaction.side} {transaction.asset} สำเร็จ",
            flex_content,
        )

    def _reply_error(self, reply_token: str, title: str, message: str) -> None:
        """Reply with an error message."""
        flex_content = FlexMessages.error_message(title, message)
        line_service.reply_flex(reply_token, f"ข้อผิดพลาด: {title}", flex_content)


# Singleton instance
image_handler = ImageHandler()
