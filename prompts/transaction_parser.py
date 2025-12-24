"""Prompt templates for Gemini AI."""

# Prompt for parsing transaction screenshots
PARSE_TRANSACTION_PROMPT = """You are a financial transaction parser. Analyze this screenshot from a trading app and extract the transaction details.

The screenshot is from either:
1. **Dime!** - A Thai app for US stocks and gold trading (can show prices in USD or THB)
2. **Binance** - A crypto exchange (usually in USDT)

Extract the following information and return ONLY a valid JSON object (no markdown, no explanation):

{
    "source_app": "Dime" or "Binance",
    "asset_raw": "The exact asset name/symbol shown in the screenshot",
    "asset_type": "STOCK", "GOLD", or "CRYPTO",
    "asset_normalized": "See normalization rules below",
    "side": "BUY" or "SELL",
    "amount": <number - the quantity purchased/sold>,
    "price": <number - the price per unit>,
    "currency": "USD" or "THB" or "USDT" (the currency shown in the screenshot),
    "total": <number - total transaction value in the original currency>,
    "date": "YYYY-MM-DD format if visible, otherwise null",
    "confidence": "high", "medium", or "low"
}

## Asset Normalization Rules:

### Gold (asset_type = "GOLD"):
All gold assets should be normalized to "XAUUSD" for consistent price tracking.
- Dime! gold: MTS-GOLD, YLG-GOLD, GOLD, ทองคำ → normalize to "XAUUSD"
- Binance gold: PAXG, XAUT → normalize to "XAUUSD"

### Stocks (asset_type = "STOCK"):
Keep the original ticker symbol as-is.
- AAPL, TSLA, NVDA, etc. → keep as-is (e.g., "AAPL")

### Crypto (asset_type = "CRYPTO"):
Keep the base crypto symbol only (without trading pair suffix).
- BTC/USDT, BTCUSDT → normalize to "BTC"
- ETH/USDT, ETHUSDT → normalize to "ETH"
- SOL/USDT → normalize to "SOL"

## Currency Detection:
- "$" or "USD" → currency = "USD"
- "฿" or "THB" or "บาท" → currency = "THB"  
- "USDT" → currency = "USDT"

## Important:
- asset_raw = exactly what's shown in the screenshot
- asset_normalized = the standardized symbol for price tracking
- If you cannot determine a field with certainty, use null
- Always return valid JSON only, no other text
"""
