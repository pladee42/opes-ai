#!/usr/bin/env python3
"""Unit tests for the TechnicalAnalysisService."""

import os
import sys
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

# Adjust path to import services
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.technical_analysis_service import TechnicalAnalysisService


@pytest.fixture
def sample_ohlcv_data():
    """Generates 250 days of dummy bullish OHLCV data."""
    np.random.seed(42)
    dates = pd.date_range(end="2026-06-23", periods=250, freq="D")
    
    # Create a generally upward trending price series
    base_price = 100.0
    price_trend = np.linspace(0, 50, 250)  # price goes from 100 to 150
    noise = np.random.normal(0, 2, 250)
    close_prices = base_price + price_trend + noise
    
    high_prices = close_prices + np.random.uniform(0.5, 3.0, 250)
    low_prices = close_prices - np.random.uniform(0.5, 3.0, 250)
    open_prices = close_prices + np.random.uniform(-1.0, 1.0, 250)
    volume = np.random.uniform(1000, 5000, 250)
    
    df = pd.DataFrame({
        "Open": open_prices,
        "High": high_prices,
        "Low": low_prices,
        "Close": close_prices,
        "Volume": volume
    }, index=dates)
    
    return df


def test_trend_bullish_expansion(sample_ohlcv_data):
    """Test BULLISH_EXPANSION condition: Close > EMA50 > EMA200."""
    service = TechnicalAnalysisService()
    
    # We will mock the dataframe and EMA outputs to verify the condition logic
    df = sample_ohlcv_data.copy()
    close_price = 150.0
    df.loc[df.index[-1], "Close"] = close_price
    
    # Under bullish expansion, Price (150) > EMA50 (130) > EMA200 (110)
    ema_50 = pd.Series([130.0] * 250, index=df.index)
    ema_200 = pd.Series([110.0] * 250, index=df.index)
    
    trend = service._compute_trend(df, close_price, ema_50, ema_200)
    
    assert trend["macro_condition"] == "BULLISH_EXPANSION"
    assert trend["ema_50_price"] == 130.0
    assert trend["ema_200_price"] == 110.0
    assert pytest.approx(trend["distance_from_50_ema_pct"], 0.01) == 15.38  # (150-130)/130 * 100
    assert pytest.approx(trend["distance_from_200_ema_pct"], 0.01) == 36.36  # (150-110)/110 * 100


def test_trend_bullish_reversion(sample_ohlcv_data):
    """Test BULLISH_REVERSION condition: EMA50 > EMA200, Price < EMA50."""
    service = TechnicalAnalysisService()
    df = sample_ohlcv_data.copy()
    close_price = 120.0
    df.loc[df.index[-1], "Close"] = close_price
    
    ema_50 = pd.Series([130.0] * 250, index=df.index)
    ema_200 = pd.Series([110.0] * 250, index=df.index)
    
    trend = service._compute_trend(df, close_price, ema_50, ema_200)
    assert trend["macro_condition"] == "BULLISH_REVERSION"


def test_trend_bearish_expansion(sample_ohlcv_data):
    """Test BEARISH_EXPANSION condition: Close < EMA50 < EMA200."""
    service = TechnicalAnalysisService()
    df = sample_ohlcv_data.copy()
    close_price = 80.0
    df.loc[df.index[-1], "Close"] = close_price
    
    ema_50 = pd.Series([100.0] * 250, index=df.index)
    ema_200 = pd.Series([120.0] * 250, index=df.index)
    
    trend = service._compute_trend(df, close_price, ema_50, ema_200)
    assert trend["macro_condition"] == "BEARISH_EXPANSION"


def test_trend_bearish_reversion(sample_ohlcv_data):
    """Test BEARISH_REVERSION condition: EMA50 < EMA200, Price > EMA50."""
    service = TechnicalAnalysisService()
    df = sample_ohlcv_data.copy()
    close_price = 110.0
    df.loc[df.index[-1], "Close"] = close_price
    
    ema_50 = pd.Series([100.0] * 250, index=df.index)
    ema_200 = pd.Series([120.0] * 250, index=df.index)
    
    trend = service._compute_trend(df, close_price, ema_50, ema_200)
    assert trend["macro_condition"] == "BEARISH_REVERSION"


