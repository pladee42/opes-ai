#!/usr/bin/env python3
"""Unit tests for the DigestService."""

import os
import sys
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

# Adjust path to import services
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.digest_service import DigestService


@pytest.fixture
def mock_user_daily():
    return {
        "user_id": "U123456",
        "display_name": "Test User",
        "digest_enabled": True,
        "digest_frequency": "daily",
        "digest_time": "07:00",
        "digest_assets": '["GOLD", "BTC"]'
    }


@pytest.fixture
def mock_user_weekly():
    return {
        "user_id": "U123456",
        "display_name": "Test User",
        "digest_enabled": True,
        "digest_frequency": "weekly",
        "digest_time": "07:00",
        "digest_day": "monday",
        "digest_assets": '["GOLD"]'
    }


@pytest.fixture
def mock_user_monthly():
    return {
        "user_id": "U123456",
        "display_name": "Test User",
        "digest_enabled": True,
        "digest_frequency": "monthly",
        "digest_time": "18:00",
        "digest_assets": '["BTC"]'
    }


def test_should_send_daily_success(mock_user_daily):
    """Test that daily schedule matches when hour matches."""
    service = DigestService()
    
    # Mock current ICT time to 07:15 AM
    mock_now = datetime(2026, 6, 22, 7, 15, tzinfo=timezone(timedelta(hours=7)))
    
    with patch.object(service, "get_current_time_ict", return_value=mock_now):
        assert service.should_send_now(mock_user_daily) is True


def test_should_not_send_daily_wrong_hour(mock_user_daily):
    """Test that daily schedule fails when hour does not match."""
    service = DigestService()
    
    # Mock current ICT time to 15:30 PM
    mock_now = datetime(2026, 6, 22, 15, 30, tzinfo=timezone(timedelta(hours=7)))
    
    with patch.object(service, "get_current_time_ict", return_value=mock_now):
        assert service.should_send_now(mock_user_daily) is False


def test_should_send_weekly_success(mock_user_weekly):
    """Test that weekly schedule matches when day and hour match."""
    service = DigestService()
    
    # June 22, 2026 is a Monday. ICT time 07:00
    mock_now = datetime(2026, 6, 22, 7, 0, tzinfo=timezone(timedelta(hours=7)))
    
    with patch.object(service, "get_current_time_ict", return_value=mock_now):
        assert service.should_send_now(mock_user_weekly) is True


def test_should_not_send_weekly_wrong_day(mock_user_weekly):
    """Test that weekly schedule fails when hour matches but day does not."""
    service = DigestService()
    
    # June 23, 2026 is a Tuesday. ICT time 07:00
    mock_now = datetime(2026, 6, 23, 7, 0, tzinfo=timezone(timedelta(hours=7)))
    
    with patch.object(service, "get_current_time_ict", return_value=mock_now):
        assert service.should_send_now(mock_user_weekly) is False


def test_should_send_monthly_success(mock_user_monthly):
    """Test that monthly schedule matches on the 1st of the month at the correct hour."""
    service = DigestService()
    
    # June 1, 2026 (1st of month). ICT time 18:00
    mock_now = datetime(2026, 6, 1, 18, 0, tzinfo=timezone(timedelta(hours=7)))
    
    with patch.object(service, "get_current_time_ict", return_value=mock_now):
        assert service.should_send_now(mock_user_monthly) is True


def test_should_not_send_monthly_wrong_day(mock_user_monthly):
    """Test that monthly schedule fails on the 2nd of the month."""
    service = DigestService()
    
    # June 2, 2026. ICT time 18:00
    mock_now = datetime(2026, 6, 2, 18, 0, tzinfo=timezone(timedelta(hours=7)))
    
    with patch.object(service, "get_current_time_ict", return_value=mock_now):
        assert service.should_send_now(mock_user_monthly) is False


def test_should_not_send_disabled(mock_user_daily):
    """Test that schedule returns False if digest is disabled."""
    service = DigestService()
    mock_user_daily["digest_enabled"] = False
    
    mock_now = datetime(2026, 6, 22, 7, 0, tzinfo=timezone(timedelta(hours=7)))
    with patch.object(service, "get_current_time_ict", return_value=mock_now):
        assert service.should_send_now(mock_user_daily) is False


