"""Gemini AI service for vision and text processing."""

import base64
import json
import re
from typing import Optional

from google import genai
from google.genai import types

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
        """Initialize the Gemini service with dual models."""
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.ocr_model = Config.GEMINI_OCR_MODEL
        self.research_model = Config.GEMINI_RESEARCH_MODEL

    def parse_transaction_image(self, image_bytes: bytes) -> Optional[dict]:
        """Parse a transaction screenshot using Gemini Vision.

        Args:
            image_bytes: The image data as bytes

        Returns:
            Parsed transaction data as dict, or None if parsing failed
        """
        try:
            # Create image part for Gemini
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/jpeg",
            )

            # Send to Gemini Vision (using OCR model)
            response = self.client.models.generate_content(
                model=self.ocr_model,
                contents=[PARSE_TRANSACTION_PROMPT, image_part],
                config=types.GenerateContentConfig(
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

    def generate_response(self, prompt: str, use_research_model: bool = False) -> str:
        """Generate a text response using Gemini.

        Args:
            prompt: The text prompt
            use_research_model: If True, use the research model (Gemini 2.5)
                              If False, use the OCR model (faster)

        Returns:
            Generated response text
        """
        try:
            model = self.research_model if use_research_model else self.ocr_model
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            return "ขออภัย ไม่สามารถประมวลผลได้ในขณะนี้"

    def deep_research(self, prompt: str) -> str:
        """Perform deep research using Gemini 2.5 Pro.

        Use this for complex financial analysis, news research,
        and tasks requiring advanced reasoning.

        Args:
            prompt: The research prompt

        Returns:
            Research response text
        """
        return self.generate_response(prompt, use_research_model=True)


# Singleton instance
gemini_service = GeminiService()
