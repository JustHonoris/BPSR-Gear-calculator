"""
config_numerical.py
Configuration for numerical stat calculations including gear levels,
unique sets, gems, and reforge stats
"""

# Gear level stat values
GEAR_LEVELS = {
    40: {
        'primary': 100,
        'secondary': 50,
        'reforge': 30
    },
    60: {
        'primary': 140,
        'secondary': 70,
        'reforge': 42
    },
    80: {
        'primary': 200,
        'secondary': 100,
        'reforge': 60
    }
}

# Available gear levels
AVAILABLE_GEAR_LEVELS = [40, 60, 80]

# Levels that support unique sets (2 primary stats instead of 1 primary + 1 secondary)
UNIQUE_SET_LEVELS = [60, 80]

# Weapon stat values (always unique, has 2 stats matching subclass)
WEAPON_LEVELS = {
    70: {
        'stat_value': 306  # Each of the 2 stats gets this value
    },
    90: {
        'stat_value': 384  # Each of the 2 stats gets this value
    }
}

# Available weapon levels
AVAILABLE_WEAPON_LEVELS = [70, 90]

# Gem configuration
GEM_STAT_VALUE = 50  # Each gem gives +50 to a stat
MAX_GEMS = 11  # Maximum number of gems a player can have
TOTAL_GEM_VALUE = GEM_STAT_VALUE * MAX_GEMS  # 550 total from gems

# Gear piece counts
TOTAL_GEAR_PIECES = 10  # Total gear pieces (not including weapon)
MAX_UNIQUE_GEAR_PIECES = 6  # Maximum unique gear pieces (excluding weapon)
WEAPON_SLOT = 1  # Weapon is a separate slot (always unique)

# Slots that CANNOT be unique (must always be regular gear)
UNIQUE_FORBIDDEN_SLOTS = ['Charm', 'Earrings', 'Ring', 'Necklace']

# Slots that CAN be unique
UNIQUE_ALLOWED_SLOTS = ['Helmet', 'Armor', 'Gauntlets', 'Boots', 'Bracelet (L)', 'Bracelet (R)']

# Subclass unique set configurations
# Format: {class_name: {subclass_name: [stat1, stat2]}}
SUBCLASS_UNIQUE_STATS = {
    'Stormblade': {
        'Iaido': ['Crit', 'Mastery'],
        'Moonstrike': ['Luck', 'Haste']
    },
    'Frost Mage': {
        'Icicle': ['Crit', 'Luck'],
        'Frost Beam': ['Haste', 'Mastery']
    },
    'Wind Knight': {
        'Skyward': ['Crit', 'Luck'],
        'Vanguard': ['Haste', 'Mastery']
    },
    'Verdant Oracle': {
        'Smite': ['Mastery', 'Luck'],
        'Lifebind': ['Mastery', 'Haste']
    },
    'Heavy Guardian': {
        'Block': ['Mastery', 'Luck'],
        'Earthfort': ['Mastery', 'Versatility']
    },
    'Marksman': {
        'Falconry': ['Crit', 'Haste'],
        'Wildpack': ['Haste', 'Mastery']
    },
    'Shield Knight': {
        'Shield': ['Haste', 'Mastery'],
        'Recovery': ['Crit', 'Mastery']
    },
    'Beat Performer': {
        'Dissonance': ['Haste', 'Luck'],
        'Concerto': ['Crit', 'Haste']
    }
}


def get_gear_level_stats(level):
    """
    Get stat values for a specific gear level
    
    Args:
        level: Gear level (40, 60, or 80)
        
    Returns:
        Dictionary with primary, secondary, and reforge values
    """
    if level not in GEAR_LEVELS:
        raise ValueError(f"Invalid gear level: {level}. Must be one of {AVAILABLE_GEAR_LEVELS}")
    return GEAR_LEVELS[level]


