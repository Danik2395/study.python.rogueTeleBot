#
# presets.py
#

import json

with open("creatures.json", "r", encoding="utf-8") as f:
    CREATURES = json.load(f)
    ENEMIES = CREATURES["enemies"]
    NPCS = CREATURES["npcs"]

with open("items.json", "r", encoding="utf-8") as f:
    ITEMS = json.load(f)

with open("layout.json", "r", encoding="utf-8") as f:
    LAYOUT = json.load(f)

with open("rules.json", "r", encoding="utf-8") as f:
    RULES = json.load(f)
    COMBAT_RULES = RULES["combat"]

with open("log_templates.json", "r", encoding="utf-8") as f:
    LOG = json.load(f)
