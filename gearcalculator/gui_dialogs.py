"""
gui_dialogs.py
Popup dialogs for gear editing and other interactions
"""

import tkinter as tk
from tkinter import ttk, messagebox
import config
import config_numerical
from locked_gear_manager import LockedGear


class AddEditGearDialog:
    """Dialog for adding or editing a locked gear piece"""
    
    def __init__(self, parent, gear_manager, unique_stats, attribute, gear_level, 
                 existing_gear=None):
        """
        Initialize the dialog
        
        Args:
            parent: Parent window
            gear_manager: LockedGearManager instance
            unique_stats: List of [stat1, stat2] for subclass
            attribute: Class attribute (Strength/Agility/Intellect)
            gear_level: Current gear level
            existing_gear: LockedGear instance if editing, None if adding
        """
        self.parent = parent
        self.gear_manager = gear_manager
        self.unique_stats = unique_stats
        self.attribute = attribute
        self.gear_level = gear_level
        self.existing_gear = existing_gear
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Gear" if existing_gear else "Add Gear")
        self.dialog.geometry("450x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Variables
        self.slot_var = tk.StringVar()
        self.type_var = tk.StringVar(value="regular")
        self.main_stat_var = tk.StringVar()
        self.sub_stat_var = tk.StringVar()
        self.gem_stat_var = tk.StringVar()
        self.gem_none_var = tk.BooleanVar(value=True)
        self.reforge_stat_var = tk.StringVar()
        self.reforge_none_var = tk.BooleanVar(value=True)
        
        self.setup_ui()
        self.populate_if_editing()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup the dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        # Slot selection
        ttk.Label(main_frame, text="Slot:", font=('TkDefaultFont', 9, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        
        # Get available slots (not already locked, unless editing)
        available_slots = []
        for slot in config.ALL_GEAR_SLOTS:
            if self.existing_gear and slot == self.existing_gear.slot:
                available_slots.append(slot)
            elif not self.gear_manager.is_slot_locked(slot):
                available_slots.append(slot)
        
        if not available_slots:
            available_slots = ["No slots available"]
        
        self.slot_combo = ttk.Combobox(main_frame, textvariable=self.slot_var,
                                      values=available_slots, state='readonly', width=30)
        self.slot_combo.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        if available_slots and available_slots[0] != "No slots available":
            self.slot_combo.current(0)
        row += 1
        
        # Gear type
        ttk.Label(main_frame, text="Gear Type:", font=('TkDefaultFont', 9, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        
        type_frame = ttk.Frame(main_frame)
        type_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Radiobutton(type_frame, text="Regular Gear", variable=self.type_var,
                       value="regular", command=self.on_type_changed).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(type_frame, text="Unique Gear", variable=self.type_var,
                       value="unique", command=self.on_type_changed).pack(side=tk.LEFT)
        row += 1
        
        # Stats frame (for regular gear)
        self.stats_frame = ttk.LabelFrame(main_frame, text="Stats", padding="10")
        self.stats_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        row += 1
        
        # Main stat
        main_stat_row = ttk.Frame(self.stats_frame)
        main_stat_row.pack(fill=tk.X, pady=5)
        ttk.Label(main_stat_row, text="Main Stat:", width=12).pack(side=tk.LEFT)
        self.main_stat_combo = ttk.Combobox(main_stat_row, textvariable=self.main_stat_var,
                                           values=config.ALL_STATS, state='readonly', width=15)
        self.main_stat_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.main_stat_combo.bind('<<ComboboxSelected>>', self.update_sub_stat_options)
        
        # Sub stat
        sub_stat_row = ttk.Frame(self.stats_frame)
        sub_stat_row.pack(fill=tk.X, pady=5)
        ttk.Label(sub_stat_row, text="Sub Stat:", width=12).pack(side=tk.LEFT)
        self.sub_stat_combo = ttk.Combobox(sub_stat_row, textvariable=self.sub_stat_var,
                                          values=config.ALL_STATS, state='readonly', width=15)
        self.sub_stat_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Unique gear info label
        self.unique_info_label = ttk.Label(self.stats_frame,
            text=f"Unique gear has fixed stats:\n{self.unique_stats[0]} + {self.unique_stats[1]}",
            foreground="blue", font=('TkDefaultFont', 8))
        # Not packed initially
        
        # Gem selection
        gem_frame = ttk.LabelFrame(main_frame, text="Gem (Optional)", padding="10")
        gem_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        row += 1
        
        gem_none_row = ttk.Frame(gem_frame)
        gem_none_row.pack(fill=tk.X, pady=(0, 5))
        ttk.Checkbutton(gem_none_row, text="No Gem", variable=self.gem_none_var,
                       command=self.on_gem_none_changed).pack(side=tk.LEFT)
        
        gem_stat_row = ttk.Frame(gem_frame)
        gem_stat_row.pack(fill=tk.X)
        ttk.Label(gem_stat_row, text="Gem Stat:", width=12).pack(side=tk.LEFT)
        self.gem_stat_combo = ttk.Combobox(gem_stat_row, textvariable=self.gem_stat_var,
                                          values=config.ALL_STATS, state='readonly', width=15)
        self.gem_stat_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.gem_stat_combo.config(state='disabled')
        
        # Reforge selection
        reforge_frame = ttk.LabelFrame(main_frame, text="Reforge (Optional)", padding="10")
        reforge_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        row += 1
        
        reforge_none_row = ttk.Frame(reforge_frame)
        reforge_none_row.pack(fill=tk.X, pady=(0, 5))
        ttk.Checkbutton(reforge_none_row, text="No Reforge", variable=self.reforge_none_var,
                       command=self.on_reforge_none_changed).pack(side=tk.LEFT)
        
        reforge_stat_row = ttk.Frame(reforge_frame)
        reforge_stat_row.pack(fill=tk.X)
        ttk.Label(reforge_stat_row, text="Reforge Stat:", width=12).pack(side=tk.LEFT)
        self.reforge_stat_combo = ttk.Combobox(reforge_stat_row, textvariable=self.reforge_stat_var,
                                              values=config.ALL_STATS, state='readonly', width=15)
        self.reforge_stat_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.reforge_stat_combo.config(state='disabled')
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
        
        # Initial type update
        self.on_type_changed()
    
    def populate_if_editing(self):
        """Populate fields if editing existing gear"""
        if not self.existing_gear:
            return
        
        gear = self.existing_gear
        
        self.slot_var.set(gear.slot)
        self.type_var.set("unique" if gear.is_unique else "regular")
        
        if not gear.is_unique:
            self.main_stat_var.set(gear.main_stat)
            self.sub_stat_var.set(gear.sub_stat)
        
        if gear.gem_stat:
            self.gem_none_var.set(False)
            self.gem_stat_var.set(gear.gem_stat)
            self.gem_stat_combo.config(state='readonly')
        
        if gear.reforge_stat:
            self.reforge_none_var.set(False)
            self.reforge_stat_var.set(gear.reforge_stat)
            self.reforge_stat_combo.config(state='readonly')
        
        self.on_type_changed()
    
    def on_type_changed(self):
        """Handle gear type change"""
        is_unique = self.type_var.get() == "unique"
        
        if is_unique:
            # Hide regular stats, show unique info
            self.main_stat_combo.pack_forget()
            self.sub_stat_combo.pack_forget()
            self.main_stat_combo.master.pack_forget()
            self.sub_stat_combo.master.pack_forget()
            self.unique_info_label.pack(pady=10)
        else:
            # Show regular stats, hide unique info
            self.unique_info_label.pack_forget()
            self.main_stat_combo.master.pack(fill=tk.X, pady=5)
            self.sub_stat_combo.master.pack(fill=tk.X, pady=5)
    
    def on_gem_none_changed(self):
        """Handle gem none checkbox"""
        if self.gem_none_var.get():
            self.gem_stat_combo.config(state='disabled')
            self.gem_stat_var.set('')
        else:
            self.gem_stat_combo.config(state='readonly')
    
    def on_reforge_none_changed(self):
        """Handle reforge none checkbox"""
        if self.reforge_none_var.get():
            self.reforge_stat_combo.config(state='disabled')
            self.reforge_stat_var.set('')
        else:
            self.reforge_stat_combo.config(state='readonly')
    
    def update_sub_stat_options(self, event=None):
        """Update sub stat options to exclude main stat"""
        main = self.main_stat_var.get()
        if main:
            available = [s for s in config.ALL_STATS if s != main]
            self.sub_stat_combo['values'] = available
    
    def validate(self):
        """Validate inputs"""
        slot = self.slot_var.get()
        if not slot or slot == "No slots available":
            messagebox.showerror("Error", "Please select a valid slot", parent=self.dialog)
            return False
        
        is_unique = self.type_var.get() == "unique"
        
        if not is_unique:
            main = self.main_stat_var.get()
            sub = self.sub_stat_var.get()
            
            if not main or not sub:
                messagebox.showerror("Error", "Please select both main and sub stats", 
                                   parent=self.dialog)
                return False
            
            if main == sub:
                messagebox.showerror("Error", "Main and sub stats must be different",
                                   parent=self.dialog)
                return False
            
            # Check forbidden stats
            forbidden = config.get_forbidden_stat(slot, self.attribute)
            if forbidden:
                if main == forbidden or sub == forbidden:
                    messagebox.showerror("Error",
                        f"{forbidden} is forbidden on {slot} for {self.attribute} classes",
                        parent=self.dialog)
                    return False
        
        # Validate gem/reforge if selected
        if not self.gem_none_var.get() and not self.gem_stat_var.get():
            messagebox.showerror("Error", "Please select a gem stat or check 'No Gem'",
                               parent=self.dialog)
            return False
        
        if not self.reforge_none_var.get() and not self.reforge_stat_var.get():
            messagebox.showerror("Error", "Please select a reforge stat or check 'No Reforge'",
                               parent=self.dialog)
            return False
        
        return True
    
    def save(self):
        """Save the gear"""
        if not self.validate():
            return
        
        slot = self.slot_var.get()
        is_unique = self.type_var.get() == "unique"
        
        if is_unique:
            main_stat = self.unique_stats[0]
            sub_stat = self.unique_stats[1]
        else:
            main_stat = self.main_stat_var.get()
            sub_stat = self.sub_stat_var.get()
        
        gem_stat = None if self.gem_none_var.get() else self.gem_stat_var.get()
        reforge_stat = None if self.reforge_none_var.get() else self.reforge_stat_var.get()
        
        self.result = LockedGear(
            slot=slot,
            is_unique=is_unique,
            main_stat=main_stat,
            sub_stat=sub_stat,
            gem_stat=gem_stat,
            reforge_stat=reforge_stat
        )
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel the dialog"""
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        """Show dialog and wait for result"""
        self.dialog.wait_window()
        return self.result


class ConfirmDialog:
    """Simple confirmation dialog"""
    
    def __init__(self, parent, title, message):
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Message
        ttk.Label(self.dialog, text=message, wraplength=350, padding="20").pack()
        
        # Buttons
        button_frame = ttk.Frame(self.dialog, padding="20")
        button_frame.pack()
        
        ttk.Button(button_frame, text="Yes", command=self.yes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="No", command=self.no).pack(side=tk.LEFT, padx=5)
        
        # Center
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def yes(self):
        self.result = True
        self.dialog.destroy()
    
    def no(self):
        self.result = False
        self.dialog.destroy()
    
    def show(self):
        self.dialog.wait_window()
        return self.result
