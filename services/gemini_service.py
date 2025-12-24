"""Gemini AI service for vision and text processing."""

import json
import re
from typing import Optional

import google.generativeai as genai

from config import Config


# Prompt for parsing transaction screenshots
PARSE_TRANSACTION_PROMPT = """You are a financial transaction parser. Analyze this screenshot from a trading app and extract the transaction details.

The screenshot is from either:
1. **Dime!** - A Thai app for US stocks and gold trading
2. **Binance** - A crypto exchange

Extract the following information and return ONLY a valid JSON object (no markdown, no explanation):

{
    "source_app": "Dime" or "Binance",
    "asset": "The asset symbol (e.g., XAUUSD for gold, AAPL for Apple stock, BTC for Bitcoin)",
    "side": "BUY" or "SELL",
    "amount": <number - the quantity purchased/sold>,
    "price": <number - the price per unit>,
    "total_thb": <number - total value in THB if shown, otherwise calculate>,
    "date": "YYYY-MM-DD format if visible, otherwise null",
    "confidence": "high", "medium", or "low"
}

Rules:
- For Dime! gold trades, the asset is usually "XAUUSD" or "Gold"
- For Dime! stock trades, extract the stock ticker symbol
- For Binance, extract the crypto symbol (BTC, ETH, etc.)
- If you cannot determine a field with certainty, use null
- Always return valid JSON only, no other text
"""


class GeminiService:
    """Service for Gemini AI operations."""

    def __init__(self):
        """Initialize the Gemini service."""
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)

    def parse_transaction_image(self, image_bytes: bytes) -> Optional[dict]:
        """Parse a transaction screenshot using Gemini Vision.

        Args:
            image_bytes: The image data as bytes

        Returns:
            Parsed transaction data as dict, or None if parsing failed
        """
        try:
            # Create image part for Gemini
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_bytes,
            }

            # Send to Gemini Vision
            response = self.model.generate_content(
                [PARSE_TRANSACTION_PROMPT, image_part],
                generation_config=genai.GenerationConfig(
                    temperature=0.1,  # Low temperature for consistent parsing
                    max_output_tokens=500,
                ),
            )

            # Extract JSON from response
            response_text = response.text.strip()

            # Try to extract JSON if wrapped in markdown code blocks
            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response_text)
            if json_match:
                response_text = json_match.group(1)

            # Parse JSON
            parsed = json.loads(response_text)

            # Validate required fields
            required_fields = ["source_app", "asset", "side", "amount"]
            if not all(parsed.get(f) for f in required_fields):
                return None

            return parsed

        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            return None
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None

    def generate_response(self, prompt: str) -> str:
        """Generate a text response using Gemini.

        Args:
            prompt: The text prompt

        Returns:
            Generated response text
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            return "ขออภัย ไม่สามารถประมวลผลได้ในขณะนี้"


# Singleton instance
gemini_service = GeminiService()
