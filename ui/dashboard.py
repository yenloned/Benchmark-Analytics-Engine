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
        
        # Set minimum window size and make it resizable
        self.root.minsize(1200, 700)
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
        """Setup the main user interface with scrollable content"""
        # Create main scrollable frame
        self.main_canvas = tk.Canvas(self.root, bg='#f0f0f0')
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)
        
        # Configure the scrollable frame
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        # Create window in canvas with padding
        self.main_canvas.create_window((10, 10), window=self.scrollable_frame, anchor="nw", width=1380)
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas and scrollbar
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to scroll
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.main_canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.main_canvas.bind_all("<Button-5>", self._on_mousewheel)
        
        # Title
        title_label = ttk.Label(self.scrollable_frame, text="Benchmark Analytics Engine", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(10, 20))
        
        # Scroll indicator
        scroll_indicator = ttk.Label(self.scrollable_frame, 
                                   text="💡 Tip: Use mouse wheel or scrollbar to navigate through all content", 
                                   font=('Arial', 9), foreground='gray')
        scroll_indicator.pack(pady=(0, 10))
        
        # Input section
        self.create_input_section(self.scrollable_frame)
        
        # Results section
        self.create_results_section(self.scrollable_frame)
        
        # Charts section
        self.create_charts_section(self.scrollable_frame)
        
        # Configure canvas to expand with window
        self.root.bind('<Configure>', self._on_window_configure)
        
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        # Handle different platforms
        if event.delta:
            # Windows
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        else:
            # Linux/Mac
            if event.num == 4:
                self.main_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.main_canvas.yview_scroll(1, "units")
    
    def _on_window_configure(self, event):
        """Handle window resize to update canvas width"""
        # Only handle main window resize events
        if event.widget == self.root:
            # Update canvas width to match window width
            canvas_width = event.width - 20  # Account for scrollbar
            if canvas_width > 0:
                self.main_canvas.configure(width=canvas_width)
        
    def create_input_section(self, parent):
        """Create the input controls section"""
        input_frame = ttk.LabelFrame(parent, text="Portfolio Configuration", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Step 1: Portfolio symbols input
        symbols_frame = ttk.LabelFrame(input_frame, text="Step 1: Enter Your Portfolio Symbols", padding=5)
        symbols_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(symbols_frame, text="Stock Symbols (comma-separated):", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.portfolio_entry = ttk.Entry(symbols_frame, width=60, font=('Arial', 10))
        self.portfolio_entry.pack(fill=tk.X, pady=(5, 5))
        self.portfolio_entry.insert(0, "AAPL,MSFT,GOOGL,AMZN,META")
        self.portfolio_entry.bind('<KeyRelease>', self.on_portfolio_change)
        
        # Quick portfolio options
        quick_frame = ttk.Frame(symbols_frame)
        quick_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(quick_frame, text="Quick Options:").pack(side=tk.LEFT)
        self.sample_var = tk.StringVar()
        sample_combo = ttk.Combobox(quick_frame, textvariable=self.sample_var, 
                                   state="readonly", width=25)
        sample_combo['values'] = [
            "Tech Growth (AAPL,MSFT,GOOGL,AMZN,META)",
            "Value Stocks (BRK-B,JNJ,PG,KO,WMT)",
            "Dividend Aristocrats (JNJ,PG,KO,WMT,HD)",
            "Financial (JPM,BAC,WFC,GS,MS)",
            "Healthcare (JNJ,PFE,UNH,ABBV,TMO)"
        ]
        sample_combo.pack(side=tk.LEFT, padx=(10, 0))
        sample_combo.bind('<<ComboboxSelected>>', self.on_sample_selected)
        
        # Step 2: Portfolio weights section
        weights_frame = ttk.LabelFrame(input_frame, text="Step 2: Configure Portfolio Weights (Optional)", padding=5)
        weights_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Weight instructions
        ttk.Label(weights_frame, text="Customize how much of your portfolio goes to each stock:", 
                 font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 5))
        ttk.Label(weights_frame, text="• Leave empty for equal weighting", 
                 font=('Arial', 8), foreground='gray').pack(anchor=tk.W)
        ttk.Label(weights_frame, text="• Weights should sum to 100%", 
                 font=('Arial', 8), foreground='gray').pack(anchor=tk.W)
        
        # Weights input frame
        self.weights_frame = ttk.Frame(weights_frame)
        self.weights_frame.pack(fill=tk.X, pady=(5, 5))
        
        # Weight validation label
        self.weight_validation_label = ttk.Label(weights_frame, text="", foreground="green")
        self.weight_validation_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Weight distribution options
        weight_options_frame = ttk.Frame(weights_frame)
        weight_options_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(weight_options_frame, text="Set Equal Weights", 
                  command=self.set_equal_weights).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(weight_options_frame, text="Clear All Weights", 
                  command=self.clear_weights).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(weight_options_frame, text="Refresh Weights", 
                  command=self.create_weight_inputs).pack(side=tk.LEFT)
        
        # Step 3: Analysis settings
        settings_frame = ttk.LabelFrame(input_frame, text="Step 3: Analysis Settings", padding=5)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Benchmark and period selection
        selection_frame = ttk.Frame(settings_frame)
        selection_frame.pack(fill=tk.X)
        
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
        
        # Initialize weights
        self.portfolio_weights = {}
        self.weight_entries = {}
        self.create_weight_inputs()
        
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
        
        # Risk-return chart tab
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
            # Clear the sample selection to allow manual editing
            self.sample_var.set('')
            # Recreate weight inputs for new symbols
            self.create_weight_inputs()
    
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
            
            # Get portfolio weights
            weights = self.get_portfolio_weights()
            
            # Run analysis
            results = self.analyzer.analyze_portfolio_vs_benchmark(
                portfolio_data, benchmark_data,
                portfolio_name="Portfolio",
                benchmark_name=benchmark,
                weights=weights
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
        title.pack(pady=(0, 10))
        
        # Portfolio weights display
        if 'weights_used' in results and results['weights_used'] != 'equal-weighted':
            weights_frame = ttk.LabelFrame(metrics_frame, text="Portfolio Weights", padding=5)
            weights_frame.pack(fill=tk.X, pady=(0, 10))
            
            weights_text = "Custom Weights: "
            for symbol, weight in results['weights_used'].items():
                weights_text += f"{symbol} ({weight*100:.1f}%) "
            
            ttk.Label(weights_frame, text=weights_text, font=('Arial', 10)).pack(anchor=tk.W)
        elif 'weights_used' in results:
            weights_frame = ttk.LabelFrame(metrics_frame, text="Portfolio Weights", padding=5)
            weights_frame.pack(fill=tk.X, pady=(0, 10))
            ttk.Label(weights_frame, text="Equal-Weighted Portfolio", font=('Arial', 10)).pack(anchor=tk.W)
        
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

    def on_portfolio_change(self, event=None):
        """Handle portfolio symbols change"""
        # Debounce the input to avoid too many updates
        if hasattr(self, '_portfolio_change_timer'):
            self.root.after_cancel(self._portfolio_change_timer)
        
        self._portfolio_change_timer = self.root.after(500, self.refresh_weight_inputs)
    
    def refresh_weight_inputs(self):
        """Refresh weight inputs and reset weights for new portfolio"""
        # Clear sample selection when user manually edits
        if self.sample_var.get():
            self.sample_var.set('')
        
        # Recreate weight inputs (this will reset weights)
        self.create_weight_inputs()
    
    def create_weight_inputs(self):
        """Create weight input fields for portfolio symbols"""
        # Clear existing weight inputs
        for widget in self.weights_frame.winfo_children():
            widget.destroy()
        
        # Get current symbols
        symbols = [s.strip() for s in self.portfolio_entry.get().split(',') if s.strip()]
        
        if not symbols:
            # Show message when no symbols
            ttk.Label(self.weights_frame, text="Enter portfolio symbols above to configure weights", 
                     font=('Arial', 9), foreground='gray').pack(pady=10)
            # Reset weights when no symbols
            self.portfolio_weights = {}
            self.update_weight_validation()
            return
        
        # Reset weights for new portfolio
        self.portfolio_weights = {}
        
        # Create weight inputs
        self.weight_entries = {}
        
        # Create a scrollable frame for many stocks
        if len(symbols) > 8:
            # Create canvas and scrollbar for many stocks
            canvas = tk.Canvas(self.weights_frame, height=120)
            scrollbar = ttk.Scrollbar(self.weights_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Create weight inputs in scrollable frame
            for i, symbol in enumerate(symbols):
                symbol_frame = ttk.Frame(scrollable_frame)
                symbol_frame.pack(fill=tk.X, pady=2)
                
                # Symbol label
                ttk.Label(symbol_frame, text=f"{symbol}:", width=10).pack(side=tk.LEFT)
                
                # Weight entry
                weight_entry = ttk.Entry(symbol_frame, width=8)
                weight_entry.pack(side=tk.LEFT, padx=(5, 0))
                weight_entry.bind('<KeyRelease>', self.on_weight_change)
                
                # Percentage label
                ttk.Label(symbol_frame, text="%").pack(side=tk.LEFT, padx=(2, 0))
                
                # Store reference
                self.weight_entries[symbol] = weight_entry
                
                # Set default equal weight
                equal_weight = 100.0 / len(symbols)
                self.portfolio_weights[symbol] = equal_weight
                weight_entry.insert(0, f"{equal_weight:.1f}")
            
            # Pack canvas and scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
        else:
            # Simple layout for fewer stocks
            for i, symbol in enumerate(symbols):
                symbol_frame = ttk.Frame(self.weights_frame)
                symbol_frame.pack(fill=tk.X, pady=2)
                
                # Symbol label
                ttk.Label(symbol_frame, text=f"{symbol}:", width=10).pack(side=tk.LEFT)
                
                # Weight entry
                weight_entry = ttk.Entry(symbol_frame, width=8)
                weight_entry.pack(side=tk.LEFT, padx=(5, 0))
                weight_entry.bind('<KeyRelease>', self.on_weight_change)
                
                # Percentage label
                ttk.Label(symbol_frame, text="%").pack(side=tk.LEFT, padx=(2, 0))
                
                # Store reference
                self.weight_entries[symbol] = weight_entry
                
                # Set default equal weight
                equal_weight = 100.0 / len(symbols)
                self.portfolio_weights[symbol] = equal_weight
                weight_entry.insert(0, f"{equal_weight:.1f}")
        
        self.update_weight_validation()
    
    def on_weight_change(self, event=None):
        """Handle weight input changes"""
        try:
            total_weight = 0
            for symbol, entry in self.weight_entries.items():
                try:
                    weight = float(entry.get() or 0)
                    self.portfolio_weights[symbol] = weight
                    total_weight += weight
                except ValueError:
                    self.portfolio_weights[symbol] = 0
            
            self.update_weight_validation()
            
        except Exception as e:
            print(f"Error updating weights: {e}")
    
    def update_weight_validation(self):
        """Update weight validation display"""
        try:
            # Get current symbols to validate against
            current_symbols = [s.strip() for s in self.portfolio_entry.get().split(',') if s.strip()]
            
            # Only validate if we have symbols and weights
            if not current_symbols or not self.portfolio_weights:
                self.weight_validation_label.config(text="", foreground="green")
                return
            
            # Calculate total weight for current symbols only
            total_weight = 0
            for symbol in current_symbols:
                if symbol in self.portfolio_weights:
                    total_weight += self.portfolio_weights[symbol]
            
            if abs(total_weight - 100.0) < 0.1:  # Allow small rounding errors
                self.weight_validation_label.config(
                    text=f"✓ Total: {total_weight:.1f}% (Valid)", 
                    foreground="green"
                )
            elif total_weight == 0:
                self.weight_validation_label.config(
                    text="No weights set (will use equal weighting)", 
                    foreground="blue"
                )
            else:
                self.weight_validation_label.config(
                    text=f"⚠ Total: {total_weight:.1f}% (Should equal 100%)", 
                    foreground="red"
                )
                
        except Exception as e:
            self.weight_validation_label.config(
                text="Error calculating weights", 
                foreground="red"
            )
    
    def set_equal_weights(self):
        """Set equal weights for all symbols"""
        symbols = [s.strip() for s in self.portfolio_entry.get().split(',') if s.strip()]
        if symbols:
            equal_weight = 100.0 / len(symbols)
            for symbol in symbols:
                self.portfolio_weights[symbol] = equal_weight
                if symbol in self.weight_entries:
                    self.weight_entries[symbol].delete(0, tk.END)
                    self.weight_entries[symbol].insert(0, f"{equal_weight:.1f}")
            self.update_weight_validation()
        else:
            messagebox.showwarning("Warning", "Please enter portfolio symbols first")
    
    def set_market_cap_weights(self):
        """Set market cap weights (placeholder - would need market cap data)"""
        messagebox.showinfo("Info", "Market cap weighting would require additional market data. Using equal weights for now.")
        self.set_equal_weights()
    
    def clear_weights(self):
        """Clear all weight inputs"""
        for entry in self.weight_entries.values():
            entry.delete(0, tk.END)
        self.portfolio_weights = {}
        self.update_weight_validation()
        messagebox.showinfo("Info", "Weights cleared. Analysis will use equal weighting.")
    
    def get_portfolio_weights(self):
        """Get current portfolio weights as a dictionary"""
        weights = {}
        total_weight = sum(self.portfolio_weights.values())
        
        if abs(total_weight - 100.0) < 0.1 and total_weight > 0:  # Valid weights
            # Normalize to ensure they sum to 100%
            for symbol, weight in self.portfolio_weights.items():
                weights[symbol] = weight / 100.0
        else:
            # Use equal weights if invalid or no weights set
            symbols = [s.strip() for s in self.portfolio_entry.get().split(',') if s.strip()]
            if symbols:
                equal_weight = 1.0 / len(symbols)
                for symbol in symbols:
                    weights[symbol] = equal_weight
        
        return weights 