def get_subclasses(class_name):
    """
    Get available subclasses for a class
    
    Args:
        class_name: Name of the class
        
    Returns:
        List of subclass names
    """
    if class_name not in SUBCLASS_UNIQUE_STATS:
        return []
    return list(SUBCLASS_UNIQUE_STATS[class_name].keys())


def get_unique_stats(class_name, subclass_name):
    """
    Get the unique set stats for a class/subclass combination
    
    Args:
        class_name: Name of the class
        subclass_name: Name of the subclass
        
    Returns:
        List of two stats [stat1, stat2]
    """
    if class_name not in SUBCLASS_UNIQUE_STATS:
        raise ValueError(f"Unknown class: {class_name}")
    
    if subclass_name not in SUBCLASS_UNIQUE_STATS[class_name]:
        raise ValueError(f"Unknown subclass {subclass_name} for class {class_name}")
    
    return SUBCLASS_UNIQUE_STATS[class_name][subclass_name]


def get_weapon_stats(weapon_level):
    """
    Get stat value for a specific weapon level
    
    Args:
        weapon_level: Weapon level (70 or 90)
        
    Returns:
        Stat value for each of the 2 stats
    """
    if weapon_level not in WEAPON_LEVELS:
        raise ValueError(f"Invalid weapon level: {weapon_level}. Must be one of {AVAILABLE_WEAPON_LEVELS}")
    return WEAPON_LEVELS[weapon_level]['stat_value']


def can_slot_be_unique(slot):
    """
    Check if a slot can be unique gear
    
    Args:
        slot: Slot name
        
    Returns:
        Boolean - True if slot can be unique
    """
    return slot in UNIQUE_ALLOWED_SLOTS


def validate_unique_gear_count(unique_count):
    """
    Validate that unique gear count is within limits
    
    Args:
        unique_count: Number of unique gear pieces (excluding weapon)
        
    Returns:
        Boolean - True if valid
    """
    return 0 <= unique_count <= MAX_UNIQUE_GEAR_PIECES


def calculate_max_stat_from_gear(level, unique_count):
    """
    Calculate maximum possible value for a single stat from gear pieces
    
    Args:
        level: Gear level (40, 60, 80)
        unique_count: Number of unique gear pieces (0-6)
        
    Returns:
        Maximum stat value from gear alone
    """
    stats = get_gear_level_stats(level)
    regular_count = TOTAL_GEAR_PIECES - unique_count
    
    # Unique pieces: 2 primary stats each
    unique_contribution = unique_count * stats['primary'] * 2
    
    # Regular pieces: 1 primary + 1 secondary each
    regular_contribution = regular_count * (stats['primary'] + stats['secondary'])
    
    return unique_contribution + regular_contribution


def calculate_max_reforge_total(level):
    """
    Calculate total reforge stats available for all gear pieces
    
    Args:
        level: Gear level
        
    Returns:
        Total reforge stat value
    """
    stats = get_gear_level_stats(level)
    return stats['reforge'] * TOTAL_GEAR_PIECES


def get_stat_sources_breakdown(level, unique_count, weapon_level=None):
    """
    Get a breakdown of all stat sources
    
    Args:
        level: Gear level
        unique_count: Number of unique gear pieces (0-6)
        weapon_level: Weapon level (70 or 90), optional
        
    Returns:
        Dictionary with breakdown of stat sources
    """
    stats = get_gear_level_stats(level)
    regular_count = TOTAL_GEAR_PIECES - unique_count
    
    breakdown = {
        'level': level,
        'unique_count': unique_count,
        'regular_count': regular_count,
        'weapon_level': weapon_level,
        'per_piece': {
            'unique_primary': stats['primary'],
            'regular_primary': stats['primary'],
            'regular_secondary': stats['secondary'],
            'reforge': stats['reforge']
        },
        'total_gear_pieces': TOTAL_GEAR_PIECES,
        'max_unique_pieces': MAX_UNIQUE_GEAR_PIECES,
        'max_from_gear': calculate_max_stat_from_gear(level, unique_count),
        'total_reforge': calculate_max_reforge_total(level),
        'gems': {
            'per_gem': GEM_STAT_VALUE,
            'max_gems': MAX_GEMS,
            'total_from_gems': TOTAL_GEM_VALUE
        }
    }
    
    if weapon_level:
        weapon_value = get_weapon_stats(weapon_level)
        breakdown['weapon'] = {
            'level': weapon_level,
            'stat_value': weapon_value,
            'total_from_weapon': weapon_value * 2  # 2 stats
        }
    
    return breakdown


