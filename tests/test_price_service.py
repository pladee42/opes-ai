#!/usr/bin/env python3
"""Test script for price_service USD/THB conversion."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import directly to avoid loading other services
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import PriceService class directly
from services.price_service import PriceService
price_service = PriceService()

def test_forex_api():
    """Test the forex API directly."""
    print("=" * 50)
    print("Testing Tiingo Forex API for USD/THB")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv("TIINGO_API_KEY")
    if not api_key:
        print("❌ TIINGO_API_KEY not found in environment!")
        return
    print(f"✅ API Key found: {api_key[:8]}...")
    
    # Test forex endpoint directly
    print("\n--- Testing Forex Endpoint ---")
    import requests
    
    url = "https://api.tiingo.com/tiingo/fx/thbusd/top"
    headers = {"Authorization": f"Token {api_key}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Forex data received:")
            print(f"   Data: {data}")
            if data and len(data) > 0:
                mid_price = data[0].get("midPrice")
                print(f"   midPrice (THB per 1 USD): {1/mid_price if mid_price else 'N/A'}")
        else:
            print(f"❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_price_service():
    """Test the PriceService methods."""
    print("\n" + "=" * 50)
    print("Testing PriceService Methods")
    print("=" * 50)
    
    # Test USD/THB rate
    print("\n--- get_usd_thb_rate() ---")
    rate = price_service.get_usd_thb_rate()
    print(f"USD/THB Rate: {rate}")
    if rate == 34.0:
        print("⚠️  WARNING: Using fallback rate (34.0)!")
    else:
        print(f"✅ Live rate fetched: {rate:.4f}")
    
    # Test some price lookups
    print("\n--- get_price_thb() for various assets ---")
    test_tickers = ["GOOGL", "BTC", "GOLD", "ORCL"]
    
    for ticker in test_tickers:
        price_usd = price_service.get_price_usd(ticker)
        price_thb = price_service.get_price_thb(ticker)
        usd_str = f"{price_usd:,.2f}" if price_usd else "N/A"
        thb_str = f"{price_thb:,.2f}" if price_thb else "N/A"
        print(f"{ticker:8} USD: {usd_str:>12} | THB: {thb_str:>14}")
    
    # Batch test
    print("\n--- get_prices_thb() batch ---")
    prices = price_service.get_prices_thb(test_tickers)
    for ticker, price in prices.items():
        print(f"{ticker:8} THB: {price:,.2f}")

if __name__ == "__main__":
    test_forex_api()
    test_price_service()
