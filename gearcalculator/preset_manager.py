"""
preset_manager.py
Manages saving and loading of configuration presets
"""

import json
import os
from datetime import datetime


class PresetManager:
    """Manages configuration and gear presets"""
    
    def __init__(self, preset_folder="presets"):
        """
        Initialize preset manager
        
        Args:
            preset_folder: Folder to store preset files
        """
        self.preset_folder = preset_folder
        self._ensure_folder_exists()
    
    def _ensure_folder_exists(self):
        """Create preset folder if it doesn't exist"""
        if not os.path.exists(self.preset_folder):
            os.makedirs(self.preset_folder)
    
    def save_preset(self, name, config_data, locked_gear_data):
        """
        Save a preset
        
        Args:
            name: Preset name
            config_data: Configuration dictionary
            locked_gear_data: Locked gear dictionary
            
        Returns:
            (success, message)
        """
        try:
            preset = {
                'name': name,
                'created': datetime.now().isoformat(),
                'version': '2.2',
                'config': config_data,
                'locked_gear': locked_gear_data
            }
            
            # Sanitize filename
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = os.path.join(self.preset_folder, f"{safe_name}.json")
            
            with open(filename, 'w') as f:
                json.dump(preset, f, indent=2)
            
            return True, f"Preset saved: {filename}"
        
        except Exception as e:
            return False, f"Error saving preset: {str(e)}"
    
    def load_preset(self, filename):
        """
        Load a preset
        
        Args:
            filename: Preset filename (with or without path)
            
        Returns:
            (success, preset_data or error_message)
        """
        try:
            # If just filename given, add path
            if not os.path.dirname(filename):
                filename = os.path.join(self.preset_folder, filename)
            
            with open(filename, 'r') as f:
                preset = json.load(f)
            
            return True, preset
        
        except FileNotFoundError:
            return False, "Preset file not found"
        except json.JSONDecodeError:
            return False, "Invalid preset file format"
        except Exception as e:
            return False, f"Error loading preset: {str(e)}"
    
    def list_presets(self):
        """
        List all available presets
        
        Returns:
            List of (filename, preset_name, created_date) tuples
        """
        presets = []
        
        try:
            for filename in os.listdir(self.preset_folder):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.preset_folder, filename)
                    try:
                        with open(filepath, 'r') as f:
                            preset = json.load(f)
                        
                        name = preset.get('name', filename)
                        created = preset.get('created', 'Unknown')
                        presets.append((filename, name, created))
                    except:
                        # Skip invalid files
                        continue
        except:
            pass
        
        return sorted(presets, key=lambda x: x[2], reverse=True)
    
    def delete_preset(self, filename):
        """
        Delete a preset
        
        Args:
            filename: Preset filename
            
        Returns:
            (success, message)
        """
        try:
            if not os.path.dirname(filename):
                filename = os.path.join(self.preset_folder, filename)
            
            os.remove(filename)
            return True, "Preset deleted"
        
        except Exception as e:
            return False, f"Error deleting preset: {str(e)}"
    
    def export_preset(self, filename, export_path):
        """
        Export a preset to a different location
        
        Args:
            filename: Source preset filename
            export_path: Destination path
            
        Returns:
            (success, message)
        """
        try:
            if not os.path.dirname(filename):
                filename = os.path.join(self.preset_folder, filename)
            
            with open(filename, 'r') as f:
                preset = json.load(f)
            
            with open(export_path, 'w') as f:
                json.dump(preset, f, indent=2)
            
            return True, f"Preset exported to {export_path}"
        
        except Exception as e:
            return False, f"Error exporting preset: {str(e)}"
    
    def import_preset(self, import_path):
        """
        Import a preset from external file
        
        Args:
            import_path: Path to preset file
            
        Returns:
            (success, message)
        """
        try:
            with open(import_path, 'r') as f:
                preset = json.load(f)
            
            # Validate preset structure
            if 'name' not in preset or 'config' not in preset:
                return False, "Invalid preset file structure"
            
            # Save to presets folder
            name = preset['name']
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = os.path.join(self.preset_folder, f"{safe_name}.json")
            
            with open(filename, 'w') as f:
                json.dump(preset, f, indent=2)
            
            return True, f"Preset imported: {name}"
        
        except Exception as e:
            return False, f"Error importing preset: {str(e)}"


# Test
if __name__ == "__main__":
    print("Testing PresetManager...")
    
    manager = PresetManager()
    
    # Test save
    test_config = {
        'class_name': 'Stormblade',
        'subclass_name': 'Iaido',
        'gear_level': 80,
        'min_stats': {'Crit': 2000}
    }
    
    test_gear = {
        'locked_pieces': [
            {'slot': 'Helmet', 'is_unique': True, 'main_stat': 'Crit', 'sub_stat': 'Mastery'}
        ]
    }
    
    success, msg = manager.save_preset("Test Build", test_config, test_gear)
    print(f"Save: {msg}")
    
    # Test list
    presets = manager.list_presets()
    print(f"\nAvailable presets: {len(presets)}")
    for filename, name, created in presets:
        print(f"  - {name} (created: {created})")
    
    # Test load
    if presets:
        success, data = manager.load_preset(presets[0][0])
        if success:
            print(f"\nLoaded preset: {data['name']}")
            print(f"  Class: {data['config']['class_name']}")
    
    print("\n✅ PresetManager test complete!")
