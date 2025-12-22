#!/usr/bin/env python3
"""
Silent Hill 2 (2024 Remake) Save Game Editor
Supports modifying health, weapon ammo, and inventory items
"""

import zlib
import struct
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime


class SH2SaveEditor:
    """Editor for Silent Hill 2 (2024 Remake) save files"""
    
    def __init__(self, filename):
        self.filename = filename
        self.save_data = None
        self.decompressed = None
        
    def load(self):
        """Load and decompress the save file"""
        with open(self.filename, 'rb') as f:
            data = f.read()
        
        # Find zlib compression (can be at different offsets)
        for i in range(0, 300):
            if data[i:i+2] in (b'\x78\x9c', b'\x78\xda'):
                compressed_size_offset = i - 8
                # Format: COMPRESSED size first, then UNCOMPRESSED size
                compressed_size = struct.unpack('<I', data[compressed_size_offset:compressed_size_offset+4])[0]
                uncompressed_size = struct.unpack('<I', data[compressed_size_offset+4:compressed_size_offset+8])[0]
                
                compressed_data = data[i:i+compressed_size]
                decompressed = zlib.decompress(compressed_data)
                
                self.save_data = {
                    'header': data[:compressed_size_offset],
                    'size_info_offset': compressed_size_offset,
                    'compression_offset': i,
                    'decompressed': decompressed,
                    'uncompressed_size': uncompressed_size,
                    'compressed_size': compressed_size
                }
                self.decompressed = bytearray(decompressed)
                return True
        
        return False
    
    def save(self, output_filename=None):
        """Save the modified save file"""
        if output_filename is None:
            output_filename = self.filename
        
        # Compress the modified data
        compressed = zlib.compress(bytes(self.decompressed), level=9)
        
        # Update sizes
        new_uncompressed_size = len(self.decompressed)
        new_compressed_size = len(compressed)
        
        # Rebuild the file
        # IMPORTANT: The format is COMPRESSED size first, then UNCOMPRESSED size
        new_file = bytearray(self.save_data['header'])
        new_file.extend(struct.pack('<I', new_compressed_size))    # At 0x89 (or similar): compressed size
        new_file.extend(struct.pack('<I', new_uncompressed_size))  # At 0x8D (or similar): uncompressed size
        new_file.extend(compressed)
        
        # Write to file
        with open(output_filename, 'wb') as f:
            f.write(new_file)
        
        print(f"✓ Saved to: {output_filename}")
        print(f"  Original size: {self.save_data['uncompressed_size']:,} bytes")
        print(f"  New size: {new_uncompressed_size:,} bytes")
    
    def _find_property_offset(self, property_name, data_type='float'):
        """Find offset of a property value"""
        pos = self.decompressed.find(property_name.encode() + b'\x00')
        if pos == -1:
            return -1
        
        # Skip: string + null + "FloatProperty"/"IntProperty" + null + size (4) + metadata (8)
        if data_type == 'float':
            type_name = b'FloatProperty\x00'
        else:
            type_name = b'IntProperty\x00'
        
        offset = pos + len(property_name) + 1 + len(type_name) + 4 + 8
        return offset
    
    def _find_weapon_offset(self, weapon_name):
        """Find offset of weapon ammo count"""
        pos = self.decompressed.find(weapon_name.encode() + b'\x00')
        if pos == -1:
            return -1
        
        # Ammo is stored as int32 right after weapon name + null
        return pos + len(weapon_name) + 1
    
    def get_health(self):
        """Get current health value"""
        offset = self._find_property_offset('HealthValue', 'float')
        if offset > 0:
            return struct.unpack('<f', self.decompressed[offset:offset+4])[0]
        return None
    
    def set_health(self, value):
        """Set health value"""
        offset = self._find_property_offset('HealthValue', 'float')
        if offset > 0:
            self.decompressed[offset:offset+4] = struct.pack('<f', float(value))
            return True
        return False
    
    def get_weapon_ammo(self, weapon_name):
        """Get weapon ammo count"""
        offset = self._find_weapon_offset(weapon_name)
        if offset > 0:
            return struct.unpack('<i', self.decompressed[offset:offset+4])[0]
        return None
    
    def set_weapon_ammo(self, weapon_name, amount):
        """Set weapon ammo count"""
        offset = self._find_weapon_offset(weapon_name)
        if offset > 0:
            self.decompressed[offset:offset+4] = struct.pack('<i', int(amount))
            return True
        return False
    
    def _find_item_quantity_offset(self, item_name):
        """Find offset of item quantity in CollectedItems"""
        pos = self.decompressed.find(item_name.encode() + b'\x00')
        if pos == -1:
            return -1
        
        # Find Quantity after item name
        qty_pos = self.decompressed.find(b'Quantity\x00', pos, pos + 100)
        if qty_pos == -1:
            return -1
        
        # The value is 34 bytes after "Quantity" string
        return qty_pos + 34
    
    def get_item_quantity(self, item_name):
        """Get quantity of an inventory item"""
        offset = self._find_item_quantity_offset(item_name)
        if offset > 0 and offset + 4 <= len(self.decompressed):
            return struct.unpack('<i', self.decompressed[offset:offset+4])[0]
        return None
    
    def set_item_quantity(self, item_name, amount):
        """Set quantity of an inventory item"""
        offset = self._find_item_quantity_offset(item_name)
        if offset > 0 and offset + 4 <= len(self.decompressed):
            self.decompressed[offset:offset+4] = struct.pack('<i', int(amount))
            return True
        return False
    
    def display_info(self):
        """Display current save file information"""
        print("\n" + "="*70)
        print(f"SAVE FILE: {Path(self.filename).name}")
        print("="*70)
        
        # Health
        health = self.get_health()
        if health is not None:
            print(f"Health: {health:.2f}")
        
        # Check various weapons
        weapons = ['Pistol', 'Shotgun', 'Rifle', 'Handgun', 'SteelPipe']
        print("\nWeapon Ammo:")
        found_weapons = False
        for weapon in weapons:
            ammo = self.get_weapon_ammo(weapon)
            if ammo is not None:
                print(f"  {weapon}: {ammo}")
                found_weapons = True
        if not found_weapons:
            print("  (No weapons found)")
        
        # Check inventory items
        inventory_items = ['HealthDrink', 'Syringe', 'HandgunAmmo', 'ShotgunAmmo', 'ShotgunShells', 
                          'RifleAmmo', 'FirstAidKit']
        print("\nInventory Items:")
        found_items = False
        for item in inventory_items:
            quantity = self.get_item_quantity(item)
            if quantity is not None:
                print(f"  {item}: {quantity}")
                found_items = True
        if not found_items:
            print("  (No items found)")


