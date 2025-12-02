"""
calculator_v2.py
Core calculation engine for RPG Gear Set Calculator
Now supports locked gear integration
"""

from itertools import combinations
import config
import config_numerical


class GearCalculator:
    def __init__(self, class_name, subclass_name, gear_level, weapon_level, 
                 unique_count, gem_assumption, min_stats, locked_gear_manager=None):
        """
        Initialize the gear calculator
        
        Args:
            class_name: Character class
            subclass_name: Character subclass
            gear_level: Gear level (40, 60, 80)
            weapon_level: Weapon level (70, 90)
            unique_count: Number of unique gear pieces (0-6)
            gem_assumption: Gem value ('min'=50, 'avg'=60, 'max'=70)
            min_stats: Dict of minimum stat requirements
            locked_gear_manager: LockedGearManager instance (optional)
        """
        self.class_name = class_name
        self.subclass_name = subclass_name
        self.gear_level = gear_level
        self.weapon_level = weapon_level
        self.unique_count = unique_count
        self.min_stats = min_stats
        self.locked_gear_manager = locked_gear_manager
        
        # Validate inputs
        if not config.validate_class_subclass(class_name, subclass_name):
            raise ValueError(f"Invalid class/subclass: {class_name}/{subclass_name}")
        
        # Get attribute for forbidden stats
        self.attribute = config.CLASS_ATTRIBUTES[class_name]
        
        # Get gear stats
        gear_stats = config_numerical.get_gear_level_stats(gear_level)
        self.primary_value = gear_stats['primary']
        self.secondary_value = gear_stats['secondary']
        self.reforge_value = gear_stats['reforge']
        
        # Get weapon stats
        self.weapon_stat_value = config_numerical.get_weapon_stats(weapon_level)
        
        # Get unique stats for this subclass
        self.unique_stats = config_numerical.get_unique_stats(class_name, subclass_name)
        
        # Gem value based on assumption
        gem_values = {'min': 50, 'avg': 60, 'max': 70}
        self.gem_value = gem_values.get(gem_assumption, 60)
        
        # Handle locked gear
        self.has_locked_gear = locked_gear_manager is not None and locked_gear_manager.count() > 0
        
        if self.has_locked_gear:
            # Get stats from locked gear (including weapon if locked)
            self.locked_stats = locked_gear_manager.get_total_stats(
                gear_level, self.unique_stats, self.gem_value
            )
            
            # Get locked slots
            self.locked_slots = set(locked_gear_manager.get_locked_slots())
            
            # Get available resources
            self.total_gems, self.total_reforges = locked_gear_manager.get_available_resources()
            
            # Calculate how many gear slots we still need to fill
            self.slots_to_fill = 10 - len(self.locked_slots)
            
            # Adjust unique count if needed (can't exceed available slots that support unique)
            available_unique_slots = [s for s in config.UNIQUE_ALLOWED_SLOTS 
                                     if s not in self.locked_slots]
            # Count unique pieces in locked gear
            locked_unique_count = sum(1 for piece in locked_gear_manager.locked_pieces 
                                     if piece.is_unique)
            self.unique_count = min(unique_count, len(available_unique_slots))
            self.total_unique_in_build = locked_unique_count + self.unique_count
            
        else:
            # No locked gear - use defaults
            self.locked_stats = {stat: 0 for stat in config.ALL_STATS}
            self.locked_slots = set()
            self.total_gems = 11
            self.total_reforges = 11
            self.slots_to_fill = 10
            self.total_unique_in_build = unique_count
        
        self.solutions = []
    
    def get_optional_slot_combinations(self):
        """Get all ways to choose optional slots (excluding locked slots)"""
        # Get available optional slots (not locked)
        available_optional = [s for s in config.OPTIONAL_SLOTS if s not in self.locked_slots]
        
        # Get available mandatory slots (not locked)
        available_mandatory = [s for s in config.MANDATORY_SLOTS if s not in self.locked_slots]
        
        # We need to choose enough optional slots to fill remaining gear
        # Total slots needed = 10 - locked_count
        # Mandatory available = available_mandatory
        # Optional needed = total_needed - mandatory_available
        
        slots_needed = self.slots_to_fill
        mandatory_count = len(available_mandatory)
        optional_needed = slots_needed - mandatory_count
        
        if optional_needed < 0:
            # More mandatory slots available than needed (shouldn't happen)
            optional_needed = 0
        
        if optional_needed > len(available_optional):
            # Not enough optional slots available
            return []
        
        # Generate combinations
        if optional_needed == 0:
            return [available_mandatory]
        
        optional_combos = [list(combo) for combo in combinations(available_optional, optional_needed)]
        
        # Combine with mandatory slots
        result = [available_mandatory + optional for optional in optional_combos]
        
        return result
    
    def get_unique_slot_assignments(self, slots):
        """
        Get all ways to assign unique gear to slots (excluding locked slots)
        
        Args:
            slots: List of unlocked slots being used
            
        Returns:
            List of lists, each containing slots that should be unique
        """
        # Filter to only slots that can be unique and aren't locked
        valid_unique_slots = [s for s in slots if s in config.UNIQUE_ALLOWED_SLOTS]
        
        # Generate all combinations of choosing 'unique_count' slots
        if self.unique_count == 0:
            return [[]]
        
        if self.unique_count > len(valid_unique_slots):
            return []
        
        return [list(combo) for combo in combinations(valid_unique_slots, self.unique_count)]
    
    def enumerate_gear_stats(self, slots, unique_slots):
        """
        Recursively enumerate all valid stat assignments for gear
        
        Args:
            slots: List of unlocked gear slots
            unique_slots: List of unlocked slots that have unique gear
            
        Yields:
            Dictionary mapping slot -> (stat1, stat2, is_unique)
        """
        def recurse(index, current_assignment):
            if index == len(slots):
                yield current_assignment.copy()
                return
            
            slot = slots[index]
            is_unique = slot in unique_slots
            
            if is_unique:
                # Unique gear: both stats are the subclass unique stats
                assignment = (self.unique_stats[0], self.unique_stats[1], True)
                current_assignment[slot] = assignment
                yield from recurse(index + 1, current_assignment)
            else:
                # Regular gear: try all valid main/sub combinations
                valid_stats = config.get_valid_stats_for_slot(slot, self.attribute)
                
                for main_stat in valid_stats:
                    for sub_stat in valid_stats:
                        if main_stat != sub_stat:
                            assignment = (main_stat, sub_stat, False)
                            current_assignment[slot] = assignment
                            yield from recurse(index + 1, current_assignment)
        
        yield from recurse(0, {})
    
    def calculate_gear_totals(self, gear_assignment):
        """
        Calculate total stats from gear (including locked gear and weapon)
        
        Args:
            gear_assignment: Dict mapping unlocked slot -> (stat1, stat2, is_unique)
            
        Returns:
            Dict mapping stat -> total value from all gear
        """
        totals = {stat: 0 for stat in config.ALL_STATS}
        
        # Start with locked gear stats (includes weapon if locked)
        for stat, value in self.locked_stats.items():
            totals[stat] += value
        
        # Add weapon stats if not locked
        if "Weapon" not in self.locked_slots:
            totals[self.unique_stats[0]] += self.weapon_stat_value
            totals[self.unique_stats[1]] += self.weapon_stat_value
        
        # Add unlocked gear stats
        for slot, (stat1, stat2, is_unique) in gear_assignment.items():
            if is_unique:
                totals[stat1] += self.primary_value
                totals[stat2] += self.primary_value
            else:
                totals[stat1] += self.primary_value
                totals[stat2] += self.secondary_value
        
        return totals
    
    def assign_gems_and_reforges(self, gear_totals):
        """
        Optimally assign gems and reforges to meet minimum requirements
        Uses only remaining/available resources
        
        Args:
            gear_totals: Current stat totals from gear
            
        Returns:
            (gem_counts, reforge_counts, final_totals, meets_requirements)
            or None if requirements cannot be met
        """
        # Calculate what we still need
        needed = {}
        for stat, min_val in self.min_stats.items():
            current = gear_totals.get(stat, 0)
            if current < min_val:
                needed[stat] = min_val - current
        
        if not needed:
            # Already meet all requirements
            return ({}, {}, gear_totals.copy(), True)
        
        # Assign gems first (more valuable)
        gem_counts = {}
        remaining_gems = self.total_gems
        
        for stat in sorted(needed.keys(), key=lambda s: needed[s], reverse=True):
            gems_needed = (needed[stat] + self.gem_value - 1) // self.gem_value
            gems_to_use = min(gems_needed, remaining_gems)
            
            if gems_to_use > 0:
                gem_counts[stat] = gems_to_use
                needed[stat] -= gems_to_use * self.gem_value
                remaining_gems -= gems_to_use
                
                if needed[stat] <= 0:
                    del needed[stat]
        
        # Assign reforges for remaining needs
        reforge_counts = {}
        remaining_reforges = self.total_reforges
        
        for stat in sorted(needed.keys(), key=lambda s: needed[s], reverse=True):
            reforges_needed = (needed[stat] + self.reforge_value - 1) // self.reforge_value
            reforges_to_use = min(reforges_needed, remaining_reforges)
            
            if reforges_to_use > 0:
                reforge_counts[stat] = reforges_to_use
                needed[stat] -= reforges_to_use * self.reforge_value
                remaining_reforges -= reforges_to_use
                
                if needed[stat] <= 0:
                    del needed[stat]
        
        # Check if we still have unmet needs
        if needed:
            return None
        
        # Calculate final totals
        final_totals = gear_totals.copy()
        for stat, count in gem_counts.items():
            final_totals[stat] = final_totals.get(stat, 0) + count * self.gem_value
        for stat, count in reforge_counts.items():
            final_totals[stat] = final_totals.get(stat, 0) + count * self.reforge_value
        
        # Verify all requirements met
        meets_requirements = all(
            final_totals.get(stat, 0) >= min_val 
            for stat, min_val in self.min_stats.items()
        )
        
        return (gem_counts, reforge_counts, final_totals, meets_requirements)
    
    def calculate(self, max_solutions=None):
        """
        Main calculation method - finds all valid solutions
        
        Args:
            max_solutions: Optional limit on number of solutions to find
            
        Returns:
            List of solution dictionaries
        """
        self.solutions = []
        solutions_found = 0
        
        # If all slots are locked, just validate
        if self.has_locked_gear and len(self.locked_slots) >= 10:
            return self._validate_fully_locked_build()
        
        # Get all slot combinations
        slot_combinations = self.get_optional_slot_combinations()
        
        if not slot_combinations:
            # No valid slot combinations
            return []
        
        for slot_combo in slot_combinations:
            # Get all ways to assign unique gear
            unique_assignments = self.get_unique_slot_assignments(slot_combo)
            
            for unique_slots in unique_assignments:
                # Enumerate all stat combinations
                for gear_assignment in self.enumerate_gear_stats(slot_combo, unique_slots):
                    # Calculate totals from gear
                    gear_totals = self.calculate_gear_totals(gear_assignment)
                    
                    # Try to assign gems and reforges
                    result = self.assign_gems_and_reforges(gear_totals)
                    
                    if result and result[3]:
                        gem_counts, reforge_counts, final_totals, _ = result
                        
                        # Combine locked and unlocked slots for solution
                        all_slots = list(self.locked_slots) + slot_combo
                        
                        solution = {
                            'slots': all_slots,
                            'unique_slots': unique_slots,
                            'gear_assignment': gear_assignment,
                            'gem_counts': gem_counts,
                            'reforge_counts': reforge_counts,
                            'final_totals': final_totals,
                            'gear_totals': gear_totals,
                            'has_locked_gear': self.has_locked_gear
                        }
                        
                        self.solutions.append(solution)
                        solutions_found += 1
                        
                        if max_solutions and solutions_found >= max_solutions:
                            return self.solutions
        
        return self.solutions
    
    def _validate_fully_locked_build(self):
        """Validate a build where all 10 slots are locked"""
        gear_totals = self.locked_stats.copy()
        
        result = self.assign_gems_and_reforges(gear_totals)
        
        if result and result[3]:
            gem_counts, reforge_counts, final_totals, _ = result
            
            solution = {
                'slots': list(self.locked_slots),
                'unique_slots': [],
                'gear_assignment': {},
                'gem_counts': gem_counts,
                'reforge_counts': reforge_counts,
                'final_totals': final_totals,
                'gear_totals': gear_totals,
                'has_locked_gear': True,
                'fully_locked': True
            }
            
            return [solution]
        
        return []
    
    def format_solution(self, solution, solution_number=None):
        """Format a solution for display"""
        lines = []
        
        if solution_number:
            lines.append(f"\n{'='*60}")
            lines.append(f"SOLUTION #{solution_number}")
            lines.append(f"{'='*60}")
        
        # Slots used
        lines.append(f"\nSlots Used: {', '.join(solution['slots'])}")
        
        # Show locked gear section if applicable
        if self.has_locked_gear and self.locked_gear_manager:
            lines.append(f"\n--- LOCKED GEAR (Your Equipment) ---")
            for piece in self.locked_gear_manager.locked_pieces:
                stat_str = f"{piece.main_stat} ({self.primary_value}) + {piece.sub_stat} ({self.primary_value})" if piece.is_unique else f"{piece.main_stat} ({self.primary_value}) + {piece.sub_stat} ({self.secondary_value})"
                extras = []
                if piece.gem_stat:
                    extras.append(f"{piece.gem_stat} gem (+{self.gem_value})")
                if piece.reforge_stat:
                    extras.append(f"{piece.reforge_stat} reforge (+{self.reforge_value})")
                extras_str = ", " + ", ".join(extras) if extras else ""
                gear_type = "UNIQUE" if piece.is_unique else "REGULAR"
                lines.append(f"  {piece.slot:15} [{gear_type}]: {stat_str}{extras_str}")
        
        # Gear breakdown (unlocked gear only)
        if solution.get('gear_assignment'):
            lines.append(f"\n--- CALCULATED GEAR (Remaining Slots) ---")
            for slot in solution['slots']:
                if slot in self.locked_slots:
                    continue
                
                stat1, stat2, is_unique = solution['gear_assignment'][slot]
                if is_unique:
                    lines.append(f"  {slot:15} [UNIQUE]: {stat1} ({self.primary_value}) + {stat2} ({self.primary_value})")
                else:
                    lines.append(f"  {slot:15} [REGULAR]: {stat1} ({self.primary_value}) + {stat2} ({self.secondary_value})")
        
        # Weapon
        if "Weapon" not in self.locked_slots:
            lines.append(f"\n--- WEAPON ---")
            lines.append(f"  {'Weapon':15} [UNIQUE]: {self.unique_stats[0]} ({self.weapon_stat_value}) + {self.unique_stats[1]} ({self.weapon_stat_value})")
        
        # Gems
        total_gems_used = sum(solution['gem_counts'].values())
        lines.append(f"\n--- GEMS ({total_gems_used}/{self.total_gems} available used) ---")
        if solution['gem_counts']:
            for stat, count in sorted(solution['gem_counts'].items()):
                lines.append(f"  {stat}: {count} gems (+{count * self.gem_value})")
        else:
            lines.append("  None needed")
        
        # Reforges
        total_reforges_used = sum(solution['reforge_counts'].values())
        lines.append(f"\n--- REFORGES ({total_reforges_used}/{self.total_reforges} available used) ---")
        if solution['reforge_counts']:
            for stat, count in sorted(solution['reforge_counts'].items()):
                lines.append(f"  {stat}: {count} reforges (+{count * self.reforge_value})")
        else:
            lines.append("  None needed")
        
        # Final totals
        lines.append(f"\n--- FINAL STATS ---")
        for stat in config.ALL_STATS:
            total = solution['final_totals'].get(stat, 0)
            required = self.min_stats.get(stat, 0)
            status = "✓" if total >= required else "✗"
            lines.append(f"  {stat:12}: {total:4} {status} (required: {required})")
        
        return '\n'.join(lines)


def test_calculator():
    """Test the calculator with a sample configuration"""
    print("Testing RPG Gear Calculator...")
    print("="*60)
    
    # Test configuration
    calc = GearCalculator(
        class_name="Stormblade",
        subclass_name="Iaido",
        gear_level=80,
        weapon_level=90,
        unique_count=6,
        gem_assumption='avg',
        min_stats={
            'Crit': 2000,
            'Haste': 600,
            'Mastery': 900
        }
    )
    
    print(f"Class: {calc.class_name} - {calc.subclass_name}")
    print(f"Gear Level: {calc.gear_level}, Weapon Level: {calc.weapon_level}")
    print(f"Unique Pieces: {calc.unique_count}")
    print(f"Gem Value: {calc.gem_value}")
    print(f"\nMinimum Requirements:")
    for stat, val in calc.min_stats.items():
        print(f"  {stat}: {val}")
    
    print(f"\nSearching for solutions (finding first 5)...")
    solutions = calc.calculate(max_solutions=5)
    
    print(f"\nFound {len(solutions)} solutions!")
    
    if solutions:
        print(calc.format_solution(solutions[0], 1))


if __name__ == "__main__":
    test_calculator()