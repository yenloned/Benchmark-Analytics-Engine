"""
Financial Analyzer Module
Contains all calculations for benchmark comparison metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import stats
from datetime import datetime

class PortfolioAnalyzer:
    """Main class for portfolio analysis and benchmark comparison"""
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize analyzer
        
        Args:
            risk_free_rate: Annual risk-free rate (default 2%)
        """
        self.risk_free_rate = risk_free_rate
        self.risk_free_rate_daily = (1 + risk_free_rate) ** (1/252) - 1
    
    def analyze_portfolio_vs_benchmark(
        self, 
        portfolio_prices: pd.DataFrame, 
        benchmark_prices: pd.Series,
        portfolio_name: str = "Portfolio",
        benchmark_name: str = "Benchmark",
        weights: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Main analysis function - compares portfolio against benchmark
        
        Args:
            portfolio_prices: DataFrame with portfolio stock prices
            benchmark_prices: Series with benchmark prices
            portfolio_name: Name for portfolio
            benchmark_name: Name for benchmark
            weights: Dictionary of stock weights (e.g., {'AAPL': 0.3, 'MSFT': 0.7})
            
        Returns:
            Dictionary with all analysis results
        """
        try:
            # Calculate returns
            portfolio_returns = self._calculate_portfolio_returns(portfolio_prices, weights)
            benchmark_returns = benchmark_prices.pct_change().dropna()
            
            # Align data (same time period)
            aligned_data = self._align_data(portfolio_returns, benchmark_returns)
            if aligned_data is None:
                return {}
            
            portfolio_returns, benchmark_returns = aligned_data
            
            # Calculate metrics
            results = {
                'portfolio_name': portfolio_name,
                'benchmark_name': benchmark_name,
                'analysis_date': datetime.now().strftime("%Y-%m-%d"),
                'data_points': len(portfolio_returns),
                'start_date': portfolio_returns.index[0].strftime("%Y-%m-%d"),
                'end_date': portfolio_returns.index[-1].strftime("%Y-%m-%d"),
                'weights_used': weights if weights else 'equal-weighted',
                
                # Performance metrics
                'portfolio_total_return': self._calculate_total_return(portfolio_returns),
                'benchmark_total_return': self._calculate_total_return(benchmark_returns),
                'excess_return': self._calculate_excess_return(portfolio_returns, benchmark_returns),
                
                # Risk metrics
                'portfolio_volatility': self._calculate_volatility(portfolio_returns),
                'benchmark_volatility': self._calculate_volatility(benchmark_returns),
                'portfolio_sharpe_ratio': self._calculate_sharpe_ratio(portfolio_returns),
                'benchmark_sharpe_ratio': self._calculate_sharpe_ratio(benchmark_returns),
                
                # Benchmark comparison metrics
                'alpha': self._calculate_alpha(portfolio_returns, benchmark_returns),
                'beta': self._calculate_beta(portfolio_returns, benchmark_returns),
                'correlation': self._calculate_correlation(portfolio_returns, benchmark_returns),
                'r_squared': self._calculate_r_squared(portfolio_returns, benchmark_returns),
                'tracking_error': self._calculate_tracking_error(portfolio_returns, benchmark_returns),
                'information_ratio': self._calculate_information_ratio(portfolio_returns, benchmark_returns),
                
                # Risk analysis
                'max_drawdown': self._calculate_max_drawdown(portfolio_returns),
                'var_95': self._calculate_var(portfolio_returns, 0.95),
                'var_99': self._calculate_var(portfolio_returns, 0.99),
                
                # Additional metrics
                'up_capture': self._calculate_up_capture(portfolio_returns, benchmark_returns),
                'down_capture': self._calculate_down_capture(portfolio_returns, benchmark_returns),
                'calmar_ratio': self._calculate_calmar_ratio(portfolio_returns),
                
                # Raw data for charts
                'portfolio_returns': portfolio_returns,
                'benchmark_returns': benchmark_returns,
                'cumulative_returns': self._calculate_cumulative_returns(portfolio_returns, benchmark_returns)
            }
            
            return results
            
        except Exception as e:
            print(f"Error in portfolio analysis: {e}")
            return {}
    
    def _calculate_portfolio_returns(self, portfolio_prices: pd.DataFrame, weights: Optional[Dict[str, float]] = None) -> pd.Series:
        """Calculate portfolio returns with optional custom weights"""
        # Calculate individual stock returns
        stock_returns = portfolio_prices.pct_change().dropna()
        
        if weights is None:
            # Equal-weighted portfolio (simple average)
            portfolio_returns = stock_returns.mean(axis=1)
        else:
            # Custom-weighted portfolio
            portfolio_returns = pd.Series(0.0, index=stock_returns.index)
            
            for symbol, weight in weights.items():
                if symbol in stock_returns.columns:
                    portfolio_returns += stock_returns[symbol] * weight
            
            # Normalize weights if they don't sum to 1
            total_weight = sum(weights.values())
            if total_weight != 0:
                portfolio_returns = portfolio_returns / total_weight
        
        return portfolio_returns
    
    def _align_data(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> Optional[Tuple[pd.Series, pd.Series]]:
        """Align portfolio and benchmark data to same time period"""
        try:
            # Find common dates
            common_dates = portfolio_returns.index.intersection(benchmark_returns.index)
            
            if len(common_dates) < 30:  # Need at least 30 days of data
                print("Insufficient overlapping data")
                return None
            
            # Align data
            portfolio_aligned = portfolio_returns.loc[common_dates]
            benchmark_aligned = benchmark_returns.loc[common_dates]
            
            return portfolio_aligned, benchmark_aligned
            
        except Exception as e:
            print(f"Error aligning data: {e}")
            return None
    
    def _calculate_total_return(self, returns: pd.Series) -> float:
        """Calculate total return from daily returns"""
        return (1 + returns).prod() - 1
    
    def _calculate_excess_return(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """Calculate excess return (portfolio - benchmark)"""
        portfolio_total = self._calculate_total_return(portfolio_returns)
        benchmark_total = self._calculate_total_return(benchmark_returns)
        return portfolio_total - benchmark_total
    
    def _calculate_volatility(self, returns: pd.Series) -> float:
        """Calculate annualized volatility"""
        return returns.std() * np.sqrt(252)
    
    def _calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate Sharpe ratio (risk-adjusted return)"""
        excess_returns = returns - self.risk_free_rate_daily
        if returns.std() == 0:
            return 0
        return (excess_returns.mean() * 252) / (returns.std() * np.sqrt(252))
    
    def _calculate_alpha(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """Calculate Jensen's Alpha"""
        beta = self._calculate_beta(portfolio_returns, benchmark_returns)
        
        portfolio_annual_return = portfolio_returns.mean() * 252
        benchmark_annual_return = benchmark_returns.mean() * 252
        
        alpha = portfolio_annual_return - (self.risk_free_rate + beta * (benchmark_annual_return - self.risk_free_rate))
        return alpha
    
    def _calculate_beta(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """Calculate Beta (market sensitivity)"""
        covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
        variance = np.var(benchmark_returns)
        
        if variance == 0:
            return 0
        
        return covariance / variance
    
    def _calculate_correlation(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """Calculate correlation coefficient"""
        return portfolio_returns.corr(benchmark_returns)
    
    def _calculate_r_squared(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """Calculate R-squared (coefficient of determination)"""
        correlation = self._calculate_correlation(portfolio_returns, benchmark_returns)
        return correlation ** 2
    
    def _calculate_tracking_error(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """Calculate tracking error (annualized)"""
        excess_returns = portfolio_returns - benchmark_returns
        return excess_returns.std() * np.sqrt(252)
    
    def _calculate_information_ratio(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """Calculate information ratio"""
        excess_returns = portfolio_returns - benchmark_returns
        tracking_error = self._calculate_tracking_error(portfolio_returns, benchmark_returns)
        
        if tracking_error == 0:
            return 0
        
        return (excess_returns.mean() * 252) / tracking_error
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def _calculate_var(self, returns: pd.Series, confidence_level: float) -> float:
        """Calculate Value at Risk"""
        return np.percentile(returns, (1 - confidence_level) * 100)
    
    def _calculate_up_capture(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """Calculate up capture ratio"""
        up_periods = benchmark_returns > 0
        if not up_periods.any():
            return 0
        
        portfolio_up_return = portfolio_returns[up_periods].mean()
        benchmark_up_return = benchmark_returns[up_periods].mean()
        
        if benchmark_up_return == 0:
            return 0
        
        return portfolio_up_return / benchmark_up_return
    
    def _calculate_down_capture(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """Calculate down capture ratio"""
        down_periods = benchmark_returns < 0
        if not down_periods.any():
            return 0
        
        portfolio_down_return = portfolio_returns[down_periods].mean()
        benchmark_down_return = benchmark_returns[down_periods].mean()
        
        if benchmark_down_return == 0:
            return 0
        
        return portfolio_down_return / benchmark_down_return
    
    def _calculate_calmar_ratio(self, returns: pd.Series) -> float:
        """Calculate Calmar ratio (return / max drawdown)"""
        total_return = self._calculate_total_return(returns)
        max_drawdown = abs(self._calculate_max_drawdown(returns))
        
        if max_drawdown == 0:
            return 0
        
        return total_return / max_drawdown
    
    def _calculate_cumulative_returns(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> pd.DataFrame:
        """Calculate cumulative returns for both portfolio and benchmark"""
        portfolio_cumulative = (1 + portfolio_returns).cumprod()
        benchmark_cumulative = (1 + benchmark_returns).cumprod()
        
        return pd.DataFrame({
            'Portfolio': portfolio_cumulative,
            'Benchmark': benchmark_cumulative
        })
    
    def format_results(self, results: Dict) -> Dict:
        """Format results for display (convert to percentages, round numbers)"""
        if not results:
            return {}
        
        formatted = results.copy()
        
        # Convert to percentages and round
        percentage_fields = [
            'portfolio_total_return', 'benchmark_total_return', 'excess_return',
            'portfolio_volatility', 'benchmark_volatility', 'alpha',
            'tracking_error', 'max_drawdown', 'var_95', 'var_99'
        ]
        
        for field in percentage_fields:
            if field in formatted:
                formatted[field] = round(formatted[field] * 100, 2)
        
        # Round other metrics
        decimal_fields = [
            'portfolio_sharpe_ratio', 'benchmark_sharpe_ratio', 'beta',
            'correlation', 'r_squared', 'information_ratio',
            'up_capture', 'down_capture', 'calmar_ratio'
        ]
        
        for field in decimal_fields:
            if field in formatted:
                formatted[field] = round(formatted[field], 4)
        
        return formatted 