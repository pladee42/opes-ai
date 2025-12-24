"""Gemini AI service for vision and text processing."""

import base64
import json
import re
from typing import Optional

from google import genai
from google.genai import types

from config import Config
from prompts.transaction_parser import PARSE_TRANSACTION_PROMPT


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

            print(f"🔧 Using model: {self.ocr_model}")

            # Send to Gemini Vision (using OCR model)
            # Note: Gemini 3 uses "thinking" tokens, so we need higher max_output_tokens
            response = self.client.models.generate_content(
                model=self.ocr_model,
                contents=[PARSE_TRANSACTION_PROMPT, image_part],
                config=types.GenerateContentConfig(
                    temperature=0.1,  # Low temperature for consistent parsing
                    max_output_tokens=8000,  # High enough for Gemini 3 thinking + output
                ),
            )

            # Debug: print full response
            print(f"🔍 Response object: {response}")
            print(f"🔍 Response candidates: {response.candidates if hasattr(response, 'candidates') else 'N/A'}")

            # Extract JSON from response - try different methods
            response_text = None
            if hasattr(response, 'text') and response.text:
                response_text = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                # Try to get text from candidates
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content.parts:
                    response_text = candidate.content.parts[0].text

            if not response_text:
                print("Gemini returned empty response")
                print(f"🔍 Full response dump: {vars(response) if hasattr(response, '__dict__') else response}")
                return None
            response_text = response_text.strip()

            # Try to extract JSON if wrapped in markdown code blocks
            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response_text)
            if json_match:
                response_text = json_match.group(1)

            # Parse JSON
            parsed = json.loads(response_text)
            print(f"✅ Parsed JSON: {parsed}")

            # Validate required fields (using asset_normalized from new prompt)
            required_fields = ["source_app", "asset_normalized", "side", "amount"]
            if not all(parsed.get(f) for f in required_fields):
                print(f"❌ Missing required fields. Got: {list(parsed.keys())}")
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
