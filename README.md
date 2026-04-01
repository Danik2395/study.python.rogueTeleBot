# Button structure

`command:arg_0:arg_1:arg_n`

| Command | arg_0 | arg_1 |
|---|---|---|
| init_run | — | — |
| continue_run | — | — |
| move | forward, backward, left, right, down, to_fork | — |
| attack | {enemy_key_name} | — |
| inventory_open | inventory (default), room_loot | — |
| inventory_select | {item_key_name} | {source} |
| move_item_to | {destination} | — |
| goto_menu | {key_menu} | — |
| menu | {key_menu} | {action} |
| back_from_menu | {source_key_menu} | — |
| start_again | — | — |


# Buttons layout

## Menu mode (overlay)

### Main menu (opened_menu: "menu_main")
- menu:menu_main:new_game
- menu:menu_main:continue
- goto_menu:menu_upgrades

### Upgrades menu (opened_menu: "menu_upgrades")
- menu:menu_upgrades:heal
- menu:menu_upgrades:damage
- menu:menu_upgrades:defence
- back_from_menu:menu_updrades

### Help menu (opened_menu: "menu_help")
- goto_menu:menu_main

## Explore mode

- move:{direction}
- move:to_fork
- inventory_open:inventory
- inventory_open:room_loot

## Combat mode

- attack:{enemy}
- inventory_open:inventory

## Inventory mode (overlay)

- back_from_menu:inventory
- inventory_select:{item_key_name}:inventory (from player inventory)
    - move_item_to:room_loot
    - use_item
- `------`
- inventory_select:{item_key_name}:{loot_source} (from room loot)
    - move_item_to:inventory
    - use_item

## Death mode (overlay)

- start_again
- goto_menu:menu_main


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


# TODO

- [x] Set up core codebase
- [x] Enable terminal debugging
- [x] Create  an asynchronous database
- [ ] Develop an asynchronous bot
- [ ] Develop an user interface in bot
- [ ] Integrate LLM
- [ ] Add new features
- [ ] Neat the balance
