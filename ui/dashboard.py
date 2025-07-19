"""
Dashboard UI Module
Main window interface for the benchmark analytics application
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from typing import Optional, Dict
import os

from core.data_service import YahooFinanceService, safe_data_fetch
from core.analyzer import PortfolioAnalyzer
from core.chart_maker import ChartMaker

class BenchmarkDashboard:
    """Main dashboard window for benchmark analytics"""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the dashboard
        
        Args:
            root: Main tkinter window
        """
        self.root = root
        self.root.title("Benchmark Analytics Engine")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize services
        self.data_service = YahooFinanceService()
        self.analyzer = PortfolioAnalyzer()
        self.chart_maker = ChartMaker()
        
        # Store current results
        self.current_results = {}
        self.current_charts = {}
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Benchmark Analytics Engine", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Input section
        self.create_input_section(main_frame)
        
        # Results section
        self.create_results_section(main_frame)
        
        # Charts section
        self.create_charts_section(main_frame)
        
    def create_input_section(self, parent):
        """Create the input controls section"""
        input_frame = ttk.LabelFrame(parent, text="Portfolio Input", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Portfolio symbols input
        ttk.Label(input_frame, text="Portfolio Symbols (comma-separated):").pack(anchor=tk.W)
        self.portfolio_entry = ttk.Entry(input_frame, width=60, font=('Arial', 10))
        self.portfolio_entry.pack(fill=tk.X, pady=(5, 10))
        self.portfolio_entry.insert(0, "AAPL,MSFT,GOOGL,AMZN,META")
        
        # Sample portfolios dropdown
        sample_frame = ttk.Frame(input_frame)
        sample_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(sample_frame, text="Sample Portfolios:").pack(side=tk.LEFT)
        self.sample_var = tk.StringVar()
        sample_combo = ttk.Combobox(sample_frame, textvariable=self.sample_var, 
                                   state="readonly", width=20)
        sample_combo['values'] = [
            "Tech Growth (AAPL,MSFT,GOOGL,AMZN,META)",
            "Value Stocks (BRK-B,JNJ,PG,KO,WMT)",
            "Dividend Aristocrats (JNJ,PG,KO,WMT,HD)",
            "Financial (JPM,BAC,WFC,GS,MS)",
            "Healthcare (JNJ,PFE,UNH,ABBV,TMO)"
        ]
        sample_combo.pack(side=tk.LEFT, padx=(10, 0))
        sample_combo.bind('<<ComboboxSelected>>', self.on_sample_selected)
        
        # Benchmark and period selection
        selection_frame = ttk.Frame(input_frame)
        selection_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Benchmark dropdown
        ttk.Label(selection_frame, text="Benchmark:").pack(side=tk.LEFT)
        self.benchmark_var = tk.StringVar(value="S&P 500")
        benchmark_combo = ttk.Combobox(selection_frame, textvariable=self.benchmark_var,
                                      values=self.data_service.get_available_benchmarks(),
                                      state="readonly", width=15)
        benchmark_combo.pack(side=tk.LEFT, padx=(10, 20))
        
        # Period dropdown
        ttk.Label(selection_frame, text="Period:").pack(side=tk.LEFT)
        self.period_var = tk.StringVar(value="1 Year")
        period_combo = ttk.Combobox(selection_frame, textvariable=self.period_var,
                                   values=self.data_service.get_available_periods(),
                                   state="readonly", width=10)
        period_combo.pack(side=tk.LEFT, padx=(10, 20))
        
        # Analyze button
        self.analyze_button = ttk.Button(selection_frame, text="Analyze Portfolio", 
                                        command=self.analyze_portfolio)
        self.analyze_button.pack(side=tk.LEFT, padx=(20, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(input_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(10, 0))
        
    def create_results_section(self, parent):
        """Create the results display section"""
        results_frame = ttk.LabelFrame(parent, text="Analysis Results", padding=10)
        results_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create notebook for tabs
        self.results_notebook = ttk.Notebook(results_frame)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Summary tab
        self.summary_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.summary_frame, text="Summary")
        
        # Metrics tab
        self.metrics_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.metrics_frame, text="Detailed Metrics")
        
        # Risk tab
        self.risk_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.risk_frame, text="Risk Analysis")
        
        # Export buttons
        export_frame = ttk.Frame(results_frame)
        export_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(export_frame, text="Save Charts", 
                  command=self.save_charts).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(export_frame, text="Export Data", 
                  command=self.export_data).pack(side=tk.LEFT)
        
    def create_charts_section(self, parent):
        """Create the charts display section"""
        charts_frame = ttk.LabelFrame(parent, text="Charts", padding=10)
        charts_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for chart tabs
        self.charts_notebook = ttk.Notebook(charts_frame)
        self.charts_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Performance chart tab
        self.performance_frame = ttk.Frame(self.charts_notebook)
        self.charts_notebook.add(self.performance_frame, text="Performance")
        
        # Risk-Return chart tab
        self.risk_return_frame = ttk.Frame(self.charts_notebook)
        self.charts_notebook.add(self.risk_return_frame, text="Risk-Return")
        
        # Rolling metrics tab
        self.rolling_frame = ttk.Frame(self.charts_notebook)
        self.charts_notebook.add(self.rolling_frame, text="Rolling Metrics")
        
    def on_sample_selected(self, event):
        """Handle sample portfolio selection"""
        selected = self.sample_var.get()
        if selected:
            # Extract symbols from the selected option
            symbols = selected.split('(')[1].split(')')[0]
            self.portfolio_entry.delete(0, tk.END)
            self.portfolio_entry.insert(0, symbols)
    
    def analyze_portfolio(self):
        """Main analysis function"""
        # Get input values
        portfolio_text = self.portfolio_entry.get().strip()
        benchmark = self.benchmark_var.get()
        period = self.period_var.get()
        
        # Validate input
        if not portfolio_text:
            messagebox.showerror("Error", "Please enter portfolio symbols")
            return
        
        # Parse portfolio symbols
        symbols = [s.strip() for s in portfolio_text.split(',') if s.strip()]
        if not symbols:
            messagebox.showerror("Error", "Please enter valid portfolio symbols")
            return
        
        # Start analysis
        self.analyze_button.config(state='disabled')
        self.progress.start()
        
        # Run analysis in a separate thread to avoid blocking UI
        self.root.after(100, lambda: self.run_analysis(symbols, benchmark, period))
    
    def run_analysis(self, symbols, benchmark, period):
        """Run the actual analysis"""
        try:
            # Fetch data
            portfolio_data, benchmark_data = safe_data_fetch(symbols, benchmark, period)
            
            if portfolio_data is None or benchmark_data is None:
                messagebox.showerror("Error", "Failed to fetch data. Please check your symbols and try again.")
                return
            
            # Run analysis
            results = self.analyzer.analyze_portfolio_vs_benchmark(
                portfolio_data, benchmark_data,
                portfolio_name="Portfolio",
                benchmark_name=benchmark
            )
            
            if not results:
                messagebox.showerror("Error", "Analysis failed. Please check your data and try again.")
                return
            
            # Store results
            self.current_results = results
            
            # Update UI
            self.update_results_display()
            self.create_charts()
            
            messagebox.showinfo("Success", "Analysis completed successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
        
        finally:
            # Reset UI
            self.analyze_button.config(state='normal')
            self.progress.stop()
    
    def update_results_display(self):
        """Update the results display with current analysis"""
        if not self.current_results:
            return
        
        # Format results
        formatted_results = self.analyzer.format_results(self.current_results)
        
        # Clear previous content
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        
        # Create summary display
        self.create_summary_display(formatted_results)
        
        # Create detailed metrics display
        self.create_metrics_display(formatted_results)
        
        # Create risk analysis display
        self.create_risk_display(formatted_results)
    
    def create_summary_display(self, results):
        """Create summary display"""
        # Key metrics frame
        metrics_frame = ttk.Frame(self.summary_frame)
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title = ttk.Label(metrics_frame, text="Portfolio Analysis Summary", 
                         font=('Arial', 14, 'bold'))
        title.pack(pady=(0, 20))
        
        # Key metrics using pack instead of grid
        key_metrics = [
            ("Total Return (Portfolio)", f"{results.get('portfolio_total_return', 0):.2f}%"),
            ("Total Return (Benchmark)", f"{results.get('benchmark_total_return', 0):.2f}%"),
            ("Excess Return", f"{results.get('excess_return', 0):.2f}%"),
            ("Alpha", f"{results.get('alpha', 0):.2f}%"),
            ("Beta", f"{results.get('beta', 0):.2f}"),
            ("Sharpe Ratio", f"{results.get('portfolio_sharpe_ratio', 0):.2f}"),
            ("Information Ratio", f"{results.get('information_ratio', 0):.2f}"),
            ("Correlation", f"{results.get('correlation', 0):.2f}")
        ]
        
        # Create two columns using frames
        left_column = ttk.Frame(metrics_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_column = ttk.Frame(metrics_frame)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Distribute metrics between columns
        for i, (label, value) in enumerate(key_metrics):
            if i % 2 == 0:  # Left column
                parent = left_column
            else:  # Right column
                parent = right_column
            
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=label, font=('Arial', 10, 'bold')).pack(anchor=tk.W)
            ttk.Label(frame, text=value, font=('Arial', 12)).pack(anchor=tk.W)
    
    def create_metrics_display(self, results):
        """Create detailed metrics display"""
        # Clear previous content
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()
        
        # Create text widget for detailed metrics
        text_widget = tk.Text(self.metrics_frame, wrap=tk.WORD, font=('Courier', 10))
        scrollbar = ttk.Scrollbar(self.metrics_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add detailed metrics
        text_widget.insert(tk.END, "DETAILED PORTFOLIO METRICS\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")
        
        detailed_metrics = [
            ("Analysis Period", f"{results.get('start_date', 'N/A')} to {results.get('end_date', 'N/A')}"),
            ("Data Points", f"{results.get('data_points', 0)}"),
            ("Portfolio Total Return", f"{results.get('portfolio_total_return', 0):.2f}%"),
            ("Benchmark Total Return", f"{results.get('benchmark_total_return', 0):.2f}%"),
            ("Excess Return", f"{results.get('excess_return', 0):.2f}%"),
            ("Alpha", f"{results.get('alpha', 0):.2f}%"),
            ("Beta", f"{results.get('beta', 0):.2f}"),
            ("Correlation", f"{results.get('correlation', 0):.2f}"),
            ("R-Squared", f"{results.get('r_squared', 0):.2f}"),
            ("Tracking Error", f"{results.get('tracking_error', 0):.2f}%"),
            ("Information Ratio", f"{results.get('information_ratio', 0):.2f}"),
            ("Portfolio Volatility", f"{results.get('portfolio_volatility', 0):.2f}%"),
            ("Benchmark Volatility", f"{results.get('benchmark_volatility', 0):.2f}%"),
            ("Portfolio Sharpe Ratio", f"{results.get('portfolio_sharpe_ratio', 0):.2f}"),
            ("Benchmark Sharpe Ratio", f"{results.get('benchmark_sharpe_ratio', 0):.2f}"),
            ("Up Capture", f"{results.get('up_capture', 0):.2f}"),
            ("Down Capture", f"{results.get('down_capture', 0):.2f}"),
            ("Calmar Ratio", f"{results.get('calmar_ratio', 0):.2f}")
        ]
        
        for label, value in detailed_metrics:
            text_widget.insert(tk.END, f"{label:<25}: {value}\n")
        
        text_widget.config(state=tk.DISABLED)
    
    def create_risk_display(self, results):
        """Create risk analysis display"""
        # Clear previous content
        for widget in self.risk_frame.winfo_children():
            widget.destroy()
        
        # Create risk metrics display
        risk_frame = ttk.Frame(self.risk_frame)
        risk_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(risk_frame, text="Risk Analysis", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        risk_metrics = [
            ("Maximum Drawdown", f"{results.get('max_drawdown', 0):.2f}%"),
            ("Value at Risk (95%)", f"{results.get('var_95', 0):.2f}%"),
            ("Value at Risk (99%)", f"{results.get('var_99', 0):.2f}%"),
            ("Portfolio Volatility", f"{results.get('portfolio_volatility', 0):.2f}%"),
            ("Tracking Error", f"{results.get('tracking_error', 0):.2f}%")
        ]
        
        for label, value in risk_metrics:
            frame = ttk.Frame(risk_frame)
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=label, font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
            ttk.Label(frame, text=value, font=('Arial', 12)).pack(side=tk.RIGHT)
    
    def create_charts(self):
        """Create and display charts"""
        if not self.current_results:
            return
        
        try:
            # Performance chart
            perf_fig = self.chart_maker.create_performance_chart(
                self.current_results['cumulative_returns'],
                "Portfolio",
                self.benchmark_var.get()
            )
            self.display_chart(perf_fig, self.performance_frame)
            
            # Risk-return chart
            risk_fig = self.chart_maker.create_risk_return_scatter(
                self.current_results['portfolio_returns'],
                self.current_results['benchmark_returns'],
                "Portfolio",
                self.benchmark_var.get()
            )
            self.display_chart(risk_fig, self.risk_return_frame)
            
            # Rolling metrics chart
            rolling_fig = self.chart_maker.create_rolling_metrics_chart(
                self.current_results['portfolio_returns'],
                self.current_results['benchmark_returns']
            )
            self.display_chart(rolling_fig, self.rolling_frame)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create charts: {str(e)}")
    
    def display_chart(self, fig, parent_frame):
        """Display a chart in the given frame"""
        # Clear previous content
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        # Create canvas and display chart
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def save_charts(self):
        """Save current charts to files"""
        if not self.current_results:
            messagebox.showwarning("Warning", "No analysis results to save")
            return
        
        # Ask for directory
        directory = filedialog.askdirectory(title="Select directory to save charts")
        if not directory:
            return
        
        try:
            # Create charts and save them
            perf_fig = self.chart_maker.create_performance_chart(
                self.current_results['cumulative_returns'],
                "Portfolio",
                self.benchmark_var.get()
            )
            self.chart_maker.save_chart(perf_fig, os.path.join(directory, "performance_chart.png"))
            
            risk_fig = self.chart_maker.create_risk_return_scatter(
                self.current_results['portfolio_returns'],
                self.current_results['benchmark_returns'],
                "Portfolio",
                self.benchmark_var.get()
            )
            self.chart_maker.save_chart(risk_fig, os.path.join(directory, "risk_return_chart.png"))
            
            # Summary table
            summary_fig = self.chart_maker.create_metrics_summary_table(self.current_results)
            self.chart_maker.save_chart(summary_fig, os.path.join(directory, "summary_table.png"))
            
            messagebox.showinfo("Success", f"Charts saved to {directory}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save charts: {str(e)}")
    
    def export_data(self):
        """Export analysis results to CSV"""
        if not self.current_results:
            messagebox.showwarning("Warning", "No analysis results to export")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save analysis results",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Create DataFrame for export
                export_data = {
                    'Metric': [],
                    'Value': [],
                    'Description': []
                }
                
                # Add key metrics
                metrics_info = [
                    ('portfolio_total_return', 'Portfolio Total Return (%)', 'Total return of the portfolio'),
                    ('benchmark_total_return', 'Benchmark Total Return (%)', 'Total return of the benchmark'),
                    ('excess_return', 'Excess Return (%)', 'Portfolio return minus benchmark return'),
                    ('alpha', 'Alpha (%)', 'Jensen\'s Alpha - excess return adjusted for risk'),
                    ('beta', 'Beta', 'Portfolio sensitivity to market movements'),
                    ('sharpe_ratio', 'Sharpe Ratio', 'Risk-adjusted return measure'),
                    ('information_ratio', 'Information Ratio', 'Excess return per unit of tracking error'),
                    ('correlation', 'Correlation', 'Correlation with benchmark'),
                    ('tracking_error', 'Tracking Error (%)', 'Standard deviation of excess returns'),
                    ('max_drawdown', 'Maximum Drawdown (%)', 'Largest peak-to-trough decline')
                ]
                
                for metric, label, description in metrics_info:
                    value = self.current_results.get(metric, 0)
                    if 'return' in metric or 'alpha' in metric or 'drawdown' in metric or 'error' in metric:
                        value = f"{value * 100:.2f}%" if isinstance(value, (int, float)) else str(value)
                    else:
                        value = f"{value:.4f}" if isinstance(value, (int, float)) else str(value)
                    
                    export_data['Metric'].append(label)
                    export_data['Value'].append(value)
                    export_data['Description'].append(description)
                
                # Save to CSV
                df = pd.DataFrame(export_data)
                df.to_csv(filename, index=False)
                
                messagebox.showinfo("Success", f"Data exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {str(e)}") 