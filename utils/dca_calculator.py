"""Smart DCA Calculator with Rebalance-by-Buying logic."""

from typing import Optional


def calculate_dca_rebalance(
    monthly_budget: float,
    target_allocation: dict,
    current_holdings: dict,
    asset_prices: Optional[dict] = None,
) -> dict:
    """Calculate how to allocate monthly budget to rebalance portfolio.
    
    Rebalance-by-Buying: Allocate more to underweight assets to fix imbalance.
    
    Args:
        monthly_budget: Amount to invest this month (THB)
        target_allocation: Dict of {asset: target_percent}
        current_holdings: Dict of {asset: current_value_thb}
        asset_prices: Optional dict of {asset: price_thb} for display
        
    Returns:
        Dict with buy recommendations and analysis
    """
    if not target_allocation:
        return {"error": "No target allocation set"}
    
    # Calculate total current portfolio value
    total_portfolio = sum(current_holdings.values()) if current_holdings else 0
    
    # Calculate new total after adding budget
    new_total = total_portfolio + monthly_budget
    
    # Calculate target values for each asset
    recommendations = []
    
    for asset, target_pct in target_allocation.items():
        current_value = current_holdings.get(asset, 0)
        
        # Target value after adding budget
        target_value = new_total * (target_pct / 100)
        
        # How much to buy to reach target
        buy_amount = max(0, target_value - current_value)
        
        # Current allocation percentage
        current_pct = (current_value / total_portfolio * 100) if total_portfolio > 0 else 0
        
        # Deviation from target
        deviation = current_pct - target_pct
        
        recommendations.append({
            "asset": asset,
            "target_pct": target_pct,
            "current_pct": round(current_pct, 1),
            "current_value": round(current_value, 2),
            "buy_amount": round(buy_amount, 2),
            "deviation": round(deviation, 1),
            "status": "underweight" if deviation < -5 else ("overweight" if deviation > 5 else "balanced"),
        })
    
    # Sort by deviation (most underweight first)
    recommendations.sort(key=lambda x: x["deviation"])
    
    # Adjust buy amounts to fit within budget
    total_recommended = sum(r["buy_amount"] for r in recommendations)
    
    if total_recommended > monthly_budget:
        # Scale down proportionally
        scale = monthly_budget / total_recommended
        for r in recommendations:
            r["buy_amount"] = round(r["buy_amount"] * scale, 2)
    elif total_recommended < monthly_budget:
        # Distribute remaining to underweight assets
        remaining = monthly_budget - total_recommended
        underweight = [r for r in recommendations if r["status"] == "underweight"]
        if underweight:
            extra_each = remaining / len(underweight)
            for r in underweight:
                r["buy_amount"] = round(r["buy_amount"] + extra_each, 2)
        else:
            # Distribute evenly if all balanced
            extra_each = remaining / len(recommendations)
            for r in recommendations:
                r["buy_amount"] = round(r["buy_amount"] + extra_each, 2)
    
    return {
        "monthly_budget": monthly_budget,
        "current_portfolio": round(total_portfolio, 2),
        "new_portfolio": round(new_total, 2),
        "recommendations": recommendations,
    }


def format_dca_message(result: dict, usd_thb_rate: float = None) -> str:
    """Format DCA calculation result as a readable message.
    
    Args:
        result: Output from calculate_dca_rebalance
        usd_thb_rate: Optional USD/THB exchange rate for USD display
        
    Returns:
        Formatted Thai text message
    """
    if "error" in result:
        return f"❌ {result['error']}"
    
    budget = result["monthly_budget"]
    recs = result["recommendations"]
    
    lines = [
        f"📋 **แผน DCA เดือนนี้**",
        f"💰 งบ: ฿{budget:,.0f}",
        "",
    ]
    
    for r in recs:
        status_emoji = "🔴" if r["status"] == "underweight" else ("🟢" if r["status"] == "overweight" else "⚪")
        
        lines.append(f"{status_emoji} **{r['asset']}**")
        
        # Format buy amount with optional USD
        buy_text = f"   ซื้อ: ฿{r['buy_amount']:,.0f}"
        if usd_thb_rate:
            usd_amount = r['buy_amount'] / usd_thb_rate
            buy_text += f" (${usd_amount:,.2f})"
        lines.append(buy_text)
        
        if r["current_value"] > 0:
            lines.append(f"   ปัจจุบัน: ฿{r['current_value']:,.0f} ({r['current_pct']:.0f}% → {r['target_pct']:.0f}%)")
        else:
            lines.append(f"   เป้า: {r['target_pct']:.0f}%")
        lines.append("")
    
    lines.append("🔴 = น้ำหนักต่ำ | 🟢 = น้ำหนักเกิน | ⚪ = สมดุล")
    
    return "\n".join(lines)
