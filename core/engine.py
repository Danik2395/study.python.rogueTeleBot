"""
Module for stateless engine.
Operates systems
"""

from core.systems.floor_system import FloorSystem
from core.systems.combat_system import CombatSystem
from core.systems.move_system import MoveSystem
from core.systems.inventory_system import InventorySystem
from core.entities import Player
# from core.log_handler import LogHandler
from core.state_wrapper import StateWrapper
from data.presets import LOG
from data.presets import RULES

import copy
from typing import Any

player_dead_exception = Player.Dead


def init_data() -> dict[str, Any]:
    """
    return user_data inited template
    """

    new_user_data = copy.deepcopy(LOG["user_data_template"])

    return new_user_data


def init_run(user_data: dict) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    return tuple[gen_entrance_log, new_run_state]
    """

    # Run state logic
    new_run_state = copy.deepcopy(LOG["run_state_template"])
    new_run_state["active"] = True

    floor = new_run_state["floor"]

    # Because door generation method needs floor index
    floor["index"] = 1
    floor["current_room_index"] = 0

    floor_system = FloorSystem(floor)

    gen_entrance_log = floor_system.gen_entrance()

    # User data logic
    progress = user_data["progress"]
    progress["total_runs"] += 1

    global_upgrades = user_data["global_upgrades"]
    player = new_run_state["player"]

    stats = ["health", "damage", "defence", "speed"]
    for s in stats:
        player[f"base_{s}"] += global_upgrades[f"plus_{s}"]

    player["current_health"] = player["base_health"]


    return gen_entrance_log, new_run_state


def move(direction: str, run_state: dict) -> dict[str, Any]:
    """
    return move_log
    """

    floor = run_state["floor"]

    move_system = MoveSystem(floor)

    while True:
        move_log = move_system.move(direction)

        if not move_log["is_new_room"] and move_log["room_index"] is None:
            return move_log

        if move_log["is_new_room"]:
            floor_system = FloorSystem(floor)
            opposite_direction = RULES["opposite_direction"][direction]
            floor_system.gen_room(move_system.current_room, opposite_direction)

            continue

        current_room_index = floor["current_room_index"]
        current_room = floor["rooms"][current_room_index]
        current_room_enemies = current_room["enemies"]

        if current_room_enemies and not current_room["cleared"]:
            combat_state = run_state["combat_state"]

            combat_state["in_combat"] = True
            move_log["event"] = "combat"

            # We need to set enemies so buttons append correctly
            combat_state["enemies"] = CombatSystem.build_state_enemies(current_room_enemies)

        return move_log


def move_to_fork(run_state: dict) -> dict[str, Any]:
    """
    return move_log
    """

    floor = run_state["floor"]

    move_system = MoveSystem(floor)

    move_log = move_system.move_to_fork()

    return move_log


def attack(target_enemy_name: str, run_state: dict) -> dict:
    """
    return combat_log
    """

    floor = run_state["floor"]
    current_room_index = floor["current_room_index"]
    current_room = floor["rooms"][current_room_index]

    player = run_state["player"]
    room_enemies = current_room["enemies"]
    combat_state = run_state["combat_state"]

    combat_system = CombatSystem(player, room_enemies, combat_state)

    combat_log: dict = {}
    try:
        combat_log = combat_system.proceed_action("attack", target_enemy_name)

    except player_dead_exception as d:
        run_state["active"] = False
        # Set death overlay
        run_state["menu_context"]["opened_menu"] = "dead"
        run_state["menu_context"]["type"] = "dead"

        return d.dead_log

    if combat_log["combat_ended"]:
        room_enemies.clear()
        current_room["cleared"] = True

    return combat_log

def inventory_open(loot_source: str, run_state: dict) -> dict:
    log = LOG["inventory_log_template"].copy()
    log["action"] = "open"

    combat_state = run_state["combat_state"]
    is_in_combat = combat_state["in_combat"]

    source = loot_source if not is_in_combat else "inventory"
    log["source"] = source

    inventory_state = run_state["inventory_state"]
    inventory_state["loot_source"] = source

    # Open inventory overlay
    run_state["menu_context"]["opened_menu"] = "inventory"

    return log

def inventory_select(item_key_name: str, selected_item_source: str, run_state: dict) -> dict:
    log = LOG["inventory_log_template"].copy()
    log["action"] = "select"
    log["item_key_name"] = item_key_name
    log["source"] = selected_item_source

    inventory_state = run_state["inventory_state"]
    inventory_state["selected_item_key_name"] = item_key_name
    inventory_state["selected_item_source"] = selected_item_source

    return log

def inventory_move(destination_key_name: str, run_state: dict) -> dict:
    inventory_state = run_state["inventory_state"]
    state_wrapped = StateWrapper(run_state)

    inventory_system = InventorySystem(state_wrapped.get_container, inventory_state)
    return inventory_system.move_item(destination_key_name)
