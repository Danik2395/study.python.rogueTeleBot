import json
from dataclasses import dataclass, field

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
    UI_LABELS = BRIDGE_SPEC["ui_labels"]
    PARENT_MENU = BRIDGE_SPEC["parent_menu"]

with open("data/forged_text.json", "r", encoding="utf-8") as f:
    FTEXT = json.load(f)

@dataclass
class Button:
    label: str = ""
    action: str = ""

@dataclass
class Contract():
    text: str = ""
    buttons: list[Button] = field(default_factory=list[Button])
    state_type: str = ""
