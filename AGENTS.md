# AGENTS.md

## Project

Text-based procedural roguelike as a Telegram bot. Russian language UI.
Terminal runner (`runner.py`) used for debugging without the bot.

## Stack

- Python 3.11+
- aiogram (Telegram bot, not yet implemented)
- aiosqlite (async SQLite)
- JSON files for all game data (presets, templates, rules, layout)

## Architecture layers

```
TelegramUI (bot/) — not yet implemented
    ↓
runner.py — terminal debug entrypoint
    ↓
RogueInterface (core/rogue_interface.py) — async facade, single entry point
    ↓
engine.py — stateless functions, orchestrates systems
    ↓
Systems (core/systems/) — isolated classes, mutate state, return logs
    ↓
Database (database/database.py) — aiosqlite, get/save JSON state per user_id
```

### Layers contract

- **Systems** know nothing about each other, the DB, or the bot. They receive a slice of state, mutate it, return a log dict.
- **Engine** imports systems, wires them together, handles cross-system logic (e.g. move → detect enemies → set combat_state).
- **RogueInterface** calls engine functions, calls `_finalize`, never contains game logic.
- **ui_builder** reads state and log to produce buttons and state_type. No mutations.
- **log_handler** renders log dicts to human-readable Russian text.

## Transaction flow (button press → output)

1. User presses button → `action` string sent (format: `command:arg0:arg1`)
2. `runner.py` / bot handler parses action, calls `RogueInterface` method
3. Interface calls `database.get_state(user_id)` → `active_run_state: dict`
4. Interface calls `engine.{action}(args, active_run_state)` → `log: dict`
5. Engine instantiates relevant System(s), passes state slices, systems mutate state in-place
6. Engine returns log
7. Interface calls `_finalize(user_id, state, log)`:
   - `log_handler.render(log)` → `text: str`
   - `ui_builder.get_state_type(log, state)` → `state_type: str`
   - `ui_builder.get_buttons(log, state, state_type)` → `buttons: list`
   - writes `state["menu_context"]["type"] = state_type`
   - `database.save_state(user_id, state)`
   - returns contract: `{"text": str, "buttons": list, "state_type": str}`

## Button action format

`command:arg0:arg1`

| command | arg0 | arg1 |
|---|---|---|
| init_run | — | — |
| continue_run | — | — |
| back_the_menu | — | — |
| move | forward / backward / left / right / down / to_fork | — |
| attack | {enemy_key_name} | — |
| inventory_open | inventory / room_loot | — |
| inventory_select | {item_key_name} | {source} |
| move_item_to | {destination} | — |
| use_item | — | — |
| goto_menu | {menu} | — |
| menu | {menu} | {action} |
| start_again | — | — |

`back_the_menu` sets `opened_menu: null` and calls `continue_run`. If `opened_menu` is already `null`, does nothing.

**Examples**:
- `goto_menu:main_menu` — open main menu
- `menu:main_menu:new_game` — start new game from main menu
- `menu:upgrades_menu:heal` — buy health upgrade
- `back_the_menu` — return to game from any menu
- `start_again` — start over after death

## State types

Computed from log in `ui_builder.get_state_type`, never stored (except `menu_context["type"]` for overlay recovery).

| state_type | trigger |
|---|---|
| explore | move log, combat_ended, continue |
| combat | move with enemies, attack without combat_ended |
| dead | death log |

## Menu system

For menu navigation, `menu_context` in `active_run_state` is used:

| Field | Description |
|---|---|
| `type` | Primary game type (`explore`/`combat`/`dead`/`entrance`), computed from log |
| `opened_menu` | Currently open menu (`null`/`inventory`/`main_menu`/`upgrades_menu`/`help_menu`/`dead`) |

- **Overlay menus** do not change `type`. Inventory (`inventory`) is a special case of an overlay.
- **Death screen** is an overlay with `opened_menu: "dead"`, `type: "dead"`.
- **Navigation**: `goto_menu:{menu}` buttons change `opened_menu`. `menu:{menu}:{action}` buttons perform actions within a menu.
- **Closing**: `back_the_menu` sets `opened_menu: null` and calls `continue_run`.

**Backward compatibility**: `RogueInterface` will migrate existing states with `last_state_type` to `menu_context` on load. If `last_state_type` is present, it becomes `menu_context["type"]` and `opened_menu` is set to `null`. After migration, `last_state_type` is removed from the state.

## Naming

- `key_name` — dict key used in JSON files (e.g. `"apple"`, `"dragon"`)
- `text_name` — human-readable name from preset (e.g. `"яблоко"`, `"Дракон"`)
- `source` / `destination` — container key name: `"inventory"` or `"room_loot"`
- `log` — dict returned by engine/system describing what happened
- `state` — full `active_run_state` dict
- `contract` — dict returned to UI: `{text, buttons, state_type}`
- `menu_context` — dict with `type` (primary game state) and `opened_menu` (current overlay)

## JSON file structure

### data/log_templates.json
Contains log templates (copied with `.copy()` before mutation) and `run_state_template` (deep-copied on `init_run`).

Key templates: `move_log_template`, `combat_log_template`, `combat_consequence_log_template`, `dead_log_template`, `inventory_log_template`, `continue_run_log_template`, `run_state_template`.

