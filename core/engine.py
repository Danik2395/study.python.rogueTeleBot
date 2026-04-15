"""
Module for stateless engine.
Operates systems
"""

import random

from core.systems.floor_system import FloorSystem
from core.systems.combat_system import CombatSystem
from core.systems.move_system import MoveSystem
from core.systems.inventory_system import InventorySystem
from core.systems.recall_system import RecallSystem
from core.entities import Player
# from core.log_handler import LogHandler
from core.state_wrapper import StateWrapper
from data.presets import RULES, LOG, ENEMIES, LAYOUT

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
    floor_index = floor["index"] = 1
    floor["current_room_index"] = 0

    floor_system = FloorSystem(floor)

    gen_entrance_log = floor_system.gen_entrance()
    gen_entrance_log["current_floor_index"] = floor_index

    # User data logic
    progress = user_data["progress"]
    progress["total_runs"] += 1

    global_recalls = user_data["global_recalls"]
    player = new_run_state["player"]

    stats = ["health", "damage", "defence", "speed"]
    for s in stats:
        player[f"base_{s}"] += global_recalls[f"plus_{s}"]

    player["current_health"] = player["base_health"]

    return gen_entrance_log, new_run_state


def move(direction: str, run_state: dict) -> dict[str, Any]:
    """
    return move_log
    """

    floor = run_state["floor"]

    move_system = MoveSystem(floor)

    move_log: dict = {}
    is_new_room: bool = False # For now it's like this. Idk how to do it other way
    while True:
        move_log.update(move_system.move(direction))

        if not move_log["is_new_room"] and move_log["room_index"] is None:
            return move_log

        if move_log["is_new_room"]:
            floor_system = FloorSystem(floor)
            opposite_direction = RULES["opposite_direction"][direction]
            floor_system.gen_room(move_system.current_room, opposite_direction)
            is_new_room = True

            continue
        move_log["is_new_room"] = is_new_room

        current_room_index = floor["current_room_index"]
        current_room = floor["rooms"][current_room_index]
        current_room_enemies = current_room["enemies"]

        if current_room_enemies and not current_room["cleared"]:
            combat_state = run_state["combat_state"]

            combat_state["in_combat"] = True
            combat_state["flee_direction"] = RULES["opposite_direction"][direction]
            move_log["event"] = "combat"

            # We need to set enemies so buttons append correctly
            combat_state["enemies"] = CombatSystem.build_state_enemies(current_room_enemies)


        if is_new_room and move_log["room_type"] == "camp":
            dirty_camp_health_increase_limits = RULES["move"]["camp_health_increase_limits"]
            camp_health_increase_limits = random.choice(dirty_camp_health_increase_limits)

            low, high, *buff = camp_health_increase_limits
            camp_health_increase = random.randint(low, high)

            player = run_state["player"]
            new_health = min(player["current_health"] + camp_health_increase, player["base_health"])
            health_increase_delta = new_health - player["current_health"]
            player["current_health"] = new_health

            consequence = LOG["move_consequence_log_template"]
            consequence["health_delta"] = health_increase_delta

            move_log["consequence"] = consequence
            move_log["event"] = "heal"

        return move_log


def move_to_fork(run_state: dict) -> dict[str, Any]:
    """
    return move_log
    """

    floor = run_state["floor"]

    move_system = MoveSystem(floor)

    move_log = move_system.move_to_fork()

    return move_log


