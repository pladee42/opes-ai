"""Follow event handler for onboarding new users."""

from services.line_service import line_service
from services.sheets_service import sheets_service
from utils.flex_messages import FlexMessages


class FollowHandler:
    """Handler for follow/unfollow events."""

    def handle_follow(self, event) -> None:
        """Handle when user follows the LINE OA.

        Args:
            event: LINE FollowEvent
        """
        user_id = event.source.user_id
        reply_token = event.reply_token

        print(f"👋 New follower: {user_id}")

        # Get user profile from LINE
        profile = line_service.get_profile(user_id)
        display_name = profile.get("display_name", "User") if profile else "User"

        # Check if user exists (returning user)
        existing_user = sheets_service.get_user(user_id)
        
        if existing_user:
            # Returning user
            print(f"✅ Returning user: {display_name}")
            line_service.reply_flex(
                reply_token,
                f"ยินดีต้อนรับกลับ {display_name}!",
                FlexMessages.welcome_back_message(display_name),
            )
        else:
            # New user - start onboarding
            print(f"🆕 New user: {display_name}")
            user = sheets_service.create_user(
                user_id=user_id,
                display_name=display_name,
                onboarding_status="NEW",
            )
            line_service.reply_flex(
                reply_token,
                f"ยินดีต้อนรับ {display_name}!",
                FlexMessages.welcome_new_user(display_name),
            )

    def handle_unfollow(self, event) -> None:
        """Handle when user unfollows the LINE OA.

        Args:
            event: LINE UnfollowEvent
        """
        user_id = event.source.user_id
        print(f"👋 User unfollowed: {user_id}")
        # We don't delete data - user might come back


# Singleton instance
follow_handler = FollowHandler()