### run_state_template (active_run_state shape)
```json
{
  "active": true,
  "menu_context": {
    "type": null,
    "opened_menu": null
  },
  "player": {
    "base_health", "current_health", "base_damage", "base_defence", "base_speed",
    "equipped_items": {"weapon": null, "armour": null},
    "inventory": []
  },
  "combat_state": {"in_combat": false, "turns": null, "enemies": null},
  "inventory_state": {
    "selected_item_key_name": null,
    "loot_source": null,
    "selected_item_source": null
  },
  "floor": {
    "index": null, "current_room_index": null,
    "fork_stack": [], "down_in_room": -1, "rooms": []
  }
}
```

### data/items.json
`{ key_name: { type, name, damage, defence, weight, heal, poison, min_floor } }`

### data/creatures.json
`{ enemies: { key_name: { name, health, damage, defence, speed, min_floor, biom[] } }, npcs: {} }`

### data/layout.json
Biom config: name pool, mood pool, loot pool, enemies_amount limits, loot_amount limits, floor_scale limits, branch_rules, doors_template, valid_directions. Also entrance_prompt per floor index.

### data/rules.json
`combat`: turn_delimiter, actions, damage_scale_limits.
`opposite_direction`: direction → opposite mapping.

### data/bridge_spec.json
`contract`: shape of the return contract.
`ui_labels`: action string → Russian label mapping for ui_builder.

### Room shape (inside floor.rooms)
```json
{
  "index": 0, "type": "room", "room_type": "combat",
  "name": "пещера", "mood": "затхло",
  "cleared": false,
  "enemies": ["dragon", "lizard"],
  "loot": {"room_loot": ["apple"]},
  "doors": {"forward": 1, "backward": 0, "left": "NEW", "right": null, "down": false, "branch_power": 0.38}
}
```

Door values: `null` = no door, `int` = room index, `"NEW"` = exists but not generated yet, `true` = floor exit, `false` = no exit here.

## Current implementation status

- [x] Core systems: FloorSystem, MoveSystem, CombatSystem, InventorySystem
- [x] Engine functions: init_run, move, move_to_fork, attack, inventory_open, inventory_select, inventory_move
- [x] RogueInterface (async facade)
- [x] Database (aiosqlite, get/save state)
- [x] ui_builder (buttons + state_type)
- [x] log_handler (Russian text render)
- [x] Terminal runner with full action parsing
- [ ] Telegram bot (aiogram handlers, FSM, keyboards)
- [ ] LLM text generation with hash cache
- [ ] use_item (food heal, weapon equip)
- [ ] Floor transition (down door handling)
- [ ] Death handling (state cleanup, start_again)

## AGENT DIRECTIVES & RESPONSE RULES

You are an elite, pragmatic Python architect. Your code is brutally minimal, straightforward, and strictly functional. You despise boilerplate and defensive programming when the data contract is guaranteed.

### 1. Code Style & Philosophy: "Trust the Contract"
- **STRICTLY FORBIDDEN: Defensive programming for guaranteed data.** The JSON presets (`items.json`, `layout.json`, etc.) are hand-written and validated. NEVER write checks for missing keys, `None` values, or out-of-bounds indices for data derived from these JSONs. Assume the dictionary keys always exist.
- **NO BOILERPLATE:** Do not write `try/except` blocks unless dealing with external I/O or explicitly requested. Let Python raise `KeyError` or `ValueError` if the state is corrupted.
- **MINIMALISM:** Write the exact amount of code required to mutate the state or return the log. Nothing more.
- **NO DOCSTRINGS:** Omit all docstrings, inline comments (unless clarifying a complex math/logic hack), and type hints (unless strictly necessary to resolve ambiguity).

### 2. Architectural Boundaries
- **STRICT ISOLATION:** Never write cross-layer logic.
  - Systems mutate state and return logs. They DO NOT touch the DB or UI.
  - UI Builder reads logs/state and returns buttons. It DOES NOT mutate state.
  - Interface manages flow. It DOES NOT contain game rules.
- **NO HARDCODING:** Never hardcode any game values, strings, or limits. If a value exists in a JSON preset, extract it from the state/preset.

### 3. Output & Communication Format
- **ZERO FLUFF:** No pleasantries, no "Here is the code", no filler text. Every single token must carry technical weight.
- **FLAW -> FIX:** If fixing an error, first state the exact flaw in one sentence, then provide the code fix.
- **ONE SOLUTION:** Propose exactly ONE optimal approach. Do not provide alternatives unless explicitly asked by the user. If the answer is one line of code, your entire response must be one line of code.
- **LANGUAGE:** Code, comments, variable names, and READMEs must be in **English**. All discussions, planning, reasoning summaries, and TODOs must be in **Russian**.

### 4. Proposed Solution Structure
When proposing a new feature or fixing a complex bug, use this ultra-short format:
1. **What:**[Action]
2. **Where:** [File / Class / Function]
3. **I/O:**[Input -> Output / State Mutation]
4. **Code:** [The Python snippet]

**CRITICAL:** Do not leak your internal reasoning/thinking process into the final output. Give me only the raw, direct result.