def move_down(run_state: dict, user_data: dict) -> dict[str, Any]:
    """
    return floor_entrance_log
    """

    floor = run_state["floor"]
    current_room_index = floor["current_room_index"]
    current_room = floor["rooms"][current_room_index]

    if current_room["doors"].get("down") is not True:
        move_log = LOG["move_log_template"].copy()
        move_log["direction"] = "down"
        return move_log

    floor["index"] += 1
    floor["current_room_index"] = 0
    floor["fork_stack"] = []
    floor["down_in_room"] = -1
    floor["rooms"] = []

    floor_system = FloorSystem(floor)
    floor_entrance_log = floor_system.gen_entrance()
    floor_entrance_log["current_floor_index"] = floor["index"]
    floor_entrance_log["biom_text_name"] = floor["biom_text_name"]

    progress = user_data["progress"]
    if floor["index"] > progress["max_floor_reached"]:
        progress["max_floor_reached"] = floor["index"]

    player = run_state["player"]
    global_recalls = user_data["global_recalls"]
    global_recalls["memory_fragments"] += player["memory_fragments"]
    player["memory_fragments"] = 0

    combat_state = run_state["combat_state"]
    combat_state["in_combat"] = False
    combat_state["enemies"] = None
    combat_state["turns"] = None
    combat_state["flee_direction"] = None

    inventory_state = run_state["inventory_state"]
    inventory_state["selected_item_key_name"] = None
    inventory_state["selected_item_source"] = None
    inventory_state["loot_source"] = None

    return floor_entrance_log


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

    combat_log: dict# = {}
    try:
        combat_log = combat_system.proceed_action("attack", target_enemy_name)

    except player_dead_exception as d:
        run_state["active"] = False
        # Set death overlay
        run_state["menu_context"]["opened_menu"] = "dead"
        run_state["menu_context"]["type"] = "dead"

        return d.dead_log

    consequence = combat_log["consequence"]
    for c in consequence:
        if c["dead"]:
            enemy_key_name = c["target"]
            player["memory_fragments"] += ENEMIES[enemy_key_name]["memory_fragments"]


    if combat_log["combat_ended"]:
        room_enemies.clear()
        current_room["cleared"] = True

    return combat_log

def defence(run_state: dict) -> dict:
    floor = run_state["floor"]
    current_room_index = floor["current_room_index"]
    current_room = floor["rooms"][current_room_index]

    player = run_state["player"]
    room_enemies = current_room["enemies"]
    combat_state = run_state["combat_state"]

    combat_system = CombatSystem(player, room_enemies, combat_state)

    try:
        return combat_system.proceed_action("defence")
    except player_dead_exception as d:
        run_state["active"] = False
        run_state["menu_context"]["opened_menu"] = "dead"
        run_state["menu_context"]["type"] = "dead"
        return d.dead_log

def flee(run_state: dict) -> dict:
    floor = run_state["floor"]
    biom_key = floor["biom_key_name"]

    flee_chance_limits = LAYOUT["bioms"][biom_key]["flee_chance_limits"]

    current_room_index = floor["current_room_index"]
    current_room = floor["rooms"][current_room_index]
    player = run_state["player"]
    combat_state = run_state["combat_state"]

    combat_system = CombatSystem(player, current_room["enemies"], combat_state)

    try:
        combat_log = combat_system.proceed_action("flee", flee_chance_limits=flee_chance_limits)
    except player_dead_exception as d:
        run_state["active"] = False
        run_state["menu_context"]["opened_menu"] = "dead"
        run_state["menu_context"]["type"] = "dead"
        return d.dead_log

    if combat_log.get("fled"):
        flee_direction = combat_state["flee_direction"]
        move_system = MoveSystem(floor)
        move_log = move_system.move(flee_direction)
        move_log["event"] = "flee"
        combat_state["in_combat"] = False
        combat_state["turns"] = None
        combat_state["enemies"] = None
        combat_state["flee_direction"] = None
        return move_log

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

def inventory_move(destination_key_name: str, run_state: dict, count: int | None = None) -> dict:
    inventory_state = run_state["inventory_state"]
    state_wrapped = StateWrapper(run_state)

    inventory_system = InventorySystem(state_wrapped.get_container, inventory_state)
    return inventory_system.move_item(destination_key_name, count)


def inventory_use(run_state: dict) -> dict:
    inventory_state = run_state["inventory_state"]
    player = run_state["player"]
    state_wrapped = StateWrapper(run_state)
    inventory_system = InventorySystem(state_wrapped.get_container, inventory_state)
    return inventory_system.use_item(player)


def inventory_unequip(slot: str, run_state: dict) -> dict:
    player = run_state["player"]
    state_wrapped = StateWrapper(run_state)
    inventory_system = InventorySystem(state_wrapped.get_container, run_state["inventory_state"])
    return inventory_system.unequip(slot, player)

def recall_stat(user_data: dict, stat: str) -> dict:
    recall_system = RecallSystem(user_data)

    return recall_system.recall_stat(stat)
