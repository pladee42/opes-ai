"""Rebalance calculator with drift detection and actionable buy/sell instructions."""

from typing import Optional


def calculate_rebalance_actions(
    target_allocation: dict,
    current_values: dict,
    quantities: dict,
    prices: dict,
    usd_thb_rate: float,
    threshold: float = 5.0,
) -> dict:
    """Calculate portfolio drift and actionable rebalance instructions.
    
    Args:
        target_allocation: Dict of {asset: target_percent}
        current_values: Dict of {asset: current_value_thb}
        quantities: Dict of {asset: quantity}
        prices: Dict of {asset: price_thb}
        usd_thb_rate: Current USD/THB exchange rate
        threshold: Drift threshold percentage to trigger action
        
    Returns:
        Dict with drift analysis and buy/sell recommendations
    """
    total_portfolio = sum(current_values.values())
    
    if total_portfolio <= 0:
        return {"error": "ไม่มีข้อมูลพอร์ตโฟลิโอ", "actions": []}
    
    actions = []
    total_drift_assets = 0
    
    # Include all assets from both target allocation and current holdings
    all_assets = set(target_allocation.keys()) | set(current_values.keys())
    
    for asset in all_assets:
        current_value = current_values.get(asset, 0)
        target_pct = target_allocation.get(asset, 0)
        qty = quantities.get(asset, 0)
        price = prices.get(asset, 0)
        
        # Calculate current percentage
        current_pct = (current_value / total_portfolio * 100) if total_portfolio > 0 else 0
        
        # Calculate drift
        drift = current_pct - target_pct
        
        # Determine status
        if abs(drift) >= threshold:
            total_drift_assets += 1
            if drift > 0:
                status = "overweight"  # Need to sell
            else:
                status = "underweight"  # Need to buy
        else:
            status = "balanced"
        
        # Calculate action amount
        target_value = total_portfolio * (target_pct / 100)
        value_diff = target_value - current_value  # Positive = need to buy, Negative = need to sell
        
        # Calculate quantity to trade
        if price > 0:
            qty_to_trade = abs(value_diff) / price
        else:
            qty_to_trade = 0
        
        # Calculate USD amounts
        value_diff_usd = abs(value_diff) / usd_thb_rate if usd_thb_rate else 0
        
        action = {
            "asset": asset,
            "current_pct": current_pct,
            "target_pct": target_pct,
            "drift": drift,
            "status": status,
            "action_type": "sell" if drift > 0 else "buy" if drift < 0 else "hold",
            "qty_to_trade": qty_to_trade,
            "value_thb": abs(value_diff),
            "value_usd": value_diff_usd,
            "current_qty": qty,
            "price_thb": price,
        }
        
        actions.append(action)
    
    # Sort by absolute drift (most imbalanced first)
    actions.sort(key=lambda x: abs(x["drift"]), reverse=True)
    
    return {
        "total_portfolio": total_portfolio,
        "total_drift_assets": total_drift_assets,
        "threshold": threshold,
        "actions": actions,
    }
