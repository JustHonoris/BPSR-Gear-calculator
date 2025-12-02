"""
gui_main.py
Main application window with tab management
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

from calculator_v2 import GearCalculator
from gui_config_tab import ConfigTab
from gui_results_tab import ResultsTab
from gui_gear_tab import GearTab
from locked_gear_manager import LockedGearManager


class RPGCalculatorApp:
    """Main application class"""
    
    def __init__(self, root):
        """
        Initialize the application
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("RPG Gear Set Calculator v2.1 - Modular")
        self.root.geometry("1200x850")
        
        # State
        self.calculator = None
        self.calculating = False
        self.locked_gear_manager = LockedGearManager()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main UI"""
        # Configure root grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(0, weight=1)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.config_tab = ConfigTab(self.notebook, self)
        self.gear_tab = GearTab(self.notebook, self)
        self.results_tab = ResultsTab(self.notebook, self)
        
        # Add tabs to notebook
        self.notebook.add(self.config_tab, text="⚙️ Configuration")
        self.notebook.add(self.gear_tab, text="🔒 My Gear")
        self.notebook.add(self.results_tab, text="📊 Results")
    
    def start_calculation(self):
        """Start calculation in background thread"""
        if self.calculating:
            messagebox.showwarning("Warning", "Calculation already in progress")
            return
        
        # Validate configuration
        config_data = self.config_tab.get_config()
        
        if not config_data['class_name']:
            messagebox.showerror("Error", "Please select a class")
            return
        
        if not config_data['subclass_name']:
            messagebox.showerror("Error", "Please select a subclass")
            return
        
        # Check if at least one stat requirement is set
        if not config_data['min_stats']:
            result = messagebox.askyesno("Warning",
                "No minimum stat requirements set. This will find ALL possible combinations. Continue?")
            if not result:
                return
        
        # Start calculation
        self.calculating = True
        self.config_tab.set_calculating(True)
        self.results_tab.status_label.config(text="Searching for solutions...")
        
        # Switch to results tab
        self.notebook.select(self.results_tab)
        
        # Run calculation in thread
        thread = threading.Thread(target=self.run_calculation)
        thread.daemon = True
        thread.start()
    
    def run_calculation(self):
        """Run calculation (called in background thread)"""
        try:
            config_data = self.config_tab.get_config()
            
            # Create calculator with locked gear manager
            self.calculator = GearCalculator(
                class_name=config_data['class_name'],
                subclass_name=config_data['subclass_name'],
                gear_level=config_data['gear_level'],
                weapon_level=config_data['weapon_level'],
                unique_count=config_data['unique_count'],
                gem_assumption=config_data['gem_assumption'],
                min_stats=config_data['min_stats'],
                locked_gear_manager=self.locked_gear_manager  # Pass locked gear manager
            )
            
            # Store reference to locked gear manager in calculator for formatting
            self.calculator.locked_gear_manager = self.locked_gear_manager
            
            # Calculate solutions
            solutions = self.calculator.calculate(max_solutions=config_data['max_solutions'])
            
            # Update UI in main thread
            self.root.after(0, lambda: self.calculation_complete(solutions))
            
        except Exception as e:
            self.root.after(0, lambda: self.calculation_error(str(e)))
    
    def calculation_complete(self, solutions):
        """Handle successful calculation completion"""
        self.calculating = False
        self.config_tab.set_calculating(False)
        self.config_tab.set_progress("Complete", "green")
        
        # Update results tab
        self.results_tab.set_solutions(solutions, self.calculator)
    
    def calculation_error(self, error_msg):
        """Handle calculation error"""
        self.calculating = False
        self.config_tab.set_calculating(False)
        self.config_tab.set_progress("Error", "red")
        self.results_tab.status_label.config(text="Calculation failed")
        
        messagebox.showerror("Calculation Error", f"An error occurred:\n\n{error_msg}")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = RPGCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()