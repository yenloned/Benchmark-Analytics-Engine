# Benchmark Analytics Engine

A comprehensive desktop application for portfolio analysis and benchmark comparison. This project showcases the ability to build robust financial applications with proper error handling, data processing, and quantitative analysis capabilities.

## 🚀 Features

- **Portfolio Analysis**: Compare custom portfolios against market benchmarks
- **Real-time Data**: Fetch live market data from Yahoo Finance API
- **Comprehensive Metrics**: Calculate 15+ key financial performance indicators
- **Interactive Charts**: Generate professional-grade visualizations
- **Risk Assessment**: Advanced risk metrics including VaR and maximum drawdown
- **Robust Error Handling**: Retry logic, data validation, graceful failure recovery
- **Data Export**: Save analysis results and charts for reporting

## 📊 Financial Metrics Implemented

### Performance Metrics
- **Alpha (Jensen's Alpha)**: Excess return beyond CAPM prediction
- **Beta**: Market sensitivity and systematic risk
- **Sharpe Ratio**: Risk-adjusted return measurement
- **Information Ratio**: Active management skill assessment
- **R-Squared**: Correlation with benchmark

### Risk Metrics
- **Volatility**: Annualized standard deviation of returns
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Value at Risk (VaR)**: Potential loss at confidence levels (95%, 99%)
- **Tracking Error**: Deviation from benchmark performance

### Advanced Analytics
- **Up/Down Capture Ratios**: Asymmetric market performance
- **Calmar Ratio**: Return per unit of maximum risk
- **Rolling Metrics**: Time-varying performance analysis
- **Correlation Analysis**: Portfolio diversification assessment

## 🛠️ Setup and Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

### Dependencies
```
yfinance==0.2.28      # Yahoo Finance API wrapper
pandas==2.1.4         # Data manipulation and analysis
numpy==1.24.3         # Numerical computing
matplotlib==3.8.2     # Data visualization
tkinter-tooltip==2.1.0 # GUI enhancements
```

### Design Patterns
- **Service Layer Pattern**: Separate data, analysis, and UI concerns
- **Factory Pattern**: Chart generation with configurable parameters
- **Observer Pattern**: UI updates based on analysis completion
- **Strategy Pattern**: Different calculation methods for various metrics

## 📈 Financial Calculations

### Returns Calculation
```python
# Daily returns using percentage change
daily_returns = prices.pct_change().dropna()

# Cumulative returns with compounding
cumulative_returns = (1 + daily_returns).cumprod() - 1

# Portfolio returns (equal-weighted)
portfolio_returns = returns.mean(axis=1)
```

### Risk Metrics
```python
# Annualized volatility
volatility = returns.std() * sqrt(252)

# Maximum drawdown
running_max = cumulative_returns.cummax()
drawdown = (cumulative_returns / running_max) - 1
max_drawdown = drawdown.min()

# Value at Risk (95%)
var_95 = returns.quantile(0.05)
```

### Performance Metrics
```python
# Beta calculation
covariance = np.cov(portfolio_returns, market_returns)[0,1]
variance = np.var(market_returns)
beta = covariance / variance

# Sharpe ratio
excess_return = portfolio_return - risk_free_rate
sharpe_ratio = excess_return / portfolio_volatility

# Alpha (Jensen's Alpha)
alpha = portfolio_return - (risk_free_rate + beta * (market_return - risk_free_rate))
```

## 🔧 Technical Implementation

### Data Processing Pipeline
1. **Symbol Validation**: Verify stock symbols with Yahoo Finance API
2. **Data Fetching**: Retrieve historical price data with retry logic
3. **Data Cleaning**: Handle missing values and outliers
4. **Calculation Engine**: Compute financial metrics using pandas/numpy
5. **Visualization**: Generate charts using matplotlib
6. **Results Display**: Present findings in organized UI tabs

### Error Handling Strategy
- **Network Resilience**: 3-attempt retry logic with exponential backoff
- **Data Quality**: Validation of data completeness and consistency
- **Graceful Degradation**: Continue analysis with available data
- **User Feedback**: Clear error messages and recovery suggestions

### Performance Optimizations
- **Efficient Data Structures**: Pandas DataFrames for vectorized operations
- **Memory Management**: Clear old results before loading new data
- **Async Processing**: Non-blocking UI during analysis
- **Caching**: Store fetched data to minimize API calls

## Demo
|![PREVIEW](images/demo_engine.jpg)|
|![PREVIEW](images/performance_chart.png)|
|![PREVIEW](images/risk_return_chart.png)|
|![PREVIEW](images/summary_table.png)|