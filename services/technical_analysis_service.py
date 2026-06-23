"""Technical analysis service using yfinance and pandas-ta for indicator computation."""

import logging
import numpy as np
import pandas as pd
import pandas_ta as ta
import yfinance as yf
from typing import Optional

from services.price_service import PriceService

logger = logging.getLogger(__name__)


class TechnicalAnalysisService:
    """Service for computing technical analysis indicators (EMA, RSI, VRVP, Fibonacci)."""

    YFINANCE_SYMBOL_MAP = {
        "GOLD": "GC=F",
        "XAUUSD": "GC=F",
        "XAU": "GC=F",
    }

    def get_yf_symbol(self, ticker: str) -> str:
        """Map user ticker to yfinance symbol."""
        ticker_upper = ticker.upper().strip()
        if ticker_upper in self.YFINANCE_SYMBOL_MAP:
            return self.YFINANCE_SYMBOL_MAP[ticker_upper]
        if ticker_upper in PriceService.CRYPTO_TICKERS:
            return f"{ticker_upper}-USD"
        if "-" in ticker_upper:
            return ticker_upper
        return ticker_upper

    def compute_indicators(self, ticker: str) -> dict:
        """Fetch 1 year of daily historical data and compute technical indicators.

        Returns:
            Dict matching the asset_ingest_payload schema.
        """
        yf_symbol = self.get_yf_symbol(ticker)
        logger.info(f"Computing indicators for ticker: {ticker} (yfinance: {yf_symbol})")

        ticker_obj = yf.Ticker(yf_symbol)
        df = ticker_obj.history(period="1y")

        if df.empty or len(df) < 50:
            df = ticker_obj.history(period="2y")

        if df.empty:
            raise ValueError(f"No historical data found for {yf_symbol}")

        # Normalize column capitalization
        df.columns = [col.capitalize() for col in df.columns]

        current_price = float(df["Close"].iloc[-1])

        # 1. Compute EMA 50 & 200 using pandas-ta
        ema_50 = df.ta.ema(length=50)
        ema_200 = df.ta.ema(length=200)

        trend_data = self._compute_trend(df, current_price, ema_50, ema_200)

        # 2. Compute RSI 14
        rsi = df.ta.rsi(length=14)
        momentum_data = self._classify_rsi(rsi)

        # Detect divergence
        bearish_div, bullish_div = self._detect_divergence(df, rsi)
        momentum_data["bearish_divergence_detected"] = bearish_div
        momentum_data["bullish_divergence_detected"] = bullish_div

        # 3. Compute Volume Profile (VRVP)
        vp_data = self._compute_volume_profile(df, current_price)

        # 4. Compute Fibonacci Retracements
        fib_data = self._compute_fibonacci(df)

        return {
            "metadata": {
                "ticker": ticker.upper(),
                "yfinance_symbol": yf_symbol,
                "current_price": current_price,
                "timestamp": pd.Timestamp.now().isoformat(),
            },
            "metrics": {
                "trend": trend_data,
                "momentum": momentum_data,
                "volume_profile": vp_data,
                "fibonacci": fib_data,
            }
        }

    def _compute_trend(
        self, df: pd.DataFrame, price: float, ema_50: Optional[pd.Series], ema_200: Optional[pd.Series]
    ) -> dict:
        """Determine trend classification based on EMA 50 and 200."""
        ema_50_val = float(ema_50.iloc[-1]) if ema_50 is not None and not ema_50.empty and not pd.isna(ema_50.iloc[-1]) else None
        ema_200_val = float(ema_200.iloc[-1]) if ema_200 is not None and not ema_200.empty and not pd.isna(ema_200.iloc[-1]) else None

        macro_condition = "NEUTRAL"
        dist_50 = 0.0
        dist_200 = 0.0

        if ema_50_val is not None and ema_200_val is not None:
            if price > ema_50_val > ema_200_val:
                macro_condition = "BULLISH_EXPANSION"
            elif ema_50_val > ema_200_val and price < ema_50_val:
                macro_condition = "BULLISH_REVERSION"
            elif price < ema_50_val < ema_200_val:
                macro_condition = "BEARISH_EXPANSION"
            elif ema_50_val < ema_200_val and price > ema_50_val:
                macro_condition = "BEARISH_REVERSION"

            dist_50 = ((price - ema_50_val) / ema_50_val) * 100
            dist_200 = ((price - ema_200_val) / ema_200_val) * 100
        elif ema_50_val is not None:
            if price > ema_50_val:
                macro_condition = "BULLISH_EXPANSION"
            else:
                macro_condition = "BEARISH_EXPANSION"
            dist_50 = ((price - ema_50_val) / ema_50_val) * 100

        return {
            "macro_condition": macro_condition,
            "ema_50_price": ema_50_val,
            "ema_200_price": ema_200_val,
            "distance_from_50_ema_pct": dist_50,
            "distance_from_200_ema_pct": dist_200,
        }

    def _classify_rsi(self, rsi: Optional[pd.Series]) -> dict:
        """Classify RSI value and compute velocity."""
        if rsi is None or rsi.empty or pd.isna(rsi.iloc[-1]):
            return {
                "rsi_value": None,
                "rsi_condition": "NEUTRAL",
                "rsi_3d_velocity": 0.0,
                "bearish_divergence_detected": False,
                "bullish_divergence_detected": False,
            }

        rsi_val = float(rsi.iloc[-1])

        if rsi_val > 70:
            rsi_condition = "OVERBOUGHT"
        elif rsi_val > 55:
            rsi_condition = "NEUTRAL_HIGH"
        elif rsi_val < 30:
            rsi_condition = "OVERSOLD"
        elif rsi_val < 45:
            rsi_condition = "NEUTRAL_LOW"
        else:
            rsi_condition = "NEUTRAL"

        # Velocity over 3 days (current - 3 days ago)
        rsi_3d_velocity = 0.0
        if len(rsi) >= 4:
            rsi_3d_velocity = float(rsi.iloc[-1] - rsi.iloc[-4])

        return {
            "rsi_value": rsi_val,
            "rsi_condition": rsi_condition,
            "rsi_3d_velocity": rsi_3d_velocity,
        }

    def _detect_divergence(self, df: pd.DataFrame, rsi: Optional[pd.Series], lookback: int = 20) -> tuple[bool, bool]:
        """Detect bullish or bearish divergence over the last 20 bars."""
        if len(df) < lookback or rsi is None or len(rsi) < lookback:
            return False, False

        recent_df = df.iloc[-lookback:]
        recent_rsi = rsi.iloc[-lookback:]

        mid = lookback // 2
        seg1_df = recent_df.iloc[:mid]
        seg2_df = recent_df.iloc[mid:]

        seg1_rsi = recent_rsi.iloc[:mid]
        seg2_rsi = recent_rsi.iloc[mid:]

        # 1. Bearish Divergence (Price Higher High, RSI Lower High)
        idx1_high = seg1_df["High"].idxmax()
        idx2_high = seg2_df["High"].idxmax()

        price1_high = seg1_df.loc[idx1_high, "High"]
        price2_high = seg2_df.loc[idx2_high, "High"]

        rsi1_high = seg1_rsi.loc[idx1_high]
        rsi2_high = seg2_rsi.loc[idx2_high]

        bearish_div = False
        if price2_high > price1_high and rsi2_high < rsi1_high:
            bearish_div = True

        # 2. Bullish Divergence (Price Lower Low, RSI Higher Low)
        idx1_low = seg1_df["Low"].idxmin()
        idx2_low = seg2_df["Low"].idxmin()

        price1_low = seg1_df.loc[idx1_low, "Low"]
        price2_low = seg2_df.loc[idx2_low, "Low"]

        rsi1_low = seg1_rsi.loc[idx1_low]
        rsi2_low = seg2_rsi.loc[idx2_low]

        bullish_div = False
        if price2_low < price1_low and rsi2_low > rsi1_low:
            bullish_div = True

        return bearish_div, bullish_div

    def _compute_volume_profile(self, df: pd.DataFrame, price: float) -> dict:
        """Compute Volume Profile (VRVP) from the last 60 days of data."""
        vp_df = df.iloc[-60:]
        min_p = float(vp_df["Low"].min())
        max_p = float(vp_df["High"].max())

        if max_p == min_p:
            return {
                "point_of_control_price": price,
                "immediate_support_hvn": price,
                "immediate_resistance_hvn": price,
                "liquidity_gap_below": {
                    "detected": False,
                    "start_price": 0.0,
                    "end_price": 0.0,
                }
            }

        num_bins = 50
        bins = np.zeros(num_bins)
        bin_edges = np.linspace(min_p, max_p, num_bins + 1)
        bin_centers = bin_edges[:-1] + (max_p - min_p) / (2 * num_bins)
        bin_width = (max_p - min_p) / num_bins

        for _, row in vp_df.iterrows():
            high = row["High"]
            low = row["Low"]
            vol = row["Volume"]
            if pd.isna(high) or pd.isna(low) or pd.isna(vol) or vol <= 0:
                continue

            if high == low:
                bin_idx = min(max(0, int((low - min_p) / bin_width)), num_bins - 1)
                bins[bin_idx] += vol
            else:
                overlap_indices = []
                for i in range(num_bins):
                    if bin_edges[i] <= high and bin_edges[i+1] >= low:
                        overlap_indices.append(i)
                if overlap_indices:
                    val_per_bin = vol / len(overlap_indices)
                    for i in overlap_indices:
                        bins[i] += val_per_bin

        poc_idx = int(np.argmax(bins))
        poc_price = float(bin_centers[poc_idx])

        # High Volume Nodes (HVNs): volume >= 80% of max volume (POC volume)
        hvn_threshold = 0.8 * bins[poc_idx] if bins[poc_idx] > 0 else 0
        hvn_indices = [i for i, v in enumerate(bins) if v >= hvn_threshold]

        immediate_support_hvn = min_p
        immediate_resistance_hvn = max_p

        support_candidates = [bin_centers[i] for i in hvn_indices if bin_centers[i] < price]
        if support_candidates:
            immediate_support_hvn = float(support_candidates[-1])

        resistance_candidates = [bin_centers[i] for i in hvn_indices if bin_centers[i] > price]
        if resistance_candidates:
            immediate_resistance_hvn = float(resistance_candidates[0])

        # Liquidity Gap (LVN): >= 3 consecutive bins with volume <= 20% of max volume between price and POC
        lvn_threshold = 0.2 * bins[poc_idx] if bins[poc_idx] > 0 else 0
        price_bin_idx = min(max(0, int((price - min_p) / bin_width)), num_bins - 1)

        start_idx = min(price_bin_idx, poc_idx)
        end_idx = max(price_bin_idx, poc_idx)

        consecutive_lvn = []
        max_consecutive_lvn = []

        for i in range(start_idx, end_idx + 1):
            if bins[i] <= lvn_threshold:
                consecutive_lvn.append(i)
            else:
                if len(consecutive_lvn) > len(max_consecutive_lvn):
                    max_consecutive_lvn = list(consecutive_lvn)
                consecutive_lvn = []
        if len(consecutive_lvn) > len(max_consecutive_lvn):
            max_consecutive_lvn = list(consecutive_lvn)

        gap_detected = len(max_consecutive_lvn) >= 3
        gap_start = float(bin_edges[max_consecutive_lvn[0]]) if gap_detected else 0.0
        gap_end = float(bin_edges[max_consecutive_lvn[-1] + 1]) if gap_detected else 0.0

        return {
            "point_of_control_price": poc_price,
            "immediate_support_hvn": immediate_support_hvn,
            "immediate_resistance_hvn": immediate_resistance_hvn,
            "liquidity_gap_below": {
                "detected": gap_detected,
                "start_price": gap_start,
                "end_price": gap_end,
            }
        }

    def _compute_fibonacci(self, df: pd.DataFrame) -> dict:
        """Compute Fibonacci Retracement levels from swing high/low in last 120 bars."""
        swing_df = df.iloc[-120:]
        swing_low = float(swing_df["Low"].min())
        swing_high = float(swing_df["High"].max())

        idx_low = swing_df["Low"].idxmin()
        idx_high = swing_df["High"].idxmax()
        is_uptrend = idx_low < idx_high

        price = float(df["Close"].iloc[-1])
        diff = swing_high - swing_low

        fib_prices = {}
        if diff == 0:
            fib_prices = {lvl: swing_high for lvl in ["0.236", "0.382", "0.5", "0.618", "0.786"]}
        elif is_uptrend:
            fib_prices["0.236"] = swing_high - 0.236 * diff
            fib_prices["0.382"] = swing_high - 0.382 * diff
            fib_prices["0.5"] = swing_high - 0.5 * diff
            fib_prices["0.618"] = swing_high - 0.618 * diff
            fib_prices["0.786"] = swing_high - 0.786 * diff
        else:
            fib_prices["0.236"] = swing_low + 0.236 * diff
            fib_prices["0.382"] = swing_low + 0.382 * diff
            fib_prices["0.5"] = swing_low + 0.5 * diff
            fib_prices["0.618"] = swing_low + 0.618 * diff
            fib_prices["0.786"] = swing_low + 0.786 * diff

        # Find closest level to current price
        closest_level = "0.5"
        closest_price = fib_prices["0.5"]
        min_diff = abs(price - closest_price)

        for lvl, lvl_price in fib_prices.items():
            d = abs(price - lvl_price)
            if d < min_diff:
                min_diff = d
                closest_level = lvl
                closest_price = lvl_price

        distance_pct = ((price - closest_price) / closest_price) * 100 if closest_price > 0 else 0.0

        return {
            "anchor_swing_low": swing_low,
            "anchor_swing_high": swing_high,
            "closest_level_ratio": closest_level,
            "closest_level_price": closest_price,
            "distance_to_level_pct": distance_pct,
            "golden_pocket_zone": {
                "fib_05_price": fib_prices["0.5"],
                "fib_0618_price": fib_prices["0.618"],
            }
        }


# Singleton instance
ta_service = TechnicalAnalysisService()