def create_backup(filename):
    """Create a timestamped backup of the save file"""
    if not os.path.exists(filename):
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{filename}.backup_{timestamp}"
    
    try:
        shutil.copy2(filename, backup_name)
        print(f"✓ Backup created: {backup_name}")
        return backup_name
    except Exception as e:
        print(f"⚠ Warning: Could not create backup: {e}")
        return None


def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print("Silent Hill 2 (2024 Remake) Save Editor")
        print("\nUsage:")
        print("  python sh2_save_editor.py <save_file> [options]")
        print("\nOptions:")
        print("  --info                    Display save file information")
        print("  --health <value>          Set health (e.g., 100.0)")
        print("  --pistol <ammo>           Set pistol ammo")
        print("  --shotgun <ammo>          Set shotgun ammo")
        print("  --rifle <ammo>            Set rifle ammo")
        print("  --healthdrink <qty>       Set health drink quantity")
        print("  --syringe <qty>           Set syringe quantity")
        print("  --handgunammo <qty>       Set handgun ammo (inventory item)")
        print("  --shotgunammo <qty>       Set shotgun ammo (inventory item)")
        print("  --rifleammo <qty>         Set rifle ammo (inventory item)")
        print("  --output <file>           Output filename (default: overwrites input)")
        print("  --no-backup               Skip creating backup (not recommended)")
        print("\nExamples:")
        print("  python sh2_save_editor.py SaveGameData_2.sav --info")
        print("  python sh2_save_editor.py SaveGameData_2.sav --health 100 --pistol 999")
        print("  python sh2_save_editor.py SaveGameData_2.sav --rifle 500 --rifleammo 500")
        print("  python sh2_save_editor.py SaveGameData_2.sav --healthdrink 99 --syringe 20")
        print("  python sh2_save_editor.py SaveGameData_2.sav --health 100 --output modified.sav")
        sys.exit(1)
    
    save_file = sys.argv[1]
    
    if not os.path.exists(save_file):
        print(f"Error: File not found: {save_file}")
        sys.exit(1)
    
    # Load save file
    editor = SH2SaveEditor(save_file)
    if not editor.load():
        print("Error: Could not load save file")
        sys.exit(1)
    
    # Parse arguments
    output_file = None
    modifications = []
    create_backup_flag = True
    
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == '--info':
            editor.display_info()
            sys.exit(0)
        
        elif arg == '--no-backup':
            create_backup_flag = False
        
        elif arg == '--health' and i + 1 < len(sys.argv):
            value = float(sys.argv[i + 1])
            modifications.append(('health', value))
            i += 1
        
        elif arg == '--pistol' and i + 1 < len(sys.argv):
            value = int(sys.argv[i + 1])
            modifications.append(('Pistol', value))
            i += 1
        
        elif arg == '--shotgun' and i + 1 < len(sys.argv):
            value = int(sys.argv[i + 1])
            modifications.append(('Shotgun', value))
            i += 1
        
        elif arg == '--rifle' and i + 1 < len(sys.argv):
            value = int(sys.argv[i + 1])
            modifications.append(('Rifle', value))
            i += 1
        
        elif arg == '--healthdrink' and i + 1 < len(sys.argv):
            value = int(sys.argv[i + 1])
            modifications.append(('item:HealthDrink', value))
            i += 1
        
        elif arg == '--syringe' and i + 1 < len(sys.argv):
            value = int(sys.argv[i + 1])
            modifications.append(('item:Syringe', value))
            i += 1
        
        elif arg == '--handgunammo' and i + 1 < len(sys.argv):
            value = int(sys.argv[i + 1])
            modifications.append(('item:HandgunAmmo', value))
            i += 1
        
        elif arg == '--shotgunammo' and i + 1 < len(sys.argv):
            value = int(sys.argv[i + 1])
            modifications.append(('item:ShotgunAmmo', value))
            i += 1
        
        elif arg == '--rifleammo' and i + 1 < len(sys.argv):
            value = int(sys.argv[i + 1])
            modifications.append(('item:RifleAmmo', value))
            i += 1
        
        elif arg == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 1
        
        i += 1
    
    # Apply modifications
    if modifications:
        # Create backup before modifying (unless disabled)
        if create_backup_flag and output_file is None:
            create_backup(save_file)
        
        print("\nApplying modifications:")
        for mod_type, value in modifications:
            if mod_type == 'health':
                if editor.set_health(value):
                    print(f"  ✓ Set health to {value:.2f}")
                else:
                    print(f"  ✗ Could not set health")
            elif mod_type.startswith('item:'):
                item_name = mod_type[5:]  # Remove 'item:' prefix
                if editor.set_item_quantity(item_name, value):
                    print(f"  ✓ Set {item_name} quantity to {value}")
                else:
                    print(f"  ✗ Could not set {item_name} quantity")
            else:
                if editor.set_weapon_ammo(mod_type, value):
                    print(f"  ✓ Set {mod_type} ammo to {value}")
                else:
                    print(f"  ✗ Could not set {mod_type} ammo")
        
        # Save the file
        print()
        editor.save(output_file)
        print("\n✓ Save file successfully modified!")
    else:
        print("No modifications specified. Use --info to view save data.")


if __name__ == '__main__':
    main()
