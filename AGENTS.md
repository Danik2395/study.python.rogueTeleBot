# AGENTS.md

## Project

Text-based procedural roguelike as a Telegram bot. Russian language UI.
Terminal runner (`runner.py`) used for debugging without the bot.

## Stack

- Python 3.11+
- aiogram (Telegram bot – handlers, keyboards, message editing/fallback)
- aiosqlite (async SQLite)
- JSON files for all game data (presets, templates, rules, layout)

## Architecture layers

```
TelegramUI (bot/) — implemented (UserController, keyboards, message editing/fallback)
    ↓
runner.py — terminal debug entrypoint
    ↓
bot/user_handler.py (UserController) — command handlers, callback processing, message editing
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
- **log_handler** renders log dicts to human-readable Russian text using LLM with hash‑based caching. For `continue` logs with `menu` field, first checks `FTEXT["{menu}"]`; if not found, generates via LLM.

## Transaction flow (button press → output)

1. User presses button → `action` string sent (format: `command:arg0:arg1`)
2. `runner.py` / bot handler receives action
3. Handler calls `process_action` which parses the action string and calls the appropriate `RogueInterface` method
4. Interface calls `database.get_user_run_state(user_id)` → `state: dict` (always initialized with `run_state_template`, `active: false` on first `/start`)
5. Interface calls `engine.{action}(args, state)` → `log: dict`
6. Engine instantiates relevant System(s), passes state slices, systems mutate state in-place
7. Engine returns log
8. Interface calls `_finalize_game(user_id, state, log)`:
   - `log_handler.render(log)` → `text: str`
   - `ui_builder.get_state_type(log, state)` → `state_type: str`
   - `ui_builder.get_game_buttons(log, state, state_type)` → `buttons: list[Button]`
   - writes `state["menu_context"]["type"] = state_type`
   - `database.save_user_run_state(user_id, state)`
   - returns `Contract(text, buttons, state_type)`

## Button action format

`command:arg0:arg1`

| command | arg0 | arg1 |
|---|---|---|
| init_run | — | — |
| back_from_menu | source_key_menu | — |
| move | forward / backward / left / right / down / to_fork | — |
| attack | {enemy_key_name} | — |
| inventory_open | inventory / room_loot | — |
| inventory_select | {item_key_name} | {source} |
| move_item_to | {destination} | — |
| use_item | — | — |
| equip | {item_key_name} | {source} |
| goto_menu | {key_menu} | — |
| menu | {key_menu} | {action} |
| start_again | — | — |

`back_from_menu` accepts a `source_key_menu` argument and navigates to its parent using the `parent_menu` mapping. If `source_key_menu` is `inventory` or `inventory_select`, resets inventory state. Sets `opened_menu = PARENT_MENU[source_key_menu]` (may be `null` to close overlay) and calls `continue_run`.

**Examples**:
- `goto_menu:menu_expanse` — open main menu
- `menu:menu_expanse:new_game` — start new game from main menu
- `menu:menu_recall:heal` — buy health upgrade
- `back_from_menu:inventory` — close inventory overlay
- `start_again` — start over after death

## State types

Computed from log in `ui_builder.get_state_type`, never stored (except `menu_context["type"]` for overlay recovery).

| state_type | trigger |
|---|---|
| explore | move log, combat_ended, continue |
| combat | move with enemies, attack without combat_ended |
| dead | death log |

## Inventory system

- `equipped_items` — dict‑container `{"equipped_weapon": {}, "equipped_armour": {}}`. Each slot is a separate container addressable as `source`/`destination` in `StateWrapper.get_container`. Slot determined automatically via `ITEMS[key_name]["type"]`.
- `equip` action: moves item from `inventory`/`room_loot` → `equipped_weapon`/`equipped_armour`, displacing current item in slot back to `inventory`.
- `unequip`: implemented via `move_item_to:inventory` with `source=equipped_weapon`/`equipped_armour`.
- `use_item`: consumes food (restores health) or triggers equip for weapon/armour.

## Menu system

For menu navigation, `menu_context` in `run_state` is used:

| Field | Description |
|---|---|
| `type` | Primary game type (`explore`/`combat`/`dead`/`entrance`), computed from log |
| `opened_menu` | Currently open menu (`null`/`inventory`/`menu_expanse`/`menu_recall`/`menu_help`/`dead`) |

- **Overlay menus** do not change `type`. Inventory (`inventory`) is a special case of an overlay.
- **Death screen** is an overlay with `opened_menu: "dead"`, `type: "dead"`.
- **Navigation**: `goto_menu:{menu}` buttons change `opened_menu`. `menu:{menu}:{action}` buttons perform actions within a menu.
- **Closing**: `back_from_menu` sets `opened_menu = PARENT_MENU[source_key_menu]` (may be `null` to close overlay) and calls `continue_run`.

**Parent menu hierarchy**: Navigation “Назад” uses explicit `parent_menu` mapping (`data/bridge_spec.json`):
  - `inventory_select` → `inventory`
  - `menu_recall` → `menu_expanse`
  - `menu_help` → `menu_expanse`
  - `inventory`, `dead` → `null` (close overlay)

## Naming

- `key_name` — dict key used in JSON files (e.g. `"apple"`, `"dragon"`)
- `text_name` — human-readable name from preset (e.g. `"яблоко"`, `"Дракон"`)
- `source` / `destination` — container key name: `"inventory"`, `"room_loot"`, `"equipped_weapon"`, `"equipped_armour"`
- `log` — dict returned by engine/system describing what happened
- `state` — full `run_state_template` dict
- `contract` — dict returned to UI: `{text, buttons, state_type}`
- `menu_context` — dict with `type` (primary game state) and `opened_menu` (current overlay)
- `parent_menu` — mapping of child menu to parent menu for back navigation (`data/bridge_spec.json`)

## JSON file structure

### data/log_templates.json
Contains log templates (copied with `.copy()` before mutation) and `run_state_template` (deep-copied on `init_run`).

Key templates: `move_log_template`, `combat_log_template`, `combat_consequence_log_template`, `dead_log_template`, `inventory_log_template`, `continue_run_log_template`, `run_state_template`.

### run_state (run_state_template shape)
```json
{
  "active": true,
  "menu_context": {
    "type": null,
    "opened_menu": null
  },
    "player": {
        "base_health", "current_health", "base_damage", "base_defence", "base_speed",
        "equipped_items": {"equipped_weapon": {}, "equipped_armour": {}},
        "inventory": {}
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
`parent_menu`: mapping of child menu to parent menu for back navigation (e.g., `"inventory_select" → "inventory"`).
`command_schemas`: argument definitions for each command (does not include `continue_run`).

### data/bridge_spec.json
`contract`: shape of the return contract.
`ui_labels`: action string → Russian label mapping for ui_builder.

### Room shape (inside floor.rooms)
```json
{
  "index": 0, "type": "room", "room_type": "combat",
  "text_name": "пещера", "mood": "затхло",
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
- [x] Telegram bot (aiogram handlers, keyboards, message editing/fallback)
- [x] Database UPSERT fixes (no NULL overwrites)
- [x] Button standardization (dataclass Button across codebase)
- [x] Parent‑menu navigation (`back_from_menu` uses `parent_menu` mapping)
- [x] Death handling (state cleanup, start_again)
- [x] Floor transition (down door handling)
- [x] use_item (food heal, weapon equip) & equip system
- [x] LLM text generation with hash cache

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

### 4. Output Modes & Structure

You operate in two strict modes depending on the user's prompt: **PLAN** (designing, proposing, analyzing) and **BUILD** (writing actual code, fixing bugs).

#### MODE A: PLAN (Used for new features, complex bug analysis, or when asked to plan)
Your goal is to prove the architectural fit before writing the full implementation. Follow this strict structure sorted by files:

1. **Где (Locations):** Exact file, class, or engine layer to be touched.
2. **Для чего:** One sentence summarizing what will be done.
3. **Почему (Architectural Justification):** Explain *why* this approach is chosen. Prove that it respects the Layered Architecture (Engine vs. Systems vs. UI), doesn't duplicate JSON data, and integrates cleanly with the existing `run_state`.
4. **Концепт (Concept Snippet):** A minimal, simplified Python snippet demonstrating the core mechanic, data shape, or function signature. DO NOT write the full implementation here.

#### MODE B: BUILD (Used for executing code, fixing errors, or when asked to write)
Your goal is to provide seamless, drop-in code modifications. Follow this strict structure:

1. **Что изменено (Changes):** Bulleted list of modifications.
2. **Где (Target):** `file_path -> ClassName -> function_name`.
3. **Как работает (Mechanics):** One concise sentence explaining the logic of the change.
4. **Код (Implementation):**
   - For modifying existing code provide enough surrounding context lines so the change is easy to locate.
   - For entirely new functions/classes just write new code.
   - **DO NOT** rewrite the entire file. Provide only the relevant blocks.

**CRITICAL:** Do not leak your internal reasoning/thinking process into the final output. Give me only the raw, direct result.
