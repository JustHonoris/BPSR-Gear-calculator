"""
gui_config_tab.py
Configuration tab for class, gear level, and stat requirements
"""

import tkinter as tk
from tkinter import ttk
import config
import config_numerical


class ConfigTab(ttk.Frame):
    """Configuration tab for calculator settings"""
    
    def __init__(self, parent, app):
        """
        Initialize configuration tab
        
        Args:
            parent: Parent widget (notebook)
            app: Reference to main app
        """
        super().__init__(parent, padding="10")
        self.app = app
        
        # Variables
        self.class_var = tk.StringVar()
        self.subclass_var = tk.StringVar()
        self.gear_level_var = tk.IntVar(value=80)
        self.weapon_level_var = tk.IntVar(value=90)
        self.unique_count_var = tk.IntVar(value=6)
        self.gem_assumption_var = tk.StringVar(value='avg')
        self.max_solutions_var = tk.IntVar(value=100)
        self.stat_vars = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the configuration UI"""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Top section: Class and gear settings
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        
        self._setup_class_selection(top_frame)
        self._setup_gear_selection(top_frame)
        
        # Middle section: Stat requirements
        middle_frame = ttk.LabelFrame(self, text="Minimum Stat Requirements", padding="10")
        middle_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self._setup_stat_requirements(middle_frame)
        
        # Bottom section: Calculate controls
        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self._setup_calculate_controls(bottom_frame)
    
    def _setup_class_selection(self, parent):
        """Setup class and subclass selection"""
        class_frame = ttk.LabelFrame(parent, text="Class Selection", padding="10")
        class_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Class
        class_row = ttk.Frame(class_frame)
        class_row.pack(fill=tk.X, pady=5)
        ttk.Label(class_row, text="Class:", width=15).pack(side=tk.LEFT)
        self.class_combo = ttk.Combobox(class_row, textvariable=self.class_var,
                                        values=list(config.CLASS_ATTRIBUTES.keys()),
                                        state='readonly', width=20)
        self.class_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.class_combo.bind('<<ComboboxSelected>>', self.on_class_changed)
        
        # Subclass
        subclass_row = ttk.Frame(class_frame)
        subclass_row.pack(fill=tk.X, pady=5)
        ttk.Label(subclass_row, text="Subclass:", width=15).pack(side=tk.LEFT)
        self.subclass_combo = ttk.Combobox(subclass_row, textvariable=self.subclass_var,
                                           state='readonly', width=20)
        self.subclass_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Set default
        if config.CLASS_ATTRIBUTES:
            self.class_combo.current(0)
            self.on_class_changed(None)
    
    def _setup_gear_selection(self, parent):
        """Setup gear level and unique count"""
        gear_frame = ttk.LabelFrame(parent, text="Gear Configuration", padding="10")
        gear_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Gear level
        gear_level_row = ttk.Frame(gear_frame)
        gear_level_row.pack(fill=tk.X, pady=5)
        ttk.Label(gear_level_row, text="Gear Level:", width=15).pack(side=tk.LEFT)
        for level in config_numerical.AVAILABLE_GEAR_LEVELS:
            ttk.Radiobutton(gear_level_row, text=str(level), 
                           variable=self.gear_level_var,
                           value=level).pack(side=tk.LEFT, padx=5)
        
        # Weapon level
        weapon_level_row = ttk.Frame(gear_frame)
        weapon_level_row.pack(fill=tk.X, pady=5)
        ttk.Label(weapon_level_row, text="Weapon Level:", width=15).pack(side=tk.LEFT)
        for level in config_numerical.AVAILABLE_WEAPON_LEVELS:
            ttk.Radiobutton(weapon_level_row, text=str(level),
                           variable=self.weapon_level_var,
                           value=level).pack(side=tk.LEFT, padx=5)
        
        # Unique pieces
        unique_row = ttk.Frame(gear_frame)
        unique_row.pack(fill=tk.X, pady=5)
        ttk.Label(unique_row, text="Unique Pieces:", width=15).pack(side=tk.LEFT)
        unique_spinbox = ttk.Spinbox(unique_row, from_=0, to=6,
                                     textvariable=self.unique_count_var,
                                     width=10)
        unique_spinbox.pack(side=tk.LEFT)
        
        # Gem assumption
        gem_row = ttk.Frame(gear_frame)
        gem_row.pack(fill=tk.X, pady=5)
        ttk.Label(gem_row, text="Gem Value:", width=15).pack(side=tk.LEFT)
        ttk.Radiobutton(gem_row, text="Min (50)", variable=self.gem_assumption_var,
                       value='min').pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(gem_row, text="Avg (60)", variable=self.gem_assumption_var,
                       value='avg').pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(gem_row, text="Max (70)", variable=self.gem_assumption_var,
                       value='max').pack(side=tk.LEFT, padx=5)
    
    def _setup_stat_requirements(self, parent):
        """Setup minimum stat requirement inputs"""
        parent.columnconfigure(1, weight=1)
        
        # Header with info button
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(header_frame, text="Enter minimum required values (0 = no requirement):",
                 font=('TkDefaultFont', 8), foreground='gray').pack(side=tk.LEFT)
        
        ttk.Button(header_frame, text="📊 Show Max Possible", 
                  command=self.show_max_stats).pack(side=tk.RIGHT, padx=(10, 0))
        
        row = 1
        for stat in config.ALL_STATS:
            ttk.Label(parent, text=f"{stat}:", width=15).grid(
                row=row, column=0, sticky=tk.W, pady=3)
            
            var = tk.IntVar(value=0)
            self.stat_vars[stat] = var
            
            entry = ttk.Entry(parent, textvariable=var, width=15)
            entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=3, padx=(5, 0))
            
            row += 1
    
    def show_max_stats(self):
        """Show maximum possible stats for current configuration"""
        from gui_dialogs import MaxStatsDialog
        
        config_data = {
            'class_name': self.class_var.get(),
            'subclass_name': self.subclass_var.get(),
            'gear_level': self.gear_level_var.get(),
            'weapon_level': self.weapon_level_var.get(),
            'unique_count': self.unique_count_var.get(),
            'gem_assumption': self.gem_assumption_var.get()
        }
        
        # Check if class/subclass selected
        if not config_data['class_name'] or not config_data['subclass_name']:
            messagebox.showwarning("Warning", 
                "Please select a class and subclass first to see maximum stats.")
            return
        
        dialog = MaxStatsDialog(self, config_data, self.app.locked_gear_manager)
        dialog.show()
    
    def _setup_calculate_controls(self, parent):
        """Setup calculation controls"""
        # Max solutions
        max_sol_row = ttk.Frame(parent)
        max_sol_row.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(max_sol_row, text="Max Solutions:", width=15).pack(side=tk.LEFT)
        max_solutions_spinbox = ttk.Spinbox(max_sol_row, from_=1, to=1000,
                                            textvariable=self.max_solutions_var,
                                            width=10)
        max_solutions_spinbox.pack(side=tk.LEFT)
        
        # Preset buttons
        preset_frame = ttk.Frame(parent)
        preset_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(preset_frame, text="💾 Save Preset",
                  command=self.save_preset).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(preset_frame, text="📂 Load Preset",
                  command=self.load_preset).pack(side=tk.LEFT)
        
        # Calculate button
        self.calculate_btn = ttk.Button(parent, text="🔍 Calculate Solutions",
                                       command=self.app.start_calculation)
        self.calculate_btn.pack(fill=tk.X, pady=(0, 5))
        
        # Progress label
        self.progress_label = ttk.Label(parent, text="Ready", foreground="green")
        self.progress_label.pack()
    
    def save_preset(self):
        """Save current configuration as preset"""
        from gui_dialogs import SavePresetDialog
        
        dialog = SavePresetDialog(self)
        name = dialog.show()
        
        if name:
            config_data = self.get_config()
            locked_gear_data = self.app.locked_gear_manager.to_dict()
            
            success, msg = self.app.preset_manager.save_preset(name, config_data, locked_gear_data)
            
            if success:
                messagebox.showinfo("Success", f"Preset '{name}' saved!")
            else:
                messagebox.showerror("Error", msg)
    
    def load_preset(self):
        """Load a saved preset"""
        from gui_dialogs import LoadPresetDialog
        
        dialog = LoadPresetDialog(self, self.app.preset_manager)
        filename = dialog.show()
        
        if filename:
            success, data = self.app.preset_manager.load_preset(filename)
            
            if success:
                # Load configuration
                config = data.get('config', {})
                
                self.class_var.set(config.get('class_name', ''))
                self.on_class_changed(None)
                self.subclass_var.set(config.get('subclass_name', ''))
                self.gear_level_var.set(config.get('gear_level', 80))
                self.weapon_level_var.set(config.get('weapon_level', 90))
                self.unique_count_var.set(config.get('unique_count', 6))
                self.gem_assumption_var.set(config.get('gem_assumption', 'avg'))
                self.max_solutions_var.set(config.get('max_solutions', 100))
                
                # Load stat requirements
                min_stats = config.get('min_stats', {})
                for stat, var in self.stat_vars.items():
                    var.set(min_stats.get(stat, 0))
                
                # Load locked gear
                from locked_gear_manager import LockedGearManager
                locked_gear_data = data.get('locked_gear', {})
                self.app.locked_gear_manager = LockedGearManager.from_dict(locked_gear_data)
                
                # Refresh gear tab if it exists
                if hasattr(self.app, 'gear_tab'):
                    self.app.gear_tab.manager = self.app.locked_gear_manager
                    self.app.gear_tab.refresh_display()
                
                messagebox.showinfo("Success", f"Preset '{data['name']}' loaded!")
            else:
                messagebox.showerror("Error", data)
    
    def on_class_changed(self, event):
        """Update subclass options when class changes"""
        class_name = self.class_var.get()
        if class_name in config.SUBCLASSES:
            subclasses = config.SUBCLASSES[class_name]
            self.subclass_combo['values'] = subclasses
            if subclasses:
                self.subclass_combo.current(0)
    
    def get_config(self):
        """
        Get current configuration
        
        Returns:
            Dictionary with all configuration values
        """
        min_stats = {stat: var.get() for stat, var in self.stat_vars.items() 
                    if var.get() > 0}
        
        return {
            'class_name': self.class_var.get(),
            'subclass_name': self.subclass_var.get(),
            'gear_level': self.gear_level_var.get(),
            'weapon_level': self.weapon_level_var.get(),
            'unique_count': self.unique_count_var.get(),
            'gem_assumption': self.gem_assumption_var.get(),
            'min_stats': min_stats,
            'max_solutions': self.max_solutions_var.get()
        }
    
    def set_calculating(self, is_calculating):
        """Update UI state during calculation"""
        state = 'disabled' if is_calculating else 'normal'
        self.calculate_btn.config(state=state)
        
        if is_calculating:
            self.progress_label.config(text="Calculating...", foreground="orange")
        else:
            self.progress_label.config(text="Ready", foreground="green")
    
    def set_progress(self, message, color="black"):
        """Update progress label"""
        self.progress_label.config(text=message, foreground=color)