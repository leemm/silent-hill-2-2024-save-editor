# Silent Hill 2 (2024) Remake Save Editor

A Python tool for modifying Silent Hill 2 (2024 Remake) save game files. Allows you to edit health, weapon ammo, and inventory items like health drinks and syringes.

## Features

- ✅ Modify health values
- ✅ Edit weapon ammunition (Pistol, Shotgun, Rifle, etc.)
- ✅ Change inventory item quantities (Health Drinks, Syringes, Ammo)
- ✅ **Automatic backup creation** before modifications
- ✅ View current save file contents
- ✅ Safe file format handling (proper compression/decompression)
- ✅ No checksums to worry about - game doesn't validate saves

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)

## Installation

1. Clone this repository or download `sh2_save_editor.py`
2. Make sure Python 3 is installed on your system

```bash
git clone https://github.com/yourusername/sh2-save-editor.git
cd sh2-save-editor
```

## Usage

### View Save File Contents

To see what's currently in your save file:

```bash
python sh2_save_editor.py SaveGameData_2.sav --info
```

**Example output:**
```
======================================================================
SAVE FILE: SaveGameData_2.sav
======================================================================
Health: 75.00

Weapon Ammo:
  Pistol: 10

Inventory Items:
  HealthDrink: 7
  Syringe: 5
  HandgunAmmo: 27
  ShotgunAmmo: 2
```

### Modify Health

Set your health to maximum (100.0):

```bash
python sh2_save_editor.py SaveGameData_2.sav --health 100.0
```

### Modify Weapon Ammo

Max out your pistol ammo:

```bash
python sh2_save_editor.py SaveGameData_2.sav --pistol 999
```

### Modify Inventory Items

Give yourself 99 health drinks and syringes:

```bash
python sh2_save_editor.py SaveGameData_2.sav --healthdrink 99 --syringe 99
```

### Multiple Modifications at Once

You can combine multiple modifications in one command:

```bash
python sh2_save_editor.py SaveGameData_2.sav \
  --health 100.0 \
  --pistol 999 \
  --healthdrink 99 \
  --syringe 99 \
  --shotgunammo 99
```

### Save to a Different File

To create a modified copy without overwriting the original:

```bash
python sh2_save_editor.py SaveGameData_2.sav --health 100 --output SaveGameData_2_modified.sav
```

### Skip Automatic Backup

By default, the tool creates a timestamped backup before modifying. To skip this:

```bash
python sh2_save_editor.py SaveGameData_2.sav --health 100 --no-backup
```

**Note:** Not recommended! Always keep backups.

## Available Options

| Option | Description | Example |
|--------|-------------|---------|
| `--info` | Display save file information | `--info` |
| `--health <value>` | Set health (0.0 to 100.0) | `--health 100.0` |
| `--pistol <ammo>` | Set pistol ammo | `--pistol 999` |
| `--shotgun <ammo>` | Set shotgun ammo | `--shotgun 100` |
| `--healthdrink <qty>` | Set health drink quantity | `--healthdrink 99` |
| `--syringe <qty>` | Set syringe quantity | `--syringe 50` |
| `--handgunammo <qty>` | Set handgun ammo (inventory) | `--handgunammo 999` |
| `--shotgunammo <qty>` | Set shotgun ammo (inventory) | `--shotgunammo 99` |
| `--output <file>` | Save to different file | `--output modified.sav` |
| `--no-backup` | Skip automatic backup | `--no-backup` |

## How It Works

Silent Hill 2 (2024 Remake) save files use Unreal Engine 5's save format:
1. A small header (137-155 bytes)
2. Two size fields (compressed and uncompressed sizes)
3. Zlib-compressed game data

The tool:
1. Decompresses the save file
2. Locates and modifies the requested values
3. Recompresses with the correct format
4. Writes the modified save

The game doesn't validate save integrity, so modifications are safe!

## Save File Locations

### Windows (Steam)
```
C:\Users\[YourUsername]\AppData\Local\SilentHill2\Saved\SaveGames\
```

