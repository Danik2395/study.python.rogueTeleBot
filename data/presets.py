import json

with open("data/creatures.json", "r", encoding="utf-8") as f:
    CREATURES = json.load(f)
    ENEMIES = CREATURES["enemies"]
    NPCS = CREATURES["npcs"]

with open("data/items.json", "r", encoding="utf-8") as f:
    ITEMS = json.load(f)

with open("data/layout.json", "r", encoding="utf-8") as f:
    LAYOUT = json.load(f)

with open("data/rules.json", "r", encoding="utf-8") as f:
    RULES = json.load(f)
    COMBAT_RULES = RULES["combat"]

with open("data/log_templates.json", "r", encoding="utf-8") as f:
    LOG = json.load(f)

with open("data/bridge_spec.json", "r", encoding="utf-8") as f:
    BRIDGE_SPEC = json.load(f)
    BRIDGE_CONTRACT = BRIDGE_SPEC["contract"]
    UI_LABELS = BRIDGE_SPEC["ui_lables"]
