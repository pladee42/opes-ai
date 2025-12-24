"""Tests for Gemini service."""

import pytest
from unittest.mock import patch, MagicMock
import json


class TestGeminiService:
    """Test cases for GeminiService."""

    def test_parse_transaction_valid_dime_response(self):
        """Test parsing a valid Dime transaction response."""
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "source_app": "Dime",
            "asset": "XAUUSD",
            "side": "BUY",
            "amount": 0.5,
            "price": 2650,
            "total_thb": 46550,
            "date": "2024-12-24",
            "confidence": "high"
        })

        with patch("services.gemini_service.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            from services.gemini_service import GeminiService
            service = GeminiService()
            result = service.parse_transaction_image(b"fake_image_bytes")

            assert result is not None
            assert result["source_app"] == "Dime"
            assert result["asset"] == "XAUUSD"
            assert result["side"] == "BUY"
            assert result["amount"] == 0.5

    def test_parse_transaction_valid_binance_response(self):
        """Test parsing a valid Binance transaction response."""
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "source_app": "Binance",
            "asset": "BTC",
            "side": "BUY",
            "amount": 0.001,
            "price": 3500000,
            "total_thb": 3500,
            "date": "2024-12-24",
            "confidence": "high"
        })

        with patch("services.gemini_service.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            from services.gemini_service import GeminiService
            service = GeminiService()
            result = service.parse_transaction_image(b"fake_image_bytes")

            assert result is not None
            assert result["source_app"] == "Binance"
            assert result["asset"] == "BTC"

    def test_parse_transaction_invalid_json(self):
        """Test handling invalid JSON response."""
        mock_response = MagicMock()
        mock_response.text = "This is not valid JSON"

        with patch("services.gemini_service.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            from services.gemini_service import GeminiService
            service = GeminiService()
            result = service.parse_transaction_image(b"fake_image_bytes")

            assert result is None

    def test_parse_transaction_missing_required_fields(self):
        """Test handling response with missing required fields."""
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "source_app": "Dime",
            # Missing: asset, side, amount
        })

        with patch("services.gemini_service.genai") as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            from services.gemini_service import GeminiService
            service = GeminiService()
            result = service.parse_transaction_image(b"fake_image_bytes")

            assert result is None
