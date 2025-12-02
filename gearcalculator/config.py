# config.py - Game Data Configuration

# All available stats in the game
ALL_STATS = ["Crit", "Haste", "Mastery", "Versatility", "Luck"]

# Class to Attribute mapping
CLASS_ATTRIBUTES = {
    "Shield Knight": "Strength",
    "Wind Knight": "Strength",
    "Heavy Guardian": "Strength",
    "Stormblade": "Agility",
    "Marksman": "Agility",
    "Frost Mage": "Intellect",
    "Verdant Oracle": "Intellect",
    "Beat Performer": "Intellect"
}

# Subclass definitions
SUBCLASSES = {
    "Stormblade": ["Iaido", "Moonstrike"],
    "Frost Mage": ["Icicle", "Frost Beam"],
    "Wind Knight": ["Skyward", "Vanguard"],
    "Verdant Oracle": ["Smite", "Lifebind"],
    "Heavy Guardian": ["Block", "Earthfort"],
    "Marksman": ["Falconry", "Wildpack"],
    "Shield Knight": ["Shield", "Recovery"],
    "Beat Performer": ["Dissonance", "Concerto"]
}

# Subclass unique stats (both stats for unique gear)
SUBCLASS_UNIQUE_STATS = {
    "Iaido": ["Crit", "Mastery"],
    "Moonstrike": ["Luck", "Haste"],
    "Icicle": ["Crit", "Luck"],
    "Frost Beam": ["Haste", "Mastery"],
    "Skyward": ["Crit", "Luck"],
    "Vanguard": ["Haste", "Mastery"],
    "Smite": ["Mastery", "Luck"],
    "Lifebind": ["Mastery", "Haste"],
    "Block": ["Mastery", "Luck"],
    "Earthfort": ["Mastery", "Versatility"],
    "Falconry": ["Crit", "Haste"],
    "Wildpack": ["Haste", "Mastery"],
    "Shield": ["Haste", "Mastery"],
    "Recovery": ["Crit", "Mastery"],
    "Dissonance": ["Haste", "Luck"],
    "Concerto": ["Crit", "Haste"]
}

# Gear slot definitions
MANDATORY_SLOTS = ["Earrings", "Ring", "Charm", "Necklace"]
OPTIONAL_SLOTS = ["Helmet", "Armor", "Gauntlets", "Boots", "Bracelet(L)", "Bracelet(R)"]
ALL_GEAR_SLOTS = MANDATORY_SLOTS + OPTIONAL_SLOTS

# Slots where unique gear CAN be equipped
UNIQUE_ALLOWED_SLOTS = ["Helmet", "Armor", "Gauntlets", "Boots", "Bracelet(L)", "Bracelet(R)"]

# Forbidden stats by attribute and slot
FORBIDDEN_STATS = {
    "Agility": {
        "Helmet": "Haste",
        "Armor": "Mastery",
        "Gauntlets": "Crit",
        "Boots": "Crit",
        "Earrings": "Haste",
        "Necklace": "Mastery",
        "Ring": "Versatility",
        "Bracelet(L)": "Versatility",
        "Bracelet(R)": "Luck",
        "Charm": "Luck"
    },
    "Intellect": {
        "Helmet": "Crit",
        "Armor": "Crit",
        "Gauntlets": "Versatility",
        "Boots": "Luck",
        "Earrings": "Versatility",
        "Necklace": "Luck",
        "Ring": "Mastery",
        "Bracelet(L)": "Haste",
        "Bracelet(R)": "Mastery",
        "Charm": "Haste"
    },
    "Strength": {
        "Helmet": "Versatility",
        "Armor": "Luck",
        "Gauntlets": "Haste",
        "Boots": "Mastery",
        "Earrings": "Mastery",
        "Necklace": "Haste",
        "Ring": "Luck",
        "Bracelet(L)": "Crit",
        "Bracelet(R)": "Crit",
        "Charm": "Versatility"
    }
}

def get_forbidden_stat(slot, attribute):
    """Get the forbidden stat for a given slot and attribute."""
    return FORBIDDEN_STATS.get(attribute, {}).get(slot, None)

def get_valid_stats_for_slot(slot, attribute):
    """Get list of stats that CAN be used on this slot."""
    forbidden = get_forbidden_stat(slot, attribute)
    if forbidden:
        return [stat for stat in ALL_STATS if stat != forbidden]
    return ALL_STATS.copy()

def validate_class_subclass(class_name, subclass_name):
    """Validate that subclass belongs to class."""
    if class_name not in SUBCLASSES:
        return False
    return subclass_name in SUBCLASSES[class_name]
