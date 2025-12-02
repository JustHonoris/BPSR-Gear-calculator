"""
gui_results_tab.py
Results display and filtering tab
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import config


class ResultsTab(ttk.Frame):
    """Results display with advanced filtering"""
    
    def __init__(self, parent, app):
        """
        Initialize results tab
        
        Args:
            parent: Parent widget (notebook)
            app: Reference to main app
        """
        super().__init__(parent, padding="10")
        self.app = app
        
        # State
        self.all_solutions = []
        self.filtered_solutions = []
        self.current_solution_index = 0
        self.advanced_mode = False
        
        # Filter variables
        self.simple_sort_var = tk.StringVar(value="No Sorting")
        self.stat_check_vars = {}
        self.stat_weight_vars = {}
        self.stat_weight_labels = {}
        self.max_reforges_var = tk.IntVar(value=11)
        self.top_n_var = tk.StringVar(value="all")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the results UI"""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        
        # Top: Status
        self.status_label = ttk.Label(self, text="Configure settings and click Calculate",
                                      font=('TkDefaultFont', 10, 'bold'))
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Middle: Filtering
        self._setup_filtering()
        
        # Bottom: Results display
        self._setup_results_display()
    
    def _setup_filtering(self):
        """Setup filtering controls"""
        filter_frame = ttk.LabelFrame(self, text="Filtering & Sorting", padding="10")
        filter_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filter_frame.columnconfigure(0, weight=1)
        
        # Advanced toggle button
        self.advanced_toggle_btn = ttk.Button(filter_frame, 
                                             text="▼ Show Advanced Filters",
                                             command=self.toggle_advanced_mode)
        self.advanced_toggle_btn.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Simple mode (always visible)
        simple_frame = ttk.Frame(filter_frame)
        simple_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(simple_frame, text="Quick Sort:").pack(side=tk.LEFT, padx=(0, 10))
        self.simple_sort_combo = ttk.Combobox(simple_frame, 
                                             textvariable=self.simple_sort_var,
                                             state='readonly', width=30)
        self.simple_sort_combo['values'] = [
            "No Sorting",
            "Most Flexible (Fewest Reforges)",
            "Highest Crit",
            "Highest Haste",
            "Highest Mastery",
            "Highest Versatility",
            "Highest Luck"
        ]
        self.simple_sort_combo.current(0)
        self.simple_sort_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.simple_sort_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        
        # Advanced mode (toggleable)
        self.advanced_frame = ttk.Frame(filter_frame)
        # Not gridded initially
        
        self._setup_advanced_filters()
    
    def _setup_advanced_filters(self):
        """Setup advanced filtering controls"""
        # Stat Priority Section
        stat_frame = ttk.LabelFrame(self.advanced_frame, text="Stat Priority (Weighted)",
                                   padding="10")
        stat_frame.pack(fill=tk.X, pady=5)
        
        help_text = ("Check stats to include in scoring. Set weights:\n"
                    "+1 to +10 = Maximize (prefer MORE)\n"
                    "0 = Neutral (ignore)\n"
                    "-1 to -10 = Minimize (prefer LESS / penalty)")
        ttk.Label(stat_frame, text=help_text, font=('TkDefaultFont', 8),
                 foreground="gray").pack(anchor=tk.W, pady=(0, 10))
        
        for stat in config.ALL_STATS:
            stat_row = ttk.Frame(stat_frame)
            stat_row.pack(fill=tk.X, pady=3)
            
            # Checkbox
            check_var = tk.BooleanVar(value=False)
            self.stat_check_vars[stat] = check_var
            
            cb = ttk.Checkbutton(stat_row, text=f"{stat}:", variable=check_var,
                               command=self.apply_filters, width=12)
            cb.pack(side=tk.LEFT, padx=(0, 10))
            
            # Weight slider
            weight_var = tk.IntVar(value=0)
            self.stat_weight_vars[stat] = weight_var
            
            weight_scale = ttk.Scale(stat_row, from_=-10, to=10,
                                   variable=weight_var, orient=tk.HORIZONTAL,
                                   command=lambda v, s=stat: self.on_weight_change(s, v))
            weight_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            weight_scale.set(0)
            
            # Weight label
            weight_label = ttk.Label(stat_row, text="0", width=4,
                                    anchor=tk.CENTER, relief=tk.SUNKEN)
            self.stat_weight_labels[stat] = weight_label
            weight_label.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Resource Limits Section
        resource_frame = ttk.LabelFrame(self.advanced_frame, text="Resource Limits",
                                       padding="10")
        resource_frame.pack(fill=tk.X, pady=5)
        
        reforge_row = ttk.Frame(resource_frame)
        reforge_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(reforge_row, text="Max Reforges Used:").pack(side=tk.LEFT, padx=(0, 10))
        self.max_reforges_label = ttk.Label(reforge_row, text="11")
        self.max_reforges_label.pack(side=tk.RIGHT)
        
        self.max_reforges_scale = ttk.Scale(reforge_row, from_=0, to=11,
                                           variable=self.max_reforges_var,
                                           orient=tk.HORIZONTAL,
                                           command=self.on_reforge_scale_change)
        self.max_reforges_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Display Limit Section
        limit_frame = ttk.LabelFrame(self.advanced_frame, text="Display Limit",
                                    padding="10")
        limit_frame.pack(fill=tk.X, pady=5)
        
        limit_row = ttk.Frame(limit_frame)
        limit_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(limit_row, text="Show Top:").pack(side=tk.LEFT, padx=(0, 10))
        for val in ["10", "25", "50", "100", "All"]:
            rb = ttk.Radiobutton(limit_row, text=val, variable=self.top_n_var,
                               value=val.lower(), command=self.apply_filters)
            rb.pack(side=tk.LEFT, padx=5)
        
        # Apply button
        ttk.Button(self.advanced_frame, text="Apply Filters",
                  command=self.apply_filters).pack(fill=tk.X, pady=(10, 0))
    
    def _setup_results_display(self):
        """Setup results display area"""
        display_frame = ttk.Frame(self)
        display_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(1, weight=1)
        
        # Navigation controls
        nav_frame = ttk.Frame(display_frame)
        nav_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(nav_frame, text="◀ Previous",
                  command=self.prev_solution).pack(side=tk.LEFT, padx=5)
        
        self.solution_label = ttk.Label(nav_frame, text="No solutions yet")
        self.solution_label.pack(side=tk.LEFT, padx=20)
        
        ttk.Button(nav_frame, text="Next ▶",
                  command=self.next_solution).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(nav_frame, text="📄 Export All",
                  command=self.export_solutions).pack(side=tk.RIGHT, padx=5)
        
        # Results text area
        results_container = ttk.LabelFrame(display_frame, text="Solution Details",
                                          padding="5")
        results_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.results_text = scrolledtext.ScrolledText(results_container, wrap=tk.WORD,
                                                      width=70, height=25,
                                                      font=('Courier', 9))
        self.results_text.pack(fill=tk.BOTH, expand=True)
    
    def toggle_advanced_mode(self):
        """Toggle advanced filtering mode"""
        self.advanced_mode = not self.advanced_mode
        
        if self.advanced_mode:
            self.advanced_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
            self.advanced_toggle_btn.config(text="▲ Hide Advanced Filters")
        else:
            self.advanced_frame.grid_forget()
            self.advanced_toggle_btn.config(text="▼ Show Advanced Filters")
    
    def on_weight_change(self, stat, value):
        """Update weight label and apply filters"""
        val = int(float(value))
        self.stat_weight_labels[stat].config(text=str(val))
        
        # Color code
        if val > 0:
            self.stat_weight_labels[stat].config(foreground="green")
        elif val < 0:
            self.stat_weight_labels[stat].config(foreground="red")
        else:
            self.stat_weight_labels[stat].config(foreground="black")
        
        self.apply_filters()
    
    def on_reforge_scale_change(self, value):
        """Update reforge label and apply filters"""
        val = int(float(value))
        self.max_reforges_label.config(text=str(val))
        self.apply_filters()
    
    def set_solutions(self, solutions, calculator):
        """
        Set solutions to display
        
        Args:
            solutions: List of solution dictionaries
            calculator: Calculator instance for formatting
        """
        self.all_solutions = solutions
        self.calculator = calculator
        
        if solutions:
            self.status_label.config(text=f"Found {len(solutions)} valid solutions")
            self.apply_filters()
        else:
            self.status_label.config(text="No valid solutions found")
            self.filtered_solutions = []
            self.display_no_solutions()
    
    def apply_filters(self):
        """Apply all active filters and sort solutions"""
        if not self.all_solutions:
            return
        
        filtered = self.all_solutions.copy()
        
        # Apply resource limit
        if self.advanced_mode:
            max_reforges = self.max_reforges_var.get()
            filtered = [s for s in filtered
                       if sum(s['reforge_counts'].values()) <= max_reforges]
        
        # Apply sorting
        sort_key = None
        
        if self.advanced_mode:
            checked_stats = [stat for stat, var in self.stat_check_vars.items() if var.get()]
            if checked_stats:
                def weighted_score(solution):
                    score = 0
                    for stat in checked_stats:
                        stat_value = solution['final_totals'].get(stat, 0)
                        weight = self.stat_weight_vars[stat].get()
                        score += stat_value * weight
                    return score
                sort_key = weighted_score
        
        if sort_key is None:
            simple_sort = self.simple_sort_var.get()
            if simple_sort == "Most Flexible (Fewest Reforges)":
                sort_key = lambda s: sum(s['reforge_counts'].values())
                filtered.sort(key=sort_key)
            elif simple_sort.startswith("Highest "):
                stat_name = simple_sort.replace("Highest ", "")
                sort_key = lambda s: s['final_totals'].get(stat_name, 0)
                filtered.sort(key=sort_key, reverse=True)
        else:
            filtered.sort(key=sort_key, reverse=True)
        
        # Apply top N limit
        if self.advanced_mode:
            top_n = self.top_n_var.get()
            if top_n != "all":
                n = int(top_n)
                filtered = filtered[:n]
        
        self.filtered_solutions = filtered
        
        # Update status
        if filtered:
            if len(filtered) < len(self.all_solutions):
                self.status_label.config(
                    text=f"Showing {len(filtered)} of {len(self.all_solutions)} solutions (filtered)"
                )
            else:
                self.status_label.config(text=f"Showing all {len(filtered)} solutions")
            
            self.current_solution_index = 0
            self.display_current_solution()
        else:
            self.display_no_filtered_solutions()
    
    def display_current_solution(self):
        """Display the current solution"""
        if not self.filtered_solutions:
            return
        
        if self.current_solution_index < 0:
            self.current_solution_index = 0
        elif self.current_solution_index >= len(self.filtered_solutions):
            self.current_solution_index = len(self.filtered_solutions) - 1
        
        self.solution_label.config(
            text=f"Solution {self.current_solution_index + 1} of {len(self.filtered_solutions)}"
        )
        
        solution = self.filtered_solutions[self.current_solution_index]
        formatted = self.calculator.format_solution(solution, self.current_solution_index + 1)
        
        # Add filter score if applicable
        if self.advanced_mode:
            checked_stats = [stat for stat, var in self.stat_check_vars.items() if var.get()]
            if checked_stats:
                score = 0
                score_breakdown = []
                for stat in checked_stats:
                    stat_value = solution['final_totals'].get(stat, 0)
                    weight = self.stat_weight_vars[stat].get()
                    contribution = stat_value * weight
                    score += contribution
                    
                    sign = "+" if contribution >= 0 else ""
                    score_breakdown.append(f"{stat}({stat_value})×{weight:+d}={sign}{contribution:,}")
                
                formatted += f"\n\n--- FILTER SCORE ---\n"
                formatted += f"Total Score: {score:,}\n"
                formatted += f"Breakdown: {' '.join(score_breakdown)}"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, formatted)
    
    def display_no_solutions(self):
        """Display message when no solutions found"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0,
            "No valid solutions found that meet the requirements.\n\n"
            "Try:\n"
            "- Lowering minimum stat requirements\n"
            "- Increasing unique gear count\n"
            "- Using higher gear/weapon levels\n"
            "- Adjusting gem assumptions\n"
            "- Removing locked gear restrictions")
    
    def display_no_filtered_solutions(self):
        """Display message when filters eliminate all solutions"""
        self.status_label.config(text="No solutions match current filters")
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0,
            "No solutions match the current filter criteria.\n\n"
            "Try adjusting your filters.")
    
    def prev_solution(self):
        """Show previous solution"""
        if self.filtered_solutions and self.current_solution_index > 0:
            self.current_solution_index -= 1
            self.display_current_solution()
    
    def next_solution(self):
        """Show next solution"""
        if self.filtered_solutions and self.current_solution_index < len(self.filtered_solutions) - 1:
            self.current_solution_index += 1
            self.display_current_solution()
    
    def export_solutions(self):
        """Export all filtered solutions to a text file"""
        if not self.filtered_solutions:
            messagebox.showinfo("Info", "No solutions to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                config_data = self.app.config_tab.get_config()
                
                with open(filename, 'w') as f:
                    f.write(f"RPG Gear Calculator Results\n")
                    f.write(f"{'='*60}\n\n")
                    f.write(f"Configuration:\n")
                    f.write(f"  Class: {config_data['class_name']} - {config_data['subclass_name']}\n")
                    f.write(f"  Gear Level: {config_data['gear_level']}\n")
                    f.write(f"  Weapon Level: {config_data['weapon_level']}\n")
                    f.write(f"  Unique Pieces: {config_data['unique_count']}\n")
                    f.write(f"  Gem Assumption: {config_data['gem_assumption']}\n\n")
                    f.write(f"Minimum Requirements:\n")
                    for stat, val in config_data['min_stats'].items():
                        f.write(f"  {stat}: {val}\n")
                    f.write(f"\nTotal Solutions Found: {len(self.all_solutions)}\n")
                    f.write(f"Showing (after filters): {len(self.filtered_solutions)}\n")
                    f.write(f"{'='*60}\n")
                    
                    for i, solution in enumerate(self.filtered_solutions):
                        formatted = self.calculator.format_solution(solution, i + 1)
                        f.write(f"\n{formatted}\n")
                
                messagebox.showinfo("Success",
                                  f"Exported {len(self.filtered_solutions)} solutions to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
