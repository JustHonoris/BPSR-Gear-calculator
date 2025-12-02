"""
locked_gear_manager.py
Manages locked gear pieces and calculates their contribution to stats
"""

import config
import config_numerical


class LockedGear:
    """Represents a single locked gear piece"""
    
    def __init__(self, slot, is_unique, main_stat=None, sub_stat=None, 
                 gem_stat=None, reforge_stat=None):
        """
        Initialize a locked gear piece
        
        Args:
            slot: Slot name (e.g., "Helmet", "Ring")
            is_unique: Boolean - is this unique gear?
            main_stat: Main stat (required for regular gear)
            sub_stat: Sub stat (required for regular gear)
            gem_stat: Gem stat (optional)
            reforge_stat: Reforge stat (optional)
        """
        self.slot = slot
        self.is_unique = is_unique
        self.main_stat = main_stat
        self.sub_stat = sub_stat
        self.gem_stat = gem_stat
        self.reforge_stat = reforge_stat
    
    def get_stats(self, gear_level, unique_stats, gem_value, reforge_value):
        """
        Calculate stat contributions from this gear piece
        
        Args:
            gear_level: Gear level (40, 60, 80)
            unique_stats: List of 2 stats for unique gear [stat1, stat2]
            gem_value: Value per gem
            reforge_value: Value per reforge
            
        Returns:
            Dictionary mapping stat -> value
        """
        stats = {stat: 0 for stat in config.ALL_STATS}
        
        gear_stats = config_numerical.get_gear_level_stats(gear_level)
        
        if self.is_unique:
            # Unique gear: both stats are primary value
            stats[unique_stats[0]] += gear_stats['primary']
            stats[unique_stats[1]] += gear_stats['primary']
        else:
            # Regular gear: main is primary, sub is secondary
            if self.main_stat:
                stats[self.main_stat] += gear_stats['primary']
            if self.sub_stat:
                stats[self.sub_stat] += gear_stats['secondary']
        
        # Add gem contribution
        if self.gem_stat:
            stats[self.gem_stat] += gem_value
        
        # Add reforge contribution
        if self.reforge_stat:
            stats[self.reforge_stat] += reforge_value
        
        return stats
    
    def validate(self, attribute, unique_stats=None):
        """
        Validate this gear piece
        
        Args:
            attribute: Class attribute (Strength/Agility/Intellect)
            unique_stats: Required for unique gear - [stat1, stat2]
            
        Returns:
            (is_valid, error_message)
        """
        # Check if unique gear has correct stats
        if self.is_unique:
            if not unique_stats:
                return False, "Unique stats not provided for validation"
            # For unique gear, main and sub should match unique stats
            # (Though we auto-set these, so this is a sanity check)
        
        # Check regular gear
        if not self.is_unique:
            if not self.main_stat or not self.sub_stat:
                return False, f"Regular gear must have both main and sub stats"
            
            if self.main_stat == self.sub_stat:
                return False, f"Main stat cannot equal sub stat"
            
            # Check forbidden stats
            forbidden = config.get_forbidden_stat(self.slot, attribute)
            if forbidden:
                if self.main_stat == forbidden:
                    return False, f"{forbidden} is forbidden on {self.slot} for {attribute} classes"
                if self.sub_stat == forbidden:
                    return False, f"{forbidden} is forbidden on {self.slot} for {attribute} classes"
        
        return True, "Valid"
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'slot': self.slot,
            'is_unique': self.is_unique,
            'main_stat': self.main_stat,
            'sub_stat': self.sub_stat,
            'gem_stat': self.gem_stat,
            'reforge_stat': self.reforge_stat
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        return cls(
            slot=data['slot'],
            is_unique=data['is_unique'],
            main_stat=data.get('main_stat'),
            sub_stat=data.get('sub_stat'),
            gem_stat=data.get('gem_stat'),
            reforge_stat=data.get('reforge_stat')
        )
    
    def __str__(self):
        """String representation"""
        if self.is_unique:
            stats_str = f"{self.main_stat}+{self.sub_stat}"
        else:
            stats_str = f"{self.main_stat} (main) + {self.sub_stat} (sub)"
        
        extras = []
        if self.gem_stat:
            extras.append(f"{self.gem_stat} gem")
        if self.reforge_stat:
            extras.append(f"{self.reforge_stat} reforge")
        
        extras_str = ", " + ", ".join(extras) if extras else ""
        
        gear_type = "UNIQUE" if self.is_unique else "REGULAR"
        return f"{self.slot} ({gear_type}): {stats_str}{extras_str}"


