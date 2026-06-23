"""Digest service for orchestrating technical analysis alerts and Gemini summaries."""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

from config import Config
from services.sheets_service import sheets_service
from services.technical_analysis_service import ta_service
from services.gemini_service import gemini_service
from prompts.digest_prompt import DIGEST_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


class DigestService:
    """Service to manage scheduling and generation of technical analysis digests."""

    MACRO_TREND_MAP = {
        "BULLISH_EXPANSION": "BULLISH_EXPANSION (ขาขึ้นแข็งแกร่ง)",
        "BULLISH_REVERSION": "BULLISH_REVERSION (ย่อตัวในขาขึ้น)",
        "BEARISH_EXPANSION": "BEARISH_EXPANSION (ขาลงแข็งแกร่ง)",
        "BEARISH_REVERSION": "BEARISH_REVERSION (ฟื้นตัวในขาลง)",
        "NEUTRAL": "NEUTRAL (ไซด์เวย์)",
    }

    RSI_ZONE_MAP = {
        "OVERBOUGHT": "Overbought (ซื้อมากเกินไป)",
        "NEUTRAL_HIGH": "Neutral High (ค่อนข้างแข็งแกร่ง)",
        "NEUTRAL": "Neutral (เป็นกลาง)",
        "NEUTRAL_LOW": "Neutral Low (ค่อนข้างอ่อนแอ)",
        "OVERSOLD": "Oversold (ขายมากเกินไป)",
    }

    def get_current_time_ict(self) -> datetime:
        """Get the current time in ICT (Bangkok) timezone."""
        return datetime.now(timezone(timedelta(hours=7)))

    def should_send_now(self, user: Dict[str, Any]) -> bool:
        """Check if the user is scheduled to receive a digest at the current hour."""
        # 1. Check if digest is enabled
        digest_enabled = user.get("digest_enabled", False)
        is_enabled = str(digest_enabled).upper() == "TRUE" or digest_enabled is True
        if not is_enabled:
            return False

        # 2. Check time preference (hour match)
        pref_time = str(user.get("digest_time", "07")).strip()
        pref_hour = pref_time.split(":")[0].zfill(2)

        current_time = self.get_current_time_ict()
        current_hour = str(current_time.hour).zfill(2)

        if current_hour != pref_hour:
            return False

        # 3. Check frequency preference
        frequency = str(user.get("digest_frequency", "daily")).strip().lower()

        if frequency == "daily":
            return True
        elif frequency == "weekly":
            pref_day = str(user.get("digest_day", "monday")).strip().lower()
            current_day = current_time.strftime("%A").lower()
            return current_day == pref_day
        elif frequency == "monthly":
            current_day_of_month = current_time.day
            return current_day_of_month == 1

        return False

    def generate_digest(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate real-time technical analysis and narratives for user's tracked assets."""
        user = sheets_service.get_user(user_id)
        if not user:
            logger.warning(f"User {user_id} not found in database.")
            return []

        # Parse user's tracked assets
        digest_assets = user.get("digest_assets", [])
        if isinstance(digest_assets, str):
            try:
                digest_assets = json.loads(digest_assets)
            except Exception:
                logger.error(f"Failed to parse digest_assets JSON for user {user_id}")
                digest_assets = []

        if not digest_assets:
            # Fallback to allocation assets if no specific digest assets are set
            target_allocation = user.get("target_allocation", {})
            if isinstance(target_allocation, dict):
                digest_assets = list(target_allocation.keys())

        if not digest_assets:
            logger.info(f"User {user_id} has no tracked assets for digest.")
            return []

        results = []
        for asset in digest_assets:
            try:
                # 1. Compute indicators
                payload = ta_service.compute_indicators(asset)

                # 2. Generate Thai narrative via Gemini
                narrative = self.generate_narrative(asset, payload)

                results.append({
                    "ticker": asset.upper(),
                    "indicators": payload,
                    "narrative": narrative
                })
            except Exception as e:
                logger.error(f"Error generating digest for asset {asset} for user {user_id}: {e}", exc_info=True)

        return results

    def generate_narrative(self, ticker: str, payload: Dict[str, Any]) -> str:
        """Format the Gemini prompt and call the Gemini Service to generate a Thai narrative."""
        metadata = payload["metadata"]
        metrics = payload["metrics"]
        
        trend = metrics["trend"]
        momentum = metrics["momentum"]
        vp = metrics["volume_profile"]
        fib = metrics["fibonacci"]

        # Formats and translations
        price_val = metadata["current_price"]
        current_price_str = f"${price_val:,.2f}"

        ticker_upper = ticker.upper()
        if ticker_upper == "GOLD":
            ticker_label = "GOLD (ทองคำ)"
        elif ticker_upper in ["BTC", "ETH", "SOL", "XRP", "DOGE"]:
            ticker_label = f"{ticker_upper}/USDT"
        else:
            ticker_label = ticker_upper

        macro_condition_th = self.MACRO_TREND_MAP.get(trend["macro_condition"], trend["macro_condition"])
        rsi_zone_th = self.RSI_ZONE_MAP.get(momentum["rsi_condition"], momentum["rsi_condition"])

        # Divergence message
        if momentum.get("bearish_divergence_detected"):
            divergence_status_th = "พบสัญญาณขัดแย้งขาลง Bearish Divergence"
        elif momentum.get("bullish_divergence_detected"):
            divergence_status_th = "พบสัญญาณขัดแย้งขาขึ้น Bullish Divergence"
        else:
            divergence_status_th = "ไม่พบสัญญาณขัดแย้งทางราคา (No Divergence)"

        # volume profile formatting
        poc_price_str = f"${vp['point_of_control_price']:,.2f}"
        support_hvn_str = f"${vp['immediate_support_hvn']:,.2f}"
        resistance_hvn_str = f"${vp['immediate_resistance_hvn']:,.2f}"

        # Fibonacci formatting
        fib_ratio_pct = float(fib["closest_level_ratio"]) * 100 if "." in fib["closest_level_ratio"] else float(fib["closest_level_ratio"])
        # Format ratio to clean string (e.g. 23.6, 50.0)
        fib_ratio_str = f"{fib_ratio_pct:.1f}" if fib_ratio_pct % 1 != 0 else f"{int(fib_ratio_pct)}"
        
        fib_price_str = f"${fib['closest_level_price']:,.2f}"
        fib_distance = fib["distance_to_level_pct"]
        fib_distance_str = f"{fib_distance:+.2f}"

        # Prepare prompt parameters
        prompt = DIGEST_PROMPT_TEMPLATE.format(
            json_payload=json.dumps(payload, indent=2, ensure_ascii=False),
            ticker_label=ticker_label,
            current_price=current_price_str,
            macro_condition_th=macro_condition_th,
            rsi_value=f"{momentum['rsi_value']:.2f}" if momentum['rsi_value'] is not None else "N/A",
            rsi_zone_th=rsi_zone_th,
            rsi_velocity=f"{momentum['rsi_3d_velocity']:+.2f}",
            divergence_status_th=divergence_status_th,
            resistance_hvn=resistance_hvn_str,
            support_hvn=support_hvn_str,
            poc_price=poc_price_str,
            fib_ratio=fib_ratio_str,
            fib_price=fib_price_str,
            fib_distance_pct=fib_distance_str
        )

        logger.info(f"Calling Gemini for {ticker} narrative summary...")
        response_text = gemini_service.generate_response(prompt, use_research_model=False)
        return response_text.strip()


# Singleton instance
digest_service = DigestService()
