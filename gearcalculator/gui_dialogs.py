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
            for child in self.stats_frame.winfo_children():
                child.pack_forget()
            self.unique_info_label.pack(pady=10)
        else:
            # Show regular stats, hide unique info
            self.unique_info_label.pack_forget()
            # Recreate the stat rows
            for child in self.stats_frame.winfo_children():
                child.pack_forget()
            
            # Main stat row
            main_stat_row = ttk.Frame(self.stats_frame)
            main_stat_row.pack(fill=tk.X, pady=5)
            ttk.Label(main_stat_row, text="Main Stat:", width=12).pack(side=tk.LEFT)
            self.main_stat_combo = ttk.Combobox(main_stat_row, textvariable=self.main_stat_var,
                                               values=config.ALL_STATS, state='readonly', width=15)
            self.main_stat_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.main_stat_combo.bind('<<ComboboxSelected>>', self.update_sub_stat_options)
            
            # Sub stat row
            sub_stat_row = ttk.Frame(self.stats_frame)
            sub_stat_row.pack(fill=tk.X, pady=5)
            ttk.Label(sub_stat_row, text="Sub Stat:", width=12).pack(side=tk.LEFT)
            self.sub_stat_combo = ttk.Combobox(sub_stat_row, textvariable=self.sub_stat_var,
                                              values=config.ALL_STATS, state='readonly', width=15)
            self.sub_stat_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
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


class SavePresetDialog:
    """Dialog for saving a preset"""
    
    def __init__(self, parent):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Save Preset")
        self.dialog.geometry("400x180")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        ttk.Label(main_frame, text="Enter a name for this preset:",
                 font=('TkDefaultFont', 9)).pack(anchor=tk.W, pady=(0, 10))
        
        # Name entry
        ttk.Label(main_frame, text="Preset Name:").pack(anchor=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=40)
        self.name_entry.pack(fill=tk.X, pady=(0, 20))
        self.name_entry.focus()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        self.name_entry.bind('<Return>', lambda e: self.save())
        
        # Center
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a preset name", parent=self.dialog)
            return
        
        self.result = name
        self.dialog.destroy()
    
    def cancel(self):
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        self.dialog.wait_window()
        return self.result


