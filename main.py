"""
Benchmark Analytics Engine
Main entry point for the application
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.dashboard import BenchmarkDashboard

def main():
    """Main application entry point"""
    try:
        # Create main window
        root = tk.Tk()
        
        # Create and run dashboard
        app = BenchmarkDashboard(root)
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application: {str(e)}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 