# Validation functions
def validate_gear_level(level):
    """Validate that a gear level is valid"""
    return level in AVAILABLE_GEAR_LEVELS


def validate_weapon_level(level):
    """Validate that a weapon level is valid"""
    return level in AVAILABLE_WEAPON_LEVELS


def validate_class_subclass(class_name, subclass_name):
    """Validate that a class/subclass combination is valid"""
    if class_name not in SUBCLASS_UNIQUE_STATS:
        return False, f"Unknown class: {class_name}"
    
    if subclass_name not in SUBCLASS_UNIQUE_STATS[class_name]:
        return False, f"Unknown subclass: {subclass_name}"
    
    return True, "Valid"


def can_use_unique_set(level):
    """
    Check if a gear level supports unique sets
    
    Args:
        level: Gear level
        
    Returns:
        Boolean - True if unique sets are available at this level
    """
    return level in UNIQUE_SET_LEVELS


# Test function
if __name__ == "__main__":
    print("Testing config_numerical.py...")
    print("\n=== Gear Level Stats ===")
    for level in AVAILABLE_GEAR_LEVELS:
        stats = get_gear_level_stats(level)
        print(f"Level {level}: Primary={stats['primary']}, Secondary={stats['secondary']}, Reforge={stats['reforge']}")
    
    print("\n=== Weapon Stats ===")
    for level in AVAILABLE_WEAPON_LEVELS:
        value = get_weapon_stats(level)
        print(f"Level {level} Weapon: {value} for each of 2 stats (Total: {value * 2})")
    
    print("\n=== Unique Set Availability ===")
    for level in AVAILABLE_GEAR_LEVELS:
        print(f"Level {level}: Unique sets {'available' if can_use_unique_set(level) else 'not available'}")
    
    print("\n=== Gear Configuration ===")
    print(f"Total gear pieces: {TOTAL_GEAR_PIECES}")
    print(f"Max unique gear pieces: {MAX_UNIQUE_GEAR_PIECES}")
    print(f"Weapon slot: {WEAPON_SLOT} (always unique)")
    print(f"\nSlots that CANNOT be unique: {', '.join(UNIQUE_FORBIDDEN_SLOTS)}")
    print(f"Slots that CAN be unique: {', '.join(UNIQUE_ALLOWED_SLOTS)}")
    
    print("\n=== Subclass Unique Stats ===")
    for class_name, subclasses in SUBCLASS_UNIQUE_STATS.items():
        print(f"\n{class_name}:")
        for subclass, stats in subclasses.items():
            print(f"  {subclass}: {stats[0]} + {stats[1]}")
    
    print("\n=== Stat Source Breakdown (Level 80, 6 Unique, Weapon 90) ===")
    breakdown = get_stat_sources_breakdown(80, 6, 90)
    print(f"Unique pieces: {breakdown['unique_count']}")
    print(f"Regular pieces: {breakdown['regular_count']}")
    print(f"Max from gear: {breakdown['max_from_gear']}")
    print(f"Total reforge: {breakdown['total_reforge']}")
    print(f"Total from gems: {breakdown['gems']['total_from_gems']}")
    if 'weapon' in breakdown:
        print(f"Weapon contribution: {breakdown['weapon']['total_from_weapon']} (Level {breakdown['weapon']['level']})")
    
    print("\n✅ Config test complete!")