class MaxStatsDialog:
    """Dialog showing maximum possible stats for current configuration"""
    
    def __init__(self, parent, config_data, locked_gear_manager):
        self.config_data = config_data
        self.locked_gear_manager = locked_gear_manager
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Maximum Possible Stats")
        self.dialog.geometry("650x700")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Maximum Achievable Stats",
                 font=('TkDefaultFont', 12, 'bold')).pack(pady=(0, 10))
        
        # Configuration summary
        config_frame = ttk.LabelFrame(main_frame, text="Current Configuration", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        config_text = tk.Text(config_frame, height=6, width=70, font=('TkDefaultFont', 9))
        config_text.pack()
        config_text.insert(1.0, self._format_config())
        config_text.config(state='disabled')
        
        # Max stats display
        stats_frame = ttk.LabelFrame(main_frame, text="Maximum Possible Stats", padding="10")
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.stats_text = tk.Text(stats_frame, height=20, width=70, 
                                 font=('Courier', 9), wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=scrollbar.set)
        
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Calculate and display
        self._calculate_max_stats()
        
        # Close button
        ttk.Button(main_frame, text="Close", command=self.dialog.destroy).pack()
        
        # Center
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def _format_config(self):
        """Format configuration summary"""
        lines = []
        lines.append(f"Class: {self.config_data['class_name']} - {self.config_data['subclass_name']}")
        lines.append(f"Gear Level: {self.config_data['gear_level']}")
        lines.append(f"Weapon Level: {self.config_data['weapon_level']}")
        lines.append(f"Unique Pieces: {self.config_data['unique_count']}")
        lines.append(f"Gem Assumption: {self.config_data['gem_assumption']}")
        
        locked_count = self.locked_gear_manager.count() if self.locked_gear_manager else 0
        lines.append(f"Locked Gear: {locked_count} pieces")
        
        return '\n'.join(lines)
    
    def _calculate_max_stats(self):
        """Calculate and display maximum possible stats"""
        import config_numerical
        
        # Get configuration
        gear_level = self.config_data['gear_level']
        weapon_level = self.config_data['weapon_level']
        unique_count = self.config_data['unique_count']
        gem_assumption = self.config_data['gem_assumption']
        class_name = self.config_data['class_name']
        subclass_name = self.config_data['subclass_name']
        
        # Get stat values
        gear_stats = config_numerical.get_gear_level_stats(gear_level)
        primary = gear_stats['primary']
        secondary = gear_stats['secondary']
        reforge = gear_stats['reforge']
        
        weapon_value = config_numerical.get_weapon_stats(weapon_level)
        
        gem_values = {'min': 50, 'avg': 60, 'max': 70}
        gem_value = gem_values[gem_assumption]
        
        # Get unique stats for this subclass
        unique_stats = config_numerical.get_unique_stats(class_name, subclass_name)
        
        # Account for locked gear
        locked_count = self.locked_gear_manager.count() if self.locked_gear_manager else 0
        unlocked_slots = 10 - locked_count
        
        # Get stats from locked gear
        locked_stats = {stat: 0 for stat in config.ALL_STATS}
        locked_gems = 0
        locked_reforges = 0
        
        if self.locked_gear_manager and locked_count > 0:
            locked_stats = self.locked_gear_manager.get_total_stats(gear_level, unique_stats, gem_value)
            locked_gems, locked_reforges = self.locked_gear_manager.get_resource_usage()
        
        # Available resources
        available_gems = 11 - locked_gems
        available_reforges = 11 - locked_reforges
        
        # Calculate maximums for unique stats (can be on weapon + unique gear + regular gear main)
        regular_count = unlocked_slots - unique_count
        
        max_unique_stat = {
            unique_stats[0]: weapon_value + (unique_count * primary * 2) + (regular_count * primary) + (available_gems * gem_value) + (available_reforges * reforge),
            unique_stats[1]: weapon_value + (unique_count * primary * 2) + (regular_count * primary) + (available_gems * gem_value) + (available_reforges * reforge)
        }
        
        # Calculate maximums for non-unique stats (regular gear only: main + sub)
        max_other_stat = (unlocked_slots * primary) + (unlocked_slots * secondary) + (available_gems * gem_value) + (available_reforges * reforge)
        
        # Build output
        lines = []
        lines.append("=" * 60)
        lines.append("THEORETICAL MAXIMUM STATS")
        lines.append("=" * 60)
        lines.append("")
        lines.append("These are the absolute maximum values achievable with your")
        lines.append("current configuration, assuming optimal gear distribution.")
        lines.append("")
        
        if locked_count > 0:
            lines.append("--- FROM LOCKED GEAR ---")
            for stat in config.ALL_STATS:
                value = locked_stats.get(stat, 0)
                if value > 0:
                    lines.append(f"  {stat:12}: {value:5}")
            lines.append("")
        
        lines.append("--- MAXIMUM PER STAT (Including Locked Gear) ---")
        lines.append("")
        
        # Show unique stats first
        lines.append(f"▶ UNIQUE STATS (for {subclass_name}):")
        for stat in unique_stats:
            total_max = max_unique_stat[stat] + locked_stats.get(stat, 0)
            lines.append(f"  {stat:12}: {total_max:5,}")
        
        lines.append("")
        lines.append("▶ OTHER STATS:")
        for stat in config.ALL_STATS:
            if stat not in unique_stats:
                total_max = max_other_stat + locked_stats.get(stat, 0)
                lines.append(f"  {stat:12}: {total_max:5,}")
        
        lines.append("")
        lines.append("=" * 60)
        lines.append("BREAKDOWN (For Unlocked Slots)")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append(f"Weapon:           {weapon_value:5} × 2 unique stats = {weapon_value * 2:6}")
        lines.append(f"Unique Gear:      {primary:5} × 2 × {unique_count} pieces = {primary * 2 * unique_count:6}")
        lines.append(f"Regular Gear:     {primary:5} + {secondary:3} × {regular_count} pieces = {(primary + secondary) * regular_count:6}")
        lines.append(f"Available Gems:   {gem_value:5} × {available_gems} = {gem_value * available_gems:6}")
        lines.append(f"Available Reforge:{reforge:5} × {available_reforges} = {reforge * available_reforges:6}")
        
        lines.append("")
        lines.append("=" * 60)
        lines.append("NOTES")
        lines.append("=" * 60)
        lines.append("")
        lines.append("• Unique stats can appear on weapon, unique gear, AND regular gear")
        lines.append("• Non-unique stats can only appear on regular gear (main + sub)")
        lines.append("• You cannot achieve ALL stats at maximum simultaneously")
        lines.append("• These values assume perfect gear with no stat waste")
        lines.append("• Forbidden stats reduce actual achievable values")
        
        if locked_count > 0:
            lines.append(f"• {locked_count} slots locked, calculating for {unlocked_slots} remaining")
            lines.append(f"• {locked_gems} gems and {locked_reforges} reforges already used")
        
        self.stats_text.insert(1.0, '\n'.join(lines))
        self.stats_text.config(state='disabled')
    
    def show(self):
        """Show the dialog"""
        self.dialog.wait_window()


class LoadPresetDialog:
    """Dialog for loading a preset"""
    
    def __init__(self, parent, preset_manager):
        self.result = None
        self.preset_manager = preset_manager
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Load Preset")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Instructions
        ttk.Label(main_frame, text="Select a preset to load:",
                 font=('TkDefaultFont', 9)).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Preset list
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Treeview
        columns = ('Name', 'Created')
        self.preset_tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                       height=12, selectmode='browse')
        
        self.preset_tree.heading('Name', text='Preset Name')
        self.preset_tree.heading('Created', text='Created')
        
        self.preset_tree.column('Name', width=250)
        self.preset_tree.column('Created', width=180)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                 command=self.preset_tree.yview)
        self.preset_tree.configure(yscrollcommand=scrollbar.set)
        
        self.preset_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Populate list
        self.refresh_list()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(10, 0))
        
        ttk.Button(button_frame, text="Load", command=self.load).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # Double-click to load
        self.preset_tree.bind('<Double-Button-1>', lambda e: self.load())
        
        # Center
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def refresh_list(self):
        """Refresh the preset list"""
        # Clear existing
        for item in self.preset_tree.get_children():
            self.preset_tree.delete(item)
        
        # Add presets
        presets = self.preset_manager.list_presets()
        
        if not presets:
            self.preset_tree.insert('', tk.END, values=("No presets found", ""))
            return
        
        for filename, name, created in presets:
            # Format date
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(created)
                created_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                created_str = created
            
            self.preset_tree.insert('', tk.END, values=(name, created_str),
                                   tags=(filename,))
    
    def load(self):
        selection = self.preset_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a preset to load", parent=self.dialog)
            return
        
        # Get filename from tags
        item = selection[0]
        tags = self.preset_tree.item(item, 'tags')
        
        if not tags or tags[0] == '':
            messagebox.showinfo("Info", "No presets available", parent=self.dialog)
            return
        
        filename = tags[0]
        self.result = filename
        self.dialog.destroy()
    
    def delete(self):
        selection = self.preset_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a preset to delete", parent=self.dialog)
            return
        
        item = selection[0]
        values = self.preset_tree.item(item, 'values')
        tags = self.preset_tree.item(item, 'tags')
        
        if not tags or tags[0] == '':
            return
        
        name = values[0]
        filename = tags[0]
        
        if messagebox.askyesno("Confirm Delete", f"Delete preset '{name}'?", parent=self.dialog):
            success, msg = self.preset_manager.delete_preset(filename)
            if success:
                self.refresh_list()
                messagebox.showinfo("Success", "Preset deleted", parent=self.dialog)
            else:
                messagebox.showerror("Error", msg, parent=self.dialog)
    
    def cancel(self):
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        self.dialog.wait_window()
        return self.result