class LockedGearManager:
    """Manages collection of locked gear pieces"""
    
    def __init__(self):
        self.locked_pieces = []
    
    def add_gear(self, gear):
        """
        Add a locked gear piece
        
        Args:
            gear: LockedGear instance
            
        Returns:
            (success, message)
        """
        # Check if slot already locked
        if any(piece.slot == gear.slot for piece in self.locked_pieces):
            return False, f"{gear.slot} is already locked. Remove it first."
        
        # Check total count
        if len(self.locked_pieces) >= 10:
            return False, "Cannot lock more than 10 gear pieces"
        
        self.locked_pieces.append(gear)
        return True, f"Added {gear.slot}"
    
    def remove_gear(self, slot):
        """Remove locked gear by slot name"""
        self.locked_pieces = [piece for piece in self.locked_pieces if piece.slot != slot]
    
    def get_gear(self, slot):
        """Get locked gear by slot name"""
        for piece in self.locked_pieces:
            if piece.slot == slot:
                return piece
        return None
    
    def clear_all(self):
        """Remove all locked gear"""
        self.locked_pieces = []
    
    def get_locked_slots(self):
        """Get list of locked slot names"""
        return [piece.slot for piece in self.locked_pieces]
    
    def get_total_stats(self, gear_level, unique_stats, gem_value):
        """
        Calculate total stats from all locked gear
        
        Args:
            gear_level: Gear level
            unique_stats: List of 2 unique stats for this subclass
            gem_value: Value per gem
            
        Returns:
            Dictionary mapping stat -> total value
        """
        totals = {stat: 0 for stat in config.ALL_STATS}
        
        gear_stats = config_numerical.get_gear_level_stats(gear_level)
        reforge_value = gear_stats['reforge']
        
        for piece in self.locked_pieces:
            piece_stats = piece.get_stats(gear_level, unique_stats, gem_value, reforge_value)
            for stat, value in piece_stats.items():
                totals[stat] += value
        
        return totals
    
    def get_resource_usage(self):
        """
        Calculate how many gems and reforges are used by locked gear
        
        Returns:
            (gems_used, reforges_used)
        """
        gems_used = sum(1 for piece in self.locked_pieces if piece.gem_stat)
        reforges_used = sum(1 for piece in self.locked_pieces if piece.reforge_stat)
        return gems_used, reforges_used
    
    def get_available_resources(self):
        """
        Calculate remaining gems and reforges available
        
        Returns:
            (gems_available, reforges_available)
        """
        gems_used, reforges_used = self.get_resource_usage()
        # 10 gear pieces + 1 weapon = 11 total
        # But locked pieces consume some
        locked_count = len(self.locked_pieces)
        
        # Available = total slots - locked slots
        # Each slot can have a gem and reforge
        gems_available = 11 - gems_used
        reforges_available = 11 - reforges_used
        
        return gems_available, reforges_available
    
    def validate_all(self, attribute, unique_stats):
        """
        Validate all locked gear
        
        Args:
            attribute: Class attribute
            unique_stats: Unique stats for subclass
            
        Returns:
            List of (slot, error_message) for invalid pieces
        """
        errors = []
        for piece in self.locked_pieces:
            valid, message = piece.validate(attribute, unique_stats)
            if not valid:
                errors.append((piece.slot, message))
        return errors
    
    def count(self):
        """Get number of locked pieces"""
        return len(self.locked_pieces)
    
    def is_slot_locked(self, slot):
        """Check if a specific slot is locked"""
        return any(piece.slot == slot for piece in self.locked_pieces)
    
    def get_summary(self):
        """Get a summary of locked gear"""
        if not self.locked_pieces:
            return "No locked gear"
        
        lines = [f"Locked Gear ({len(self.locked_pieces)}/10):"]
        for piece in self.locked_pieces:
            lines.append(f"  • {piece}")
        
        gems_used, reforges_used = self.get_resource_usage()
        lines.append(f"\nResources Used:")
        lines.append(f"  Gems: {gems_used}/11")
        lines.append(f"  Reforges: {reforges_used}/11")
        
        return "\n".join(lines)
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'locked_pieces': [piece.to_dict() for piece in self.locked_pieces]
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        manager = cls()
        for piece_data in data.get('locked_pieces', []):
            manager.locked_pieces.append(LockedGear.from_dict(piece_data))
        return manager


# Test
if __name__ == "__main__":
    print("Testing LockedGearManager...")
    
    manager = LockedGearManager()
    
    # Add a unique helmet
    helmet = LockedGear(
        slot="Helmet",
        is_unique=True,
        main_stat="Crit",
        sub_stat="Mastery",
        gem_stat="Haste",
        reforge_stat="Crit"
    )
    
    success, msg = manager.add_gear(helmet)
    print(f"\nAdd helmet: {success} - {msg}")
    
    # Add a regular ring
    ring = LockedGear(
        slot="Ring",
        is_unique=False,
        main_stat="Versatility",
        sub_stat="Luck",
        gem_stat="Mastery"
    )
    
    success, msg = manager.add_gear(ring)
    print(f"Add ring: {success} - {msg}")
    
    # Print summary
    print(f"\n{manager.get_summary()}")
    
    # Calculate stats
    unique_stats = ["Crit", "Mastery"]
    stats = manager.get_total_stats(gear_level=80, unique_stats=unique_stats, gem_value=60)
    print(f"\nTotal stats from locked gear:")
    for stat, value in stats.items():
        if value > 0:
            print(f"  {stat}: {value}")
    
    # Check resources
    gems_avail, reforges_avail = manager.get_available_resources()
    print(f"\nAvailable resources:")
    print(f"  Gems: {gems_avail}/11")
    print(f"  Reforges: {reforges_avail}/11")
    
    print("\n✅ LockedGearManager test complete!")
