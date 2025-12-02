"""
gui_gear_tab.py
Locked gear management tab
"""

import tkinter as tk
from tkinter import ttk, messagebox
import config
import config_numerical
from gui_dialogs import AddEditGearDialog, ConfirmDialog


class GearTab(ttk.Frame):
    """Tab for managing locked gear pieces"""
    
    def __init__(self, parent, app):
        """
        Initialize gear tab
        
        Args:
            parent: Parent widget (notebook)
            app: Reference to main app
        """
        super().__init__(parent, padding="10")
        self.app = app
        self.manager = app.locked_gear_manager
        
        self.setup_ui()
        self.refresh_display()
    
    def setup_ui(self):
        """Setup the gear management UI"""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Top: Instructions and buttons
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        top_frame.columnconfigure(0, weight=1)
        
        # Instructions
        instructions = (
            "Lock gear pieces you already own. The calculator will use these pieces "
            "and find what other gear you need.\n"
            "Locked gear reserves gems and reforges - the calculator will only use remaining resources."
        )
        ttk.Label(top_frame, text=instructions, wraplength=700, 
                 foreground="gray", font=('TkDefaultFont', 9)).grid(
                     row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Button row
        button_row = ttk.Frame(top_frame)
        button_row.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(button_row, text="➕ Add Gear", 
                  command=self.add_gear).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_row, text="🗑️ Clear All",
                  command=self.clear_all).pack(side=tk.LEFT, padx=(0, 5))
        
        self.locked_count_label = ttk.Label(button_row, text="Locked: 0/10",
                                            font=('TkDefaultFont', 9, 'bold'))
        self.locked_count_label.pack(side=tk.RIGHT)
        
        # Middle: Locked gear list
        list_frame = ttk.LabelFrame(self, text="Locked Gear Pieces", padding="10")
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview for gear list
        columns = ('Slot', 'Type', 'Stats', 'Gem', 'Reforge')
        self.gear_tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                      height=10, selectmode='browse')
        
        # Configure columns
        self.gear_tree.heading('Slot', text='Slot')
        self.gear_tree.heading('Type', text='Type')
        self.gear_tree.heading('Stats', text='Stats')
        self.gear_tree.heading('Gem', text='Gem')
        self.gear_tree.heading('Reforge', text='Reforge')
        
        self.gear_tree.column('Slot', width=120, anchor=tk.W)
        self.gear_tree.column('Type', width=80, anchor=tk.CENTER)
        self.gear_tree.column('Stats', width=200, anchor=tk.W)
        self.gear_tree.column('Gem', width=100, anchor=tk.W)
        self.gear_tree.column('Reforge', width=100, anchor=tk.W)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                 command=self.gear_tree.yview)
        self.gear_tree.configure(yscrollcommand=scrollbar.set)
        
        self.gear_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Context menu buttons
        context_frame = ttk.Frame(list_frame)
        context_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(context_frame, text="✏️ Edit Selected",
                  command=self.edit_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(context_frame, text="🗑️ Remove Selected",
                  command=self.remove_selected).pack(side=tk.LEFT)
        
        # Bottom: Stats preview
        preview_frame = ttk.LabelFrame(self, text="Stats from Locked Gear", padding="10")
        preview_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        preview_frame.columnconfigure(1, weight=1)
        
        self.stats_text = tk.Text(preview_frame, height=8, width=70, 
                                 font=('Courier', 9), wrap=tk.WORD)
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.stats_text.config(state='disabled')
        
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL,
                                         command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=preview_scrollbar.set)
        preview_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def refresh_display(self):
        """Refresh the display of locked gear"""
        # Clear tree
        for item in self.gear_tree.get_children():
            self.gear_tree.delete(item)
        
        # Add locked pieces
        for piece in self.manager.locked_pieces:
            gear_type = "UNIQUE" if piece.is_unique else "REGULAR"
            
            if piece.is_unique:
                stats_str = f"{piece.main_stat} + {piece.sub_stat}"
            else:
                stats_str = f"{piece.main_stat} (main) + {piece.sub_stat} (sub)"
            
            gem_str = piece.gem_stat if piece.gem_stat else "-"
            reforge_str = piece.reforge_stat if piece.reforge_stat else "-"
            
            self.gear_tree.insert('', tk.END, values=(
                piece.slot,
                gear_type,
                stats_str,
                gem_str,
                reforge_str
            ))
        
        # Update count
        count = self.manager.count()
        self.locked_count_label.config(text=f"Locked: {count}/10")
        
        # Update stats preview
        self.update_stats_preview()
    
    def update_stats_preview(self):
        """Update the stats preview panel"""
        self.stats_text.config(state='normal')
        self.stats_text.delete(1.0, tk.END)
        
        if self.manager.count() == 0:
            self.stats_text.insert(1.0, "No locked gear yet.\n\nClick 'Add Gear' to lock gear pieces you already own.")
            self.stats_text.config(state='disabled')
            return
        
        # Get configuration from config tab
        config_data = self.app.config_tab.get_config()
        gear_level = config_data['gear_level']
        unique_stats = config_numerical.get_unique_stats(
            config_data['class_name'],
            config_data['subclass_name']
        )
        
        gem_values = {'min': 50, 'avg': 60, 'max': 70}
        gem_value = gem_values.get(config_data['gem_assumption'], 60)
        
        # Calculate stats
        total_stats = self.manager.get_total_stats(gear_level, unique_stats, gem_value)
        gems_used, reforges_used = self.manager.get_resource_usage()
        gems_avail, reforges_avail = self.manager.get_available_resources()
        
        # Format display
        lines = []
        lines.append("=== STATS FROM LOCKED GEAR ===\n")
        
        for stat in config.ALL_STATS:
            value = total_stats.get(stat, 0)
            if value > 0:
                lines.append(f"{stat:12}: {value:4}")
        
        lines.append(f"\n\n=== RESOURCES ===")
        lines.append(f"Gems Used:       {gems_used}/11")
        lines.append(f"Gems Available:  {gems_avail}")
        lines.append(f"\nReforges Used:   {reforges_used}/11")
        lines.append(f"Reforges Avail:  {reforges_avail}")
        
        lines.append(f"\n\n=== CALCULATION ===")
        lines.append(f"Calculator will find gear for {10 - self.manager.count()} remaining slots")
        lines.append(f"using {gems_avail} gems and {reforges_avail} reforges.")
        
        self.stats_text.insert(1.0, '\n'.join(lines))
        self.stats_text.config(state='disabled')
    
    def add_gear(self):
        """Open dialog to add a new gear piece"""
        # Get current configuration
        config_data = self.app.config_tab.get_config()
        
        if not config_data['class_name'] or not config_data['subclass_name']:
            messagebox.showerror("Error", 
                "Please select a class and subclass in the Configuration tab first.")
            return
        
        # Get unique stats
        unique_stats = config_numerical.get_unique_stats(
            config_data['class_name'],
            config_data['subclass_name']
        )
        
        # Get attribute
        attribute = config.CLASS_ATTRIBUTES[config_data['class_name']]
        
        # Show dialog
        dialog = AddEditGearDialog(
            parent=self,
            gear_manager=self.manager,
            unique_stats=unique_stats,
            attribute=attribute,
            gear_level=config_data['gear_level']
        )
        
        result = dialog.show()
        
        if result:
            success, message = self.manager.add_gear(result)
            if success:
                self.refresh_display()
                messagebox.showinfo("Success", f"Added {result.slot}")
            else:
                messagebox.showerror("Error", message)
    
    def edit_selected(self):
        """Edit the selected gear piece"""
        selection = self.gear_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a gear piece to edit")
            return
        
        # Get selected item
        item = selection[0]
        values = self.gear_tree.item(item, 'values')
        slot = values[0]
        
        # Get the gear piece
        gear = self.manager.get_gear(slot)
        if not gear:
            return
        
        # Get current configuration
        config_data = self.app.config_tab.get_config()
        unique_stats = config_numerical.get_unique_stats(
            config_data['class_name'],
            config_data['subclass_name']
        )
        attribute = config.CLASS_ATTRIBUTES[config_data['class_name']]
        
        # Show dialog
        dialog = AddEditGearDialog(
            parent=self,
            gear_manager=self.manager,
            unique_stats=unique_stats,
            attribute=attribute,
            gear_level=config_data['gear_level'],
            existing_gear=gear
        )
        
        result = dialog.show()
        
        if result:
            # Remove old and add new
            self.manager.remove_gear(slot)
            success, message = self.manager.add_gear(result)
            if success:
                self.refresh_display()
                messagebox.showinfo("Success", f"Updated {result.slot}")
            else:
                # Restore old gear if failed
                self.manager.add_gear(gear)
                messagebox.showerror("Error", message)
    
    def remove_selected(self):
        """Remove the selected gear piece"""
        selection = self.gear_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a gear piece to remove")
            return
        
        # Get selected item
        item = selection[0]
        values = self.gear_tree.item(item, 'values')
        slot = values[0]
        
        # Confirm
        if messagebox.askyesno("Confirm", f"Remove {slot} from locked gear?"):
            self.manager.remove_gear(slot)
            self.refresh_display()
    
    def clear_all(self):
        """Clear all locked gear"""
        if self.manager.count() == 0:
            messagebox.showinfo("Info", "No locked gear to clear")
            return
        
        # Confirm
        dialog = ConfirmDialog(
            self,
            "Confirm Clear All",
            f"Remove all {self.manager.count()} locked gear pieces?"
        )
        
        if dialog.show():
            self.manager.clear_all()
            self.refresh_display()
            messagebox.showinfo("Success", "All locked gear removed")
