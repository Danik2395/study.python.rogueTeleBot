#
# presets.py
#

import json

with open("creatures.json", "r", encoding="utf-8") as cr_file:
    CREATURES = json.load(cr_file)

with open("items.json", "r", encoding="utf-8") as it_file:
    ITEMS = json.load(it_file)

with open("layout.json", "r", encoding="utf-8") as rmp_file:
    LAYOUT = json.load(rmp_file)

ENEMIES = CREATURES["enemies"]
NPCS = CREATURES["npcs"]
