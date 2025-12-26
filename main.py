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

# Enable CORS for API endpoints
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "Family Wealth AI"}


@app.route("/api/allocation", methods=["POST", "OPTIONS"])
def save_allocation():
    """API endpoint for LIFF to save user allocation."""
    # Handle preflight request
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        return response
    
    from services.sheets_service import sheets_service
    from utils.normalizer import normalize_allocation
    
    data = request.get_json()
    user_id = data.get("user_id")
    allocation = data.get("allocation", {})
    monthly_budget = data.get("monthly_budget")
    
    if not user_id or not allocation:
        return {"error": "Missing user_id or allocation"}, 400
    
    # Normalize asset names (e.g., "BTCUSDT" -> "BTC", "Gold" -> "GOLD")
    normalized_allocation = normalize_allocation(allocation)
    
    # Build update data
    update_data = {
        "target_allocation": normalized_allocation,
        "onboarding_status": "ACTIVE",
    }
    
    # Include budget if provided
    if monthly_budget:
        update_data["monthly_budget"] = int(monthly_budget)
    
    # Update user's allocation
    success = sheets_service.update_user(user_id, update_data)
    
    if success:
        # Send push message to confirm save
        from services.line_service import line_service
        
        budget_text = f"งบ: ฿{monthly_budget:,}/เดือน\n" if monthly_budget else ""
        allocation_text = "\n".join([f"• {ticker}: {weight}%" for ticker, weight in normalized_allocation.items()])
        
        message = f"✅ บันทึกแผนลงทุนเรียบร้อย!\n\n{budget_text}📊 สัดส่วน:\n{allocation_text}\n\n💡 พิมพ์ #dca เพื่อดูแผนซื้อ"
        line_service.push_text(user_id, message)
        
        return {"status": "ok", "message": "Allocation saved", "normalized": normalized_allocation}
    else:
        return {"error": "User not found"}, 404


@app.route("/api/user/<user_id>", methods=["GET", "OPTIONS"])
def get_user_settings(user_id):
    """API endpoint for LIFF to get user settings."""
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        return response
    
    from services.sheets_service import sheets_service
    
    user = sheets_service.get_user(user_id)
    
    if user:
        return {
            "status": "ok",
            "monthly_budget": user.get("monthly_budget", 10000),
            "target_allocation": user.get("target_allocation", {}),
            "display_name": user.get("display_name", ""),
        }
    else:
        # New user - return defaults
        return {
            "status": "ok",
            "monthly_budget": None,
            "target_allocation": {},
            "display_name": "",
        }

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
