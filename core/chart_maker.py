"""
Chart Maker Module
Generates matplotlib charts for benchmark analysis
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

class ChartMaker:
    """Class for creating charts and visualizations"""
    
    def __init__(self):
        # Set style for professional-looking charts
        plt.style.use('default')
        self.colors = {
            'portfolio': '#1f77b4',  # Blue
            'benchmark': '#ff7f0e',  # Orange
            'excess': '#2ca02c',     # Green
            'risk': '#d62728',       # Red
            'grid': '#e0e0e0'        # Light gray
        }
    
    def create_performance_chart(self, cumulative_returns: pd.DataFrame, 
                                portfolio_name: str = "Portfolio",
                                benchmark_name: str = "Benchmark") -> Figure:
        """
        Create performance comparison chart
        
        Args:
            cumulative_returns: DataFrame with cumulative returns
            portfolio_name: Name for portfolio
            benchmark_name: Name for benchmark
            
        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot cumulative returns
        ax.plot(cumulative_returns.index, cumulative_returns['Portfolio'], 
                label=portfolio_name, color=self.colors['portfolio'], linewidth=2)
        ax.plot(cumulative_returns.index, cumulative_returns['Benchmark'], 
                label=benchmark_name, color=self.colors['benchmark'], linewidth=2)
        
        # Formatting
        ax.set_title(f'Performance Comparison: {portfolio_name} vs {benchmark_name}', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Cumulative Return', fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Add value labels
        final_portfolio = cumulative_returns['Portfolio'].iloc[-1]
        final_benchmark = cumulative_returns['Benchmark'].iloc[-1]
        
        ax.annotate(f'{final_portfolio:.2%}', 
                   xy=(cumulative_returns.index[-1], final_portfolio),
                   xytext=(10, 10), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor=self.colors['portfolio'], alpha=0.7),
                   fontsize=10, color='white')
        
        ax.annotate(f'{final_benchmark:.2%}', 
                   xy=(cumulative_returns.index[-1], final_benchmark),
                   xytext=(10, -20), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor=self.colors['benchmark'], alpha=0.7),
                   fontsize=10, color='white')
        
        plt.tight_layout()
        return fig
    
    def create_risk_return_scatter(self, portfolio_returns: pd.Series, 
                                  benchmark_returns: pd.Series,
                                  portfolio_name: str = "Portfolio",
                                  benchmark_name: str = "Benchmark") -> Figure:
        """
        Create risk-return scatter plot
        
        Args:
            portfolio_returns: Portfolio daily returns
            benchmark_returns: Benchmark daily returns
            portfolio_name: Name for portfolio
            benchmark_name: Name for benchmark
            
        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Calculate metrics
        portfolio_vol = portfolio_returns.std() * np.sqrt(252)
        portfolio_return = portfolio_returns.mean() * 252
        benchmark_vol = benchmark_returns.std() * np.sqrt(252)
        benchmark_return = benchmark_returns.mean() * 252
        
        # Create scatter plot
        ax.scatter(portfolio_vol, portfolio_return, 
                  s=200, color=self.colors['portfolio'], 
                  label=portfolio_name, alpha=0.8, edgecolors='black')
        ax.scatter(benchmark_vol, benchmark_return, 
                  s=200, color=self.colors['benchmark'], 
                  label=benchmark_name, alpha=0.8, edgecolors='black')
        
        # Add labels
        ax.annotate(f'{portfolio_name}\n({portfolio_return:.1%}, {portfolio_vol:.1%})',
                   xy=(portfolio_vol, portfolio_return),
                   xytext=(portfolio_vol + 0.02, portfolio_return + 0.02),
                   fontsize=10, ha='left',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        ax.annotate(f'{benchmark_name}\n({benchmark_return:.1%}, {benchmark_vol:.1%})',
                   xy=(benchmark_vol, benchmark_return),
                   xytext=(benchmark_vol + 0.02, benchmark_return - 0.02),
                   fontsize=10, ha='left',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        # Formatting
        ax.set_title('Risk-Return Analysis', fontsize=14, fontweight='bold')
        ax.set_xlabel('Annualized Volatility', fontsize=12)
        ax.set_ylabel('Annualized Return', fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        
        # Add efficient frontier line (simplified)
        x_range = np.linspace(0, max(portfolio_vol, benchmark_vol) * 1.5, 100)
        y_range = np.linspace(0, max(portfolio_return, benchmark_return) * 1.5, 100)
        ax.plot(x_range, y_range, '--', color='gray', alpha=0.5, label='Efficient Frontier')
        
        plt.tight_layout()
        return fig
    
    def create_rolling_metrics_chart(self, portfolio_returns: pd.Series, 
                                    benchmark_returns: pd.Series,
                                    window: int = 60) -> Figure:
        """
        Create rolling metrics chart (rolling beta, correlation)
        
        Args:
            portfolio_returns: Portfolio daily returns
            benchmark_returns: Benchmark daily returns
            window: Rolling window size (default 60 days)
            
        Returns:
            matplotlib Figure object
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Calculate rolling metrics
        rolling_beta = []
        rolling_correlation = []
        dates = []
        
        for i in range(window, len(portfolio_returns)):
            window_portfolio = portfolio_returns.iloc[i-window:i]
            window_benchmark = benchmark_returns.iloc[i-window:i]
            
            # Rolling beta
            covariance = np.cov(window_portfolio, window_benchmark)[0, 1]
            variance = np.var(window_benchmark)
            beta = covariance / variance if variance != 0 else 0
            rolling_beta.append(beta)
            
            # Rolling correlation
            correlation = window_portfolio.corr(window_benchmark)
            rolling_correlation.append(correlation)
            
            dates.append(portfolio_returns.index[i])
        
        # Plot rolling beta
        ax1.plot(dates, rolling_beta, color=self.colors['portfolio'], linewidth=2)
        ax1.axhline(y=1, color='gray', linestyle='--', alpha=0.7, label='Beta = 1')
        ax1.set_title('Rolling Beta (60-day window)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Beta', fontsize=10)
        ax1.legend()
        ax1.grid(True, alpha=0.3, color=self.colors['grid'])
        
        # Plot rolling correlation
        ax2.plot(dates, rolling_correlation, color=self.colors['benchmark'], linewidth=2)
        ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
        ax2.set_title('Rolling Correlation (60-day window)', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=10)
        ax2.set_ylabel('Correlation', fontsize=10)
        ax2.grid(True, alpha=0.3, color=self.colors['grid'])
        
        # Format x-axis
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        return fig
    
    def create_metrics_summary_table(self, results: Dict) -> Figure:
        """
        Create a summary table of key metrics
        
        Args:
            results: Dictionary with analysis results
            
        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('tight')
        ax.axis('off')
        
        # Prepare data for table
        metrics_data = [
            ['Metric', 'Value', 'Status'],
            ['Total Return (Portfolio)', f"{results.get('portfolio_total_return', 0):.2f}%", self._get_status(results.get('portfolio_total_return', 0), 'return')],
            ['Total Return (Benchmark)', f"{results.get('benchmark_total_return', 0):.2f}%", ''],
            ['Excess Return', f"{results.get('excess_return', 0):.2f}%", self._get_status(results.get('excess_return', 0), 'excess')],
            ['Alpha', f"{results.get('alpha', 0):.2f}%", self._get_status(results.get('alpha', 0), 'alpha')],
            ['Beta', f"{results.get('beta', 0):.2f}", self._get_status(results.get('beta', 0), 'beta')],
            ['Sharpe Ratio', f"{results.get('portfolio_sharpe_ratio', 0):.2f}", self._get_status(results.get('portfolio_sharpe_ratio', 0), 'sharpe')],
            ['Information Ratio', f"{results.get('information_ratio', 0):.2f}", self._get_status(results.get('information_ratio', 0), 'info')],
            ['Tracking Error', f"{results.get('tracking_error', 0):.2f}%", self._get_status(results.get('tracking_error', 0), 'tracking')],
            ['Correlation', f"{results.get('correlation', 0):.2f}", self._get_status(results.get('correlation', 0), 'correlation')],
            ['Max Drawdown', f"{results.get('max_drawdown', 0):.2f}%", self._get_status(results.get('max_drawdown', 0), 'drawdown')],
            ['VaR (95%)', f"{results.get('var_95', 0):.2f}%", ''],
        ]
        
        # Create table
        table = ax.table(cellText=metrics_data[1:], colLabels=metrics_data[0],
                        cellLoc='center', loc='center')
        
        # Style the table
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        # Color code the status column
        for i in range(1, len(metrics_data)):
            status = metrics_data[i][2]
            if status == 'GOOD':
                table[(i, 2)].set_facecolor('#90EE90')  # Light green
            elif status == 'POOR':
                table[(i, 2)].set_facecolor('#FFB6C1')  # Light red
            elif status == 'MEDIUM':
                table[(i, 2)].set_facecolor('#FFE4B5')  # Light orange
        
        # Header styling
        for j in range(3):
            table[(0, j)].set_facecolor('#4CAF50')
            table[(0, j)].set_text_props(weight='bold', color='white')
        
        ax.set_title('Portfolio Analysis Summary', fontsize=16, fontweight='bold', pad=20)
        
        return fig
    
    def _get_status(self, value: float, metric_type: str) -> str:
        """Determine status for a metric value"""
        if metric_type == 'return':
            return 'GOOD' if value > 0 else 'POOR'
        elif metric_type == 'excess':
            return 'GOOD' if value > 0 else 'POOR'
        elif metric_type == 'alpha':
            return 'GOOD' if value > 0 else 'POOR'
        elif metric_type == 'beta':
            if 0.8 <= value <= 1.2:
                return 'GOOD'
            elif 0.6 <= value <= 1.4:
                return 'MEDIUM'
            else:
                return 'POOR'
        elif metric_type == 'sharpe':
            if value > 1.0:
                return 'GOOD'
            elif value > 0.5:
                return 'MEDIUM'
            else:
                return 'POOR'
        elif metric_type == 'info':
            if value > 0.5:
                return 'GOOD'
            elif value > 0.2:
                return 'MEDIUM'
            else:
                return 'POOR'
        elif metric_type == 'tracking':
            if value < 2.0:
                return 'GOOD'
            elif value < 5.0:
                return 'MEDIUM'
            else:
                return 'POOR'
        elif metric_type == 'correlation':
            if value > 0.8:
                return 'GOOD'
            elif value > 0.6:
                return 'MEDIUM'
            else:
                return 'POOR'
        elif metric_type == 'drawdown':
            return 'GOOD' if abs(value) < 10 else 'POOR'
        else:
            return ''
    
    def save_chart(self, fig: Figure, filename: str, dpi: int = 300):
        """Save chart to file"""
        fig.savefig(filename, dpi=dpi, bbox_inches='tight')
        print(f"Chart saved as {filename}")
    
    def embed_chart_in_tkinter(self, fig: Figure, parent_frame: tk.Frame) -> FigureCanvasTkAgg:
        """Embed matplotlib chart in tkinter frame"""
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        return canvas 