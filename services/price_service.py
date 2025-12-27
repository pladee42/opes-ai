"""Price service using Tiingo API for stocks, crypto, and forex/gold."""

import requests
from typing import Optional
from datetime import datetime, timedelta

from config import Config


class PriceError(Exception):
    """Raised when price data cannot be fetched."""
    pass


class PriceService:
    """Service for fetching real-time prices from Tiingo."""

    BASE_URL = "https://api.tiingo.com"
    
    # Known crypto tickers
    CRYPTO_TICKERS = {
        "BTC", "ETH", "XLM", "SOL", "DOGE", "XRP", "ADA", "DOT", 
        "MATIC", "AVAX", "LINK", "UNI", "ATOM", "LTC", "BCH"
    }
    
    # Forex pairs (including GOLD as xauusd)
    FOREX_TICKERS = {
        "GOLD": "xauusd",
        "XAUUSD": "xauusd",
        "THB": "thbusd",  # For USD to THB conversion
    }

    def __init__(self):
        """Initialize the price service."""
        self.api_key = Config.TIINGO_API_KEY
        self.headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }
        self._thb_rate_cache: Optional[float] = None
        self._thb_rate_timestamp: Optional[datetime] = None

    def _is_crypto(self, ticker: str) -> bool:
        """Check if ticker is a cryptocurrency."""
        return ticker.upper() in self.CRYPTO_TICKERS

    def _is_forex(self, ticker: str) -> bool:
        """Check if ticker is in forex/commodities."""
        return ticker.upper() in self.FOREX_TICKERS

    def _get_stock_price(self, ticker: str) -> Optional[float]:
        """Fetch stock price from IEX endpoint."""
        try:
            url = f"{self.BASE_URL}/iex/{ticker.lower()}/prices"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return float(data[0].get("last", data[0].get("close", 0)))
            return None
        except Exception as e:
            print(f"Error fetching stock price for {ticker}: {e}")
            return None

    def _get_crypto_price(self, ticker: str) -> Optional[float]:
        """Fetch crypto price from crypto endpoint."""
        try:
            # Tiingo crypto format: btcusd
            crypto_ticker = f"{ticker.lower()}usd"
            url = f"{self.BASE_URL}/tiingo/crypto/prices"
            params = {"tickers": crypto_ticker}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    price_data = data[0].get("priceData", [])
                    if price_data:
                        return float(price_data[0].get("close", 0))
            return None
        except Exception as e:
            print(f"Error fetching crypto price for {ticker}: {e}")
            return None

    def _get_forex_price(self, ticker: str) -> Optional[float]:
        """Fetch forex/gold price from forex endpoint."""
        try:
            # Map our ticker to Tiingo forex pair
            forex_pair = self.FOREX_TICKERS.get(ticker.upper(), f"{ticker.lower()}usd")
            # Correct Tiingo forex endpoint format
            url = f"{self.BASE_URL}/tiingo/fx/top?tickers={forex_pair}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    # Use mid price (average of bid and ask)
                    bid = float(data[0].get("bidPrice", 0))
                    ask = float(data[0].get("askPrice", 0))
                    return (bid + ask) / 2 if bid and ask else None
            return None
        except Exception as e:
            print(f"Error fetching forex price for {ticker}: {e}")
            return None

    def get_usd_thb_rate(self) -> float:
        """Get current USD to THB exchange rate with caching.
        
        Raises:
            PriceError: If unable to fetch exchange rate
        """
        # Cache for 5 minutes
        if (self._thb_rate_cache and self._thb_rate_timestamp and 
            datetime.now() - self._thb_rate_timestamp < timedelta(minutes=5)):
            return self._thb_rate_cache
        
        # Use frankfurter.app (free, no API key needed)
        try:
            url = "https://api.frankfurter.app/latest?from=USD&to=THB"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                rate = data.get("rates", {}).get("THB")
                if rate:
                    self._thb_rate_cache = rate
                    self._thb_rate_timestamp = datetime.now()
                    return self._thb_rate_cache
        except Exception as e:
            raise PriceError(f"ไม่สามารถดึงอัตราแลกเปลี่ยน USD/THB ได้: {e}")
        
        raise PriceError("ไม่สามารถดึงอัตราแลกเปลี่ยน USD/THB ได้")

    def get_price_usd(self, ticker: str) -> Optional[float]:
        """Get price in USD for any asset type."""
        ticker_upper = ticker.upper()
        
        if self._is_forex(ticker_upper):
            return self._get_forex_price(ticker_upper)
        elif self._is_crypto(ticker_upper):
            return self._get_crypto_price(ticker_upper)
        else:
            # Default to stock
            return self._get_stock_price(ticker_upper)

    def get_price_thb(self, ticker: str) -> Optional[float]:
        """Get price in THB for any asset type."""
        price_usd = self.get_price_usd(ticker)
        if price_usd is None:
            return None
        
        thb_rate = self.get_usd_thb_rate()
        return price_usd * thb_rate

    def get_prices_thb(self, tickers: list[str]) -> dict[str, float]:
        """Get prices for multiple tickers in THB.
        
        Returns:
            Dict of {ticker: price_thb}, missing tickers are excluded
        """
        prices = {}
        thb_rate = self.get_usd_thb_rate()  # Fetch once for efficiency
        
        for ticker in tickers:
            price_usd = self.get_price_usd(ticker)
            if price_usd is not None:
                prices[ticker] = price_usd * thb_rate
        
        return prices

    # Legacy method for backward compatibility
    def convert_to_thb(self, amount: float, currency: str) -> float:
        """Convert an amount to THB."""
        currency = currency.upper().strip()
        
        if currency == "THB":
            return amount
        elif currency in ("USD", "USDT"):
            return amount * self.get_usd_thb_rate()
        
        return amount


# Singleton instance
price_service = PriceService()
