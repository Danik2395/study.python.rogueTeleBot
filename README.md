# Button structure

`command:arg_0:arg_1:arg_n`

|Command|arg\_0|arg\_1|
|---|---|---|
|init_run|-|-|
|continue_run|-|-|
|move|forward,<br>backward,<br>left,<br>right,<br>down,<br>to_fork|-|
|attack|{enemy_key_name}|-|
|inventory_open|inventory (default, always enabled),<br>{source}|-|
|inventory_select|{item_key_name}|{source}|
|inventory_move_item|{destination}|-|
|back_the_menu<br>(for now only works for overlay menu, and returns to the last state)|-|-|


# Buttons layout

## General mode

- help

## Menu mode

### Start screen
- enter_game

### Game menu
- init_new_run
    - yes
    - no
    - back_the_menu:init_new_run
- continue_run
- upgrades
    - some_upgrade_buttons
    - back_the_menu:upgrades

## Explore mode

- move:{direction}
- move:to_fork
- inventory_open:inventory
- inventory_open:{loot_source}

## Combat mode

- attack:{enemy}
- defence
- heal
- inventory_open:inventory

## Inventory mode

- back_the_menu:inventory_open
- inventory_select:{item}:{source} (inventory)
    - use_item
    - inventory_move_item:{destination}
    - back_the_menu:inventory:select
- `------`
- inventory_select:{item}:{source} (optional loot_source)
    - use_item
    - inventory_move_item:{destination}
    - back_the_menu:inventory:select

## Death mode

- start_again
- back_the_menu:death


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
