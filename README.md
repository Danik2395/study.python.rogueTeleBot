# Button structure

`command:arg_0:arg_1:arg_n`

| Command | arg_0 | arg_1 |
|---|---|---|
| cmd_start | — | — |
| init_run | — | — |
| move | forward, backward, left, right, down, to_fork | — |
| attack | {enemy_key_name} | — |
| inventory_open | inventory (default), room_loot | — |
| inventory_select | {item_key_name} | {source} |
| move_item_to | {destination} | — |
| use_item | — | — |
| equip | {item_key_name} | {source} |
| goto_menu | {key_menu} | — |
| menu | {key_menu} | {action} |
| back_from_menu | {source_key_menu} | — |
| start_again | — | — |


# Buttons layout

## Menu mode (overlay)

### Main menu (opened_menu: "menu_expanse")
- menu:menu_expanse:new_game
- menu:menu_expanse:continue
- goto_menu:menu_recall

### Recall menu (opened_menu: "menu_recall")
- menu:menu_recall:heal
- menu:menu_recall:damage
- menu:menu_recall:defence
- back_from_menu:menu_updrades

### Help menu (opened_menu: "menu_help")
- goto_menu:menu_expanse

## Explore mode

- move:{direction}
- move:to_fork
- inventory_open:inventory
- inventory_open:room_loot

## Combat mode

- attack:{enemy}
- inventory_open:inventory

## Inventory mode (overlay)

- inventory_select:{item_key_name}:equipped_items (from equipped slots)
    - move_item_to:inventory (unequip)
- equipped slots: weapon, armour (displayed as empty if not equipped)
- `------`
- inventory_select:{item_key_name}:inventory (from player inventory)
    - move_item_to:room_loot
    - use_item (if food) / equip (if weapon/armour)
- `------`
- inventory_select:{item_key_name}:{loot_source} (from room loot)
    - move_item_to:inventory
    - use_item (if food) / equip (if weapon/armour)
- back_from_menu:inventory

## Death mode (overlay)

- start_again
- goto_menu:menu_expanse


# Inventory

Overlay mode (does not writes "inventory" into state)
Opens in split mode.
When item is selected item actions menu opens.
When item is moved to the other place menu remains the same letting select another action

## JOSN

### log_template

- `action`
    - open
        Set `source` if it is avaliable
    - move
        Item from `source` to `move_destination`
    - select
        Sets `source` of selected item and `item_name`
- `source`
    Stands for the source from where to display buttons and to set `loot_source` or for the source from where to move items

### inventory_state

- `loot_source`
    Items source that is not inventory
- `selected_item_source`
    Source of the selected item

# Meta Progression (Expanse & Recall)

## Core Navigation & States

- **Expanse** (formerly `menu_main`)
    The primary hub. A metaphysical void devoid of physical forms, existing purely as a space of consciousness.
- **Recall** (formerly `menu_upgtrades`)
    The upgrade and progression system. Represents the act of recovering lost personality fragments.

## Notes & Reality Interruption

- **Interruption Logic**
    Discovering a Note acts as a reality trigger. It forces a full-screen overlay, interrupting the game flow and compelling the player to read the text.
- **Lore & Keys**
    Notes serve a dual purpose:
    - Reveal narrative lore.
    - Act as permanent memory fragments added to recall (upgrade) in the Expanse.

## Progression Flow

- **Delayed Activation**
    Stats and skills cannot be improved immediately upon discovering a Note.
- **Recall Cycle**
    1. **Discover**: Find a Note while exploring the Labyrinth or gain memory fragments in the combat.
    2. **Return**: Transition back to the Expanse by death. Memory fragments only transfered in the entrance rooms.
    3. **Recall**: Spend accumulated memory fragments in the Recall menu to activate the specific stats.


# TODO

- [x] Set up core codebase
- [x] Enable terminal debugging
- [x] Create  an asynchronous database
- [x] Develop an asynchronous bot
- [x] Integrate LLM
- [ ] Add new features
    - [x] Add meta progression
    - [ ] Add camp room
    - [ ] Add flee chance
    - [ ] Develop an user interface in bot
- [ ] Neat the balance
