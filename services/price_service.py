"""Price and currency service for fetching exchange rates and asset prices."""

import requests
from typing import Optional
from functools import lru_cache
from datetime import datetime


class PriceService:
    """Service for fetching exchange rates and asset prices."""

    # Free exchange rate API
    EXCHANGE_RATE_API = "https://api.exchangerate-api.com/v4/latest/USD"

    # Cache duration in seconds (1 hour)
    _cache_timestamp: Optional[datetime] = None
    _cached_rates: Optional[dict] = None
    CACHE_DURATION = 3600

    def get_usd_to_thb_rate(self) -> float:
        """Get current USD to THB exchange rate.

        Returns:
            Exchange rate (e.g., 34.5 means 1 USD = 34.5 THB)
        """
        rates = self._get_exchange_rates()
        if rates and "THB" in rates:
            return rates["THB"]

        # Fallback rate if API fails
        print("⚠️ Using fallback USD/THB rate: 35.0")
        return 35.0

    def _get_exchange_rates(self) -> Optional[dict]:
        """Fetch exchange rates from API with caching."""
        now = datetime.now()

        # Check cache
        if (
            self._cached_rates
            and self._cache_timestamp
            and (now - self._cache_timestamp).seconds < self.CACHE_DURATION
        ):
            return self._cached_rates

        try:
            response = requests.get(self.EXCHANGE_RATE_API, timeout=10)
            response.raise_for_status()
            data = response.json()

            self._cached_rates = data.get("rates", {})
            self._cache_timestamp = now

            print(f"💱 Updated exchange rates: USD/THB = {self._cached_rates.get('THB', 'N/A')}")
            return self._cached_rates

        except Exception as e:
            print(f"Error fetching exchange rates: {e}")
            return self._cached_rates  # Return stale cache if available

    def convert_to_thb(self, amount: float, currency: str) -> float:
        """Convert an amount to THB.

        Args:
            amount: The amount to convert
            currency: Source currency code (e.g., 'USD', 'THB')

        Returns:
            Amount in THB
        """
        currency = currency.upper().strip()

        if currency == "THB":
            return amount

        if currency == "USD":
            rate = self.get_usd_to_thb_rate()
            return amount * rate

        # For other currencies, try to get rate via USD
        rates = self._get_exchange_rates()
        if rates and currency in rates:
            # Convert to USD first, then to THB
            usd_amount = amount / rates[currency]
            return usd_amount * rates.get("THB", 35.0)

        print(f"⚠️ Unknown currency: {currency}, returning original amount")
        return amount


# Singleton instance
price_service = PriceService()
