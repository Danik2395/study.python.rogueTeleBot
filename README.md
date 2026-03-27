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
| goto_menu | main_menu, upgrades_menu, help_menu, dead | — |
| menu | {menu_type} | {action} |
| back_the_menu | — | — |
| start_again | — | — |


# Buttons layout

## Menu mode (overlay)

### Main menu (opened_menu: "main_menu")
- menu:main_menu:new_game
- menu:main_menu:continue
- goto_menu:upgrades_menu
- goto_menu:help_menu

### Upgrades menu (opened_menu: "upgrades_menu")
- menu:upgrades_menu:heal
- menu:upgrades_menu:damage
- menu:upgrades_menu:defence
- goto_menu:main_menu

### Help menu (opened_menu: "help_menu")
- goto_menu:main_menu

## Explore mode

- move:{direction}
- move:to_fork
- inventory_open:inventory
- inventory_open:room_loot
- goto_menu:main_menu

## Combat mode

- attack:{enemy}
- inventory_open:inventory

## Inventory mode (overlay)

- back_the_menu
- inventory_select:{item_key_name}:inventory (from player inventory)
    - move_item_to:room_loot
    - use_item
- `------`
- inventory_select:{item_key_name}:{loot_source} (from room loot)
    - move_item_to:inventory
    - use_item

## Death mode (overlay)

- start_again
- goto_menu:main_menu


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