def test_rsi_zones():
    """Verify RSI classification zones."""
    service = TechnicalAnalysisService()
    
    # Helper to construct minimal rsi Series
    def rsi_series(val, change_last_3d=0.0):
        index = pd.date_range("2026-06-20", periods=4)
        vals = [val - change_last_3d, val - change_last_3d/2, val - change_last_3d/3, val]
        return pd.Series(vals, index=index)
    
    assert service._classify_rsi(rsi_series(75))["rsi_condition"] == "OVERBOUGHT"
    assert service._classify_rsi(rsi_series(60))["rsi_condition"] == "NEUTRAL_HIGH"
    assert service._classify_rsi(rsi_series(50))["rsi_condition"] == "NEUTRAL"
    assert service._classify_rsi(rsi_series(35))["rsi_condition"] == "NEUTRAL_LOW"
    assert service._classify_rsi(rsi_series(25))["rsi_condition"] == "OVERSOLD"
    
    # Check velocity
    momentum = service._classify_rsi(rsi_series(60, change_last_3d=5.0))
    assert pytest.approx(momentum["rsi_3d_velocity"], 0.01) == 5.0


def test_fibonacci_retracement():
    """Verify Fibonacci swing detection and level logic."""
    service = TechnicalAnalysisService()
    
    # Construct a dataframe with a clear Swing Low and Swing High
    dates = pd.date_range(end="2026-06-23", periods=100, freq="D")
    df = pd.DataFrame({
        "High": [100.0] * 100,
        "Low": [100.0] * 100,
        "Close": [100.0] * 100
    }, index=dates)
    
    # Create Swing Low at index 30: Low = 50.0
    df.loc[df.index[30], "Low"] = 50.0
    df.loc[df.index[30], "Close"] = 52.0
    
    # Create Swing High at index 70: High = 150.0
    df.loc[df.index[70], "High"] = 150.0
    df.loc[df.index[70], "Close"] = 148.0
    
    # Let's set the last price to 111.8 (which is exactly 0.382 retracement from swing high 150 to swing low 50)
    # Swing range = 150 - 50 = 100
    # 0.382 level = 150 - (0.382 * 100) = 111.8
    # Close = 112.0
    df.loc[df.index[-1], "Close"] = 112.0
    df.loc[df.index[-1], "High"] = 113.0
    df.loc[df.index[-1], "Low"] = 111.0
    
    fib = service._compute_fibonacci(df)
    
    assert fib["anchor_swing_low"] == 50.0
    assert fib["anchor_swing_high"] == 150.0
    assert fib["closest_level_ratio"] == "0.382"
    assert pytest.approx(fib["closest_level_price"], 0.1) == 111.8
    assert pytest.approx(fib["distance_to_level_pct"], 0.1) == 0.18 # (112 - 111.8) / 111.8 * 100
    assert fib["golden_pocket_zone"]["fib_05_price"] == 100.0
    assert fib["golden_pocket_zone"]["fib_0618_price"] == 88.2


def test_volume_profile():
    """Verify Point of Control and support/resistance HVN detection."""
    service = TechnicalAnalysisService()
    
    # Create a 60-day dataframe where volume is concentrated at 100.0 and 120.0
    dates = pd.date_range(end="2026-06-23", periods=60, freq="D")
    df = pd.DataFrame({
        "High": [100.0] * 60,
        "Low": [100.0] * 60,
        "Close": [100.0] * 60,
        "Volume": [100.0] * 60
    }, index=dates)
    
    # Put extremely high volume at $120.0
    df.loc[df.index[10:20], "High"] = 120.0
    df.loc[df.index[10:20], "Low"] = 120.0
    df.loc[df.index[10:20], "Close"] = 120.0
    df.loc[df.index[10:20], "Volume"] = 10000.0  # Point of Control
    
    # Put medium-high volume at $90.0
    df.loc[df.index[30:35], "High"] = 90.0
    df.loc[df.index[30:35], "Low"] = 90.0
    df.loc[df.index[30:35], "Close"] = 90.0
    df.loc[df.index[30:35], "Volume"] = 5000.0  # Support HVN
    
    # Current price is 110.0
    price = 110.0
    vp = service._compute_volume_profile(df, price)
    
    assert pytest.approx(vp["point_of_control_price"], 2.0) == 120.0
    assert vp["immediate_support_hvn"] < price
    assert vp["immediate_resistance_hvn"] > price
