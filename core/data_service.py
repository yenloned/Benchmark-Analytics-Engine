"""
Data Service Module
Handles all data fetching from Yahoo Finance API
"""

import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional, Tuple
import time
from datetime import datetime, timedelta
import requests
import json

class YahooFinanceService:
    """Service for fetching stock and benchmark data from Yahoo Finance"""
    
    def __init__(self):
        # Define available benchmarks with their symbols
        self.benchmarks = {
            "S&P 500": "SPY",
            "Russell 2000": "IWM", 
            "NASDAQ 100": "QQQ",
            "MSCI World": "URTH",
            "Emerging Markets": "EEM"
        }
        
        # Available time periods
        self.periods = {
            "1 Month": "1mo",
            "3 Months": "3mo", 
            "6 Months": "6mo",
            "1 Year": "1y",
            "2 Years": "2y",
            "5 Years": "5y"
        }
        
        # Retry settings
        self.max_retries = 3
        self.retry_delay = 2
    
    def _test_connectivity(self) -> bool:
        """Test basic connectivity to Yahoo Finance"""
        try:
            # Try a simple request to test connectivity
            response = requests.get("https://finance.yahoo.com", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Connectivity test failed: {e}")
            # Don't fail completely - yfinance might still work
            return True  # Changed from False to True to allow fallback
    
    def get_stock_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Get historical data for a single stock with retry logic
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: Time period (e.g., '1y', '6mo')
            
        Returns:
            DataFrame with historical data or None if error
        """
        for attempt in range(self.max_retries):
            try:
                # Clean symbol (remove spaces, convert to uppercase)
                symbol = symbol.strip().upper()
                
                print(f"Attempt {attempt + 1}/{self.max_retries}: Fetching {symbol}")
                
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period)
                
                if data.empty:
                    print(f"No data found for {symbol} (attempt {attempt + 1})")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return None
                    
                print(f"Successfully fetched data for {symbol}: {data.shape}")
                return data
                
            except Exception as e:
                print(f"Error fetching data for {symbol} (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return None
        
        return None
    
    def get_portfolio_data(self, symbols: List[str], period: str = "1y") -> pd.DataFrame:
        """
        Get data for multiple stocks (portfolio) with improved error handling
        
        Args:
            symbols: List of stock symbols
            period: Time period
            
        Returns:
            DataFrame with closing prices for all stocks
        """
        portfolio_data = {}
        valid_symbols = []
        failed_symbols = []
        
        print(f"Fetching portfolio data for {len(symbols)} symbols...")
        
        for symbol in symbols:
            symbol = symbol.strip().upper()
            print(f"Processing {symbol}...")
            
            data = self.get_stock_data(symbol, period)
            
            if data is not None and not data.empty:
                portfolio_data[symbol] = data['Close']
                valid_symbols.append(symbol)
                print(f"✓ {symbol} data added")
            else:
                failed_symbols.append(symbol)
                print(f"✗ {symbol} failed")
            
            # Small delay to be respectful to the API
            time.sleep(0.2)
        
        if not portfolio_data:
            print(f"No valid data found for any symbols. Failed symbols: {failed_symbols}")
            return pd.DataFrame()
        
        df = pd.DataFrame(portfolio_data).dropna()
        
        if df.empty:
            print("No valid data found for any symbols after processing")
            return df
        
        print(f"Successfully fetched data for: {', '.join(valid_symbols)}")
        if failed_symbols:
            print(f"Failed symbols: {', '.join(failed_symbols)}")
        
        return df
    
    def get_benchmark_data(self, benchmark_name: str, period: str = "1y") -> Optional[pd.Series]:
        """
        Get benchmark data with retry logic
        
        Args:
            benchmark_name: Name of benchmark (e.g., 'S&P 500')
            period: Time period
            
        Returns:
            Series with benchmark closing prices or None if error
        """
        symbol = self.benchmarks.get(benchmark_name, "SPY")
        print(f"Fetching benchmark data for {benchmark_name} ({symbol})...")
        
        data = self.get_stock_data(symbol, period)
        
        if data is not None and not data.empty:
            print(f"✓ Benchmark data fetched successfully")
            return data['Close']
        
        print(f"✗ Failed to fetch benchmark data for {benchmark_name}")
        return None
    
    def get_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate daily returns from prices
        
        Args:
            prices: DataFrame with price data
            
        Returns:
            DataFrame with daily returns
        """
        return prices.pct_change().dropna()
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Check if a stock symbol is valid with improved error handling
        
        Args:
            symbol: Stock symbol to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            symbol = symbol.strip().upper()
            ticker = yf.Ticker(symbol)
            
            # Try to get basic info first
            try:
                info = ticker.info
                # Check if we can get basic info and price
                if 'regularMarketPrice' in info and info['regularMarketPrice'] is not None:
                    return True
            except Exception as e:
                print(f"Info API failed for {symbol}: {e}")
            
            # Fallback: try to get historical data
            try:
                data = ticker.history(period='1mo')
                return not data.empty
            except Exception as e:
                print(f"Historical data API failed for {symbol}: {e}")
                return False
            
        except Exception as e:
            print(f"Symbol validation failed for {symbol}: {e}")
            return False
    
    def get_available_benchmarks(self) -> List[str]:
        """Get list of available benchmark names"""
        return list(self.benchmarks.keys())
    
    def get_available_periods(self) -> List[str]:
        """Get list of available period names"""
        return list(self.periods.keys())
    
    def get_period_value(self, period_name: str) -> str:
        """Convert period name to yfinance period value"""
        return self.periods.get(period_name, "1y")

def safe_data_fetch(symbols: List[str], benchmark: str, period: str = "1y") -> Tuple[Optional[pd.DataFrame], Optional[pd.Series]]:
    """
    Safe data fetching with comprehensive error handling and retry logic
    
    Args:
        symbols: List of stock symbols
        benchmark: Benchmark name
        period: Time period
        
    Returns:
        Tuple of (portfolio_data, benchmark_data) or (None, None) if error
    """
    service = YahooFinanceService()
    
    print("=== Starting Data Fetch ===")
    print(f"Symbols: {symbols}")
    print(f"Benchmark: {benchmark}")
    print(f"Period: {period}")
    
    # Validate symbols first
    valid_symbols = []
    invalid_symbols = []
    
    for symbol in symbols:
        print(f"Validating {symbol}...")
        if service.validate_symbol(symbol):
            valid_symbols.append(symbol)
            print(f"✓ {symbol} is valid")
        else:
            invalid_symbols.append(symbol)
            print(f"✗ {symbol} is invalid")
    
    if not valid_symbols:
        print(f"ERROR: No valid symbols provided. Invalid symbols: {invalid_symbols}")
        return None, None
    
    if invalid_symbols:
        print(f"Warning: Some symbols are invalid: {invalid_symbols}")
    
    # Convert period name to value if needed
    if period in service.get_available_periods():
        period_value = service.get_period_value(period)
    else:
        period_value = period
    
    # Fetch data with retry logic
    for attempt in range(service.max_retries):
        try:
            print(f"\n=== Data Fetch Attempt {attempt + 1}/{service.max_retries} ===")
            
            print(f"Fetching portfolio data for: {', '.join(valid_symbols)}")
            portfolio_data = service.get_portfolio_data(valid_symbols, period_value)
            
            print(f"Fetching benchmark data for: {benchmark}")
            benchmark_data = service.get_benchmark_data(benchmark, period_value)
            
            if portfolio_data.empty:
                print("ERROR: Failed to fetch portfolio data")
                if attempt < service.max_retries - 1:
                    print(f"Retrying in {service.retry_delay} seconds...")
                    time.sleep(service.retry_delay)
                    continue
                return None, None
                
            if benchmark_data is None or benchmark_data.empty:
                print("ERROR: Failed to fetch benchmark data")
                if attempt < service.max_retries - 1:
                    print(f"Retrying in {service.retry_delay} seconds...")
                    time.sleep(service.retry_delay)
                    continue
                return None, None
            
            print("✓ Data fetching completed successfully!")
            print(f"Portfolio data shape: {portfolio_data.shape}")
            print(f"Benchmark data shape: {benchmark_data.shape}")
            return portfolio_data, benchmark_data
            
        except Exception as e:
            print(f"ERROR during data fetch (attempt {attempt + 1}): {e}")
            if attempt < service.max_retries - 1:
                print(f"Retrying in {service.retry_delay} seconds...")
                time.sleep(service.retry_delay)
                continue
            return None, None
    
    print("ERROR: All data fetch attempts failed")
    return None, None 