### Windows (Epic Games)
```
C:\Users\[YourUsername]\AppData\Local\SilentHill2\Saved\SaveGames\
```

**Note:** Exact paths may vary. Look for files named `SaveGameData_X.sav` where X is a number (0-9).

### Linux (Steam Proton)
```
/home/<user>/.steam/steam/steamapps/compatdata/2124490/pfx/drive_c/users/steamuser/AppData/Local/SilentHill2/Saved/SaveGames/123456789012345678
```
*Replace `<user>` with your Linux username. The final folder (the long number) is your SteamID64 and may differ.*

## Examples

### Example 1: Max Medical Supplies
```bash
python sh2_save_editor.py SaveGameData_2.sav \
  --healthdrink 99 \
  --syringe 99 \
  --health 100.0
```

### Example 2: Max All Ammo
```bash
python sh2_save_editor.py SaveGameData_2.sav \
  --pistol 999 \
  --shotgun 100 \
  --handgunammo 999 \
  --shotgunammo 99
```

### Example 3: Full Loadout
```bash
python sh2_save_editor.py SaveGameData_2.sav \
  --health 100.0 \
  --pistol 999 \
  --shotgun 100 \
  --healthdrink 99 \
  --syringe 99 \
  --handgunammo 999 \
  --shotgunammo 99 \
  --output SaveGameData_2_maxed.sav
```

## Restoring from Backup

If something goes wrong, backups are automatically created with timestamps:

```
SaveGameData_2.sav.backup_20241209_153045
```

To restore:
1. Delete or rename the modified save file
2. Remove the `.backup_20241209_153045` suffix from the backup
3. You now have your original save back!

Or simply copy it back:
```bash
cp SaveGameData_2.sav.backup_20241209_153045 SaveGameData_2.sav
```

## Troubleshooting

### "Could not set [item] quantity"
The item doesn't exist in your save file yet. You need to collect at least one of that item in-game first.

### "File not found"
Make sure you're running the command from the correct directory, or provide the full path to your save file.

### Game shows black screen after loading
This shouldn't happen with the current version, but if it does:
1. Restore from the backup
2. Try again with smaller values (e.g., 99 instead of 999)
3. Open an issue on GitHub

### Values don't change in game
1. Make sure you're modifying the correct save slot
2. Verify the modification worked with `--info`
3. Try loading a different save first, then load your modified one

## Safety Notes

⚠️ **Recommended Maximum Values:**
- Health: 100.0 (game maximum)
- Health Drinks: 99 (safe)
- Syringes: 99 (safe)
- Ammo: 999 (safe for weapons), 99 (safe for inventory items)

Setting extremely high values (like 999,999) may cause:
- UI display glitches
- Integer overflow issues
- Game instability

**Always keep backups of your saves!**

## Technical Details

### File Format
The save files use Unreal Engine 5's format:
- Magic signature: `VASby`
- Size fields at offset 0x89/0x8D (may vary slightly)
- Zlib-compressed property tree
- No checksums or validation

### Property Structure
Items in inventory follow this pattern:
```
ItemRowName → "ItemName" → Quantity → IntProperty → [34 bytes] → VALUE (int32)
```

Weapon ammo:
```
"WeaponName" → [1 byte] → VALUE (int32)
```

Health:
```
"HealthValue" → FloatProperty → [metadata] → VALUE (float32)
```

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## License

MIT License - feel free to use and modify as you wish.

## Disclaimer

This tool is for personal use only. Use at your own risk. Always backup your save files before modifying them. The developers are not responsible for any data loss or corruption.

## Credits

- Reverse engineering and development by Claude (Anthropic)
- Testing and feedback by the community

## Version History

### v1.0.0 (2024-12-13)
- Initial release
- Support for Silent Hill 2 (2024 Remake)
- Support for health, weapon ammo, and inventory items
- Automatic backup creation
- Info display functionality

---

**Enjoy your modified Silent Hill 2 experience! 🎮👻**