@patch("services.digest_service.gemini_service")
def test_generate_narrative(mock_gemini, mock_user_daily):
    """Test format prompt and narrative call to Gemini."""
    mock_gemini.generate_response.return_value = "บทวิเคราะห์จำลองภาษาไทยสำหรับ BTC"
    
    service = DigestService()
    payload = {
        "metadata": {
            "ticker": "BTC",
            "yfinance_symbol": "BTC-USD",
            "current_price": 92450.0,
            "timestamp": "2026-06-23T07:00:00"
        },
        "metrics": {
            "trend": {
                "macro_condition": "BULLISH_EXPANSION",
                "ema_50_price": 88766.0,
                "ema_200_price": 82177.0,
                "distance_from_50_ema_pct": 4.15,
                "distance_from_200_ema_pct": 12.50
            },
            "momentum": {
                "rsi_value": 64.20,
                "rsi_condition": "NEUTRAL_HIGH",
                "rsi_3d_velocity": 2.10,
                "bearish_divergence_detected": False,
                "bullish_divergence_detected": False
            },
            "volume_profile": {
                "point_of_control_price": 88000.0,
                "immediate_support_hvn": 91200.0,
                "immediate_resistance_hvn": 94800.0,
                "liquidity_gap_below": {
                    "detected": True,
                    "start_price": 88000.0,
                    "end_price": 91200.0
                }
            },
            "fibonacci": {
                "anchor_swing_low": 74000.0,
                "anchor_swing_high": 95000.0,
                "closest_level_ratio": "0.236",
                "closest_level_price": 90044.0,
                "distance_to_level_pct": -2.60,
                "golden_pocket_zone": {
                    "fib_05_price": 84500.0,
                    "fib_0618_price": 82022.0
                }
            }
        }
    }
    
    result = service.generate_narrative("BTC", payload)
    
    assert result == "บทวิเคราะห์จำลองภาษาไทยสำหรับ BTC"
    mock_gemini.generate_response.assert_called_once()
    prompt_sent = mock_gemini.generate_response.call_args[0][0]
    
    assert "BTC/USDT" in prompt_sent
    assert "$92,450.00" in prompt_sent
    assert "BULLISH_EXPANSION (ขาขึ้นแข็งแกร่ง)" in prompt_sent
    assert "$91,200.00" in prompt_sent
    assert "$94,800.00" in prompt_sent
    assert "23.6%" in prompt_sent


@patch("services.digest_service.sheets_service")
@patch("services.digest_service.ta_service")
@patch("services.digest_service.gemini_service")
def test_generate_digest_success(mock_gemini, mock_ta, mock_sheets):
    """Test full generate_digest pipeline for a user with multiple tracked assets."""
    mock_sheets.get_user.return_value = {
        "user_id": "U123456",
        "display_name": "Test User",
        "digest_enabled": True,
        "digest_assets": '["GOLD", "BTC"]',
        "target_allocation": {"GOLD": 50, "BTC": 50}
    }
    
    mock_ta.compute_indicators.side_effect = lambda ticker: {
        "metadata": {
            "ticker": ticker.upper(),
            "yfinance_symbol": ticker,
            "current_price": 100.0 if ticker == "GOLD" else 92450.0,
            "timestamp": "2026-06-23T07:00:00"
        },
        "metrics": {
            "trend": {
                "macro_condition": "BULLISH_EXPANSION",
                "ema_50_price": 95.0,
                "ema_200_price": 90.0,
                "distance_from_50_ema_pct": 5.0,
                "distance_from_200_ema_pct": 10.0
            },
            "momentum": {
                "rsi_value": 60.0,
                "rsi_condition": "NEUTRAL_HIGH",
                "rsi_3d_velocity": 2.0,
                "bearish_divergence_detected": False,
                "bullish_divergence_detected": False
            },
            "volume_profile": {
                "point_of_control_price": 90.0,
                "immediate_support_hvn": 92.0,
                "immediate_resistance_hvn": 98.0,
                "liquidity_gap_below": {
                    "detected": False,
                    "start_price": 0.0,
                    "end_price": 0.0
                }
            },
            "fibonacci": {
                "anchor_swing_low": 80.0,
                "anchor_swing_high": 120.0,
                "closest_level_ratio": "0.5",
                "closest_level_price": 100.0,
                "distance_to_level_pct": 0.0,
                "golden_pocket_zone": {
                    "fib_05_price": 100.0,
                    "fib_0618_price": 95.0
                }
            }
        }
    }
    
    mock_gemini.generate_response.return_value = "Mock Thai analysis"
    
    service = DigestService()
    results = service.generate_digest("U123456")
    
    assert len(results) == 2
    assert results[0]["ticker"] == "GOLD"
    assert results[1]["ticker"] == "BTC"
    assert results[0]["narrative"] == "Mock Thai analysis"
    assert results[1]["narrative"] == "Mock Thai analysis"

