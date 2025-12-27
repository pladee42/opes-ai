import sys
import os
import unittest
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.price_service import price_service, PriceError

class TestPriceService(unittest.TestCase):
    
    def test_stock_price(self):
        """Test fetching stock prices for specific list."""
        tickers = ["NVDA"]
        print(f"\nTesting Stock Prices for: {tickers}")
        
        for ticker in tickers:
            with self.subTest(ticker=ticker):
                price = price_service.get_price_usd(ticker)
                print(f"  {ticker}: ${price:,.2f}" if price else f"  {ticker}: None")
                self.assertIsNotNone(price, f"Failed to fetch stock price for {ticker}")
                self.assertGreater(price, 0, f"Stock price for {ticker} should be > 0")

    def test_crypto_price(self):
        """Test fetching crypto prices (e.g., BTC, ETH)."""
        ticker = "BTC"
        print(f"\nTesting Crypto: {ticker}")
        price = price_service.get_price_usd(ticker)
        print(f"  Price: ${price:,.2f}" if price else "  Price: None")
        self.assertIsNotNone(price, f"Failed to fetch crypto price for {ticker}")
        self.assertGreater(price, 0, f"Crypto price for {ticker} should be > 0")

    def test_gold_price(self):
        """Test fetching Gold price (via Forex API as xauusd)."""
        ticker = "GOLD"
        print(f"\nTesting Gold (FX): {ticker}")
        price = price_service.get_price_usd(ticker)
        print(f"  Price: ${price:,.2f}" if price else "  Price: None")
        self.assertIsNotNone(price, f"Failed to fetch Gold price for {ticker}")
        self.assertGreater(price, 0, f"Gold price should be > 0")

    def test_usd_thb_rate(self):
        """Test fetching USD/THB exchange rate."""
        print(f"\nTesting USD/THB Rate")
        try:
            rate = price_service.get_usd_thb_rate()
            print(f"  Rate: ฿{rate:.2f}")
            self.assertIsNotNone(rate, "Failed to fetch USD/THB rate")
            self.assertGreater(rate, 20, "USD/THB rate seems too low")
            self.assertLess(rate, 40, "USD/THB rate seems too high")
        except PriceError as e:
            self.fail(f"PriceError fetching USD/THB rate: {e}")

if __name__ == '__main__':
    unittest.main(verbosity=2)
