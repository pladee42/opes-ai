"""Asset name normalization utilities."""

import re

# Gold asset mappings
GOLD_ALIASES = {
    "GOLD", "XAUUSD", "XAU", "MTS-GOLD", "YLG-GOLD", "PAXG", "XAUT",
    "ทองคำ", "ทอง", "MTSGOLD", "YLGGOLD"
}

# Crypto pairs to strip
CRYPTO_PAIRS = ["USDT", "USD", "BUSD", "THB", "BTC", "ETH"]


def normalize_asset(raw_asset: str) -> str:
    """Normalize asset name to standard format.
    
    Args:
        raw_asset: Raw asset name from user input
        
    Returns:
        Normalized asset name
    """
    if not raw_asset:
        return raw_asset
    
    # Uppercase and strip whitespace
    asset = raw_asset.upper().strip()
    
    # Check if it's gold
    if asset in GOLD_ALIASES or "GOLD" in asset:
        return "GOLD"
    
    # Check if it's crypto with pair suffix
    for pair in CRYPTO_PAIRS:
        if asset.endswith(pair) and len(asset) > len(pair):
            base = asset[:-len(pair)]
            # Make sure we don't strip too much (e.g., "BTC" from "BTC")
            if len(base) >= 2:
                return base
    
    # Remove common separators
    asset = re.sub(r'[-/_]', '', asset)
    
    return asset


def normalize_allocation(allocation: dict) -> dict:
    """Normalize all asset keys in an allocation dict.
    
    Args:
        allocation: Dict of {asset: weight}
        
    Returns:
        Dict with normalized asset keys, merged if duplicates
    """
    normalized = {}
    
    for asset, weight in allocation.items():
        norm_asset = normalize_asset(asset)
        
        # Merge if same normalized asset
        if norm_asset in normalized:
            normalized[norm_asset] += weight
        else:
            normalized[norm_asset] = weight
    
    return normalized
