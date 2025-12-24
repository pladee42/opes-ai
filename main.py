"""Family Wealth AI - LINE OA Webhook Handler.

This is the main entry point for the Cloud Function.
"""

import os
from flask import Flask, request, abort

from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent,
    FollowEvent,
    UnfollowEvent,
    PostbackEvent,
)

from config import Config
from services.line_service import line_service
from handlers.message_handler import message_handler
from handlers.image_handler import image_handler
from handlers.follow_handler import follow_handler
from handlers.postback_handler import postback_handler


# Initialize Flask app
app = Flask(__name__)


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "Family Wealth AI"}


@app.route("/api/allocation", methods=["POST"])
def save_allocation():
    """API endpoint for LIFF to save user allocation."""
    from services.sheets_service import sheets_service
    
    data = request.get_json()
    user_id = data.get("user_id")
    allocation = data.get("allocation", {})
    
    if not user_id or not allocation:
        return {"error": "Missing user_id or allocation"}, 400
    
    # Update user's allocation
    success = sheets_service.update_user(user_id, {
        "target_allocation": allocation,
        "onboarding_status": "ACTIVE",
    })
    
    if success:
        return {"status": "ok", "message": "Allocation saved"}
    else:
        return {"error": "User not found"}, 404



@app.route("/webhook", methods=["POST"])
def webhook():
    """LINE webhook endpoint."""
    # Get signature from header
    signature = request.headers.get("X-Line-Signature", "")

    # Get request body
    body = request.get_data(as_text=True)

    # Validate signature
    try:
        line_service.handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400, "Invalid signature")

    return "OK"


# Register event handlers
@line_service.handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event: MessageEvent):
    """Handle text messages."""
    message_handler.handle(event)


@line_service.handler.add(MessageEvent, message=ImageMessageContent)
def handle_image_message(event: MessageEvent):
    """Handle image messages."""
    image_handler.handle(event)


@line_service.handler.add(FollowEvent)
def handle_follow(event: FollowEvent):
    """Handle follow event (new user)."""
    follow_handler.handle_follow(event)


@line_service.handler.add(UnfollowEvent)
def handle_unfollow(event: UnfollowEvent):
    """Handle unfollow event."""
    follow_handler.handle_unfollow(event)


@line_service.handler.add(PostbackEvent)
def handle_postback(event: PostbackEvent):
    """Handle postback event (Rich Menu actions)."""
    postback_handler.handle(event)


# Cloud Functions entry point
def main(request):
    """Cloud Functions entry point.

    Args:
        request: Flask request object

    Returns:
        Flask response
    """
    with app.request_context(request.environ):
        try:
            rv = app.preprocess_request()
            if rv is None:
                rv = app.dispatch_request()
        except Exception as e:
            rv = app.handle_exception(e)
        response = app.make_response(rv)
        return app.process_response(response)


# Local development
if __name__ == "__main__":
    # Validate configuration
    missing = Config.validate()
    if missing:
        print(f"⚠️  Missing configuration: {', '.join(missing)}")
        print("   Please set these environment variables or update .env file")
    else:
        print("✅ Configuration validated")

    # Run Flask development server
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
