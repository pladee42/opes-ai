"""LINE Messaging API service."""

import requests
from typing import Optional

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer,
)

from config import Config


class LineService:
    """Service for LINE Messaging API operations."""

    def __init__(self):
        """Initialize the LINE service."""
        self.configuration = Configuration(
            access_token=Config.LINE_CHANNEL_ACCESS_TOKEN
        )
        self.handler = WebhookHandler(Config.LINE_CHANNEL_SECRET)

    @property
    def api(self) -> MessagingApi:
        """Get the MessagingApi client."""
        api_client = ApiClient(self.configuration)
        return MessagingApi(api_client)

    def reply_text(self, reply_token: str, text: str) -> None:
        """Reply with a text message."""
        self.api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=text)],
            )
        )

    def reply_flex(self, reply_token: str, alt_text: str, flex_content: dict) -> None:
        """Reply with a Flex Message."""
        self.api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[
                    FlexMessage(
                        alt_text=alt_text,
                        contents=FlexContainer.from_dict(flex_content),
                    )
                ],
            )
        )

    def get_profile(self, user_id: str) -> Optional[dict]:
        """Get user profile from LINE."""
        try:
            profile = self.api.get_profile(user_id)
            return {
                "user_id": profile.user_id,
                "display_name": profile.display_name,
                "picture_url": profile.picture_url,
            }
        except Exception as e:
            print(f"Error getting LINE profile: {e}")
            return None

    def get_message_content(self, message_id: str) -> Optional[bytes]:
        """Download message content (image, video, etc.)."""
        try:
            url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
            headers = {"Authorization": f"Bearer {Config.LINE_CHANNEL_ACCESS_TOKEN}"}

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            return response.content
        except Exception as e:
            print(f"Error downloading content: {e}")
            return None


# Singleton instance
line_service = LineService()
