"""
Module for stateless engine.
Operates systems
"""

from core.systems.floor_system import FloorSystem
from core.systems.combat_system import CombatSystem
from core.systems.move_system import MoveSystem
from core.systems.loot_system import LootSystem
from log_handler import LogHandler
from data.presets import LOG
from data.presets import RULES

import copy
from typing import Any


def init_run() -> tuple[dict[str, Any], dict[str, Any]]:
    """
    return tuple[gen_entrance_log, new_run_state]
    """

    new_run_state = copy.deepcopy(LOG["run_state_template"])

    floor = new_run_state["floor"]

    # Because door generation method needs floor index
    floor["index"] = 1
    floor["current_room_index"] = 0

    floor_system = FloorSystem(floor)

    gen_entrance_log = floor_system.gen_entrance()

    return gen_entrance_log, new_run_state


def move(direction: str, active_run_state: dict) -> dict[str, Any]:
    """
    return move_log
    """

    floor = active_run_state["floor"]

    move_system = MoveSystem(floor)

    while True:
        move_log = move_system.move(direction)

        if not move_log["is_new_room"] and not move_log["room_index"]:
            return move_log

        if move_log["is_new_room"] == True:
            floor_system = FloorSystem(floor)
            opposite_direction = RULES["opposite_direction"][direction]
            floor_system.gen_room(move_system.current_room_doors, opposite_direction)

            continue

        current_room_index = active_run_state["floor"]["current_room_index"]
        current_room = floor["rooms"][current_room_index]

        if current_room["enemies"] and not current_room["cleared"]:
            active_run_state["combat_state"]["in_combat"] = True

            move_log["event"] = "combat"
            active_run_state["combat_state"]["in_combat"] = True

        return move_log


def move_to_fork(active_run_state: dict) -> dict[str, Any]:
    """
    return move_log
    """

    floor = active_run_state["floor"]

    move_system = MoveSystem(floor)

    move_log = move_system.move_to_fork()

    return move_log


def attack(target_enemy_name: str, active_run_state: dict) -> dict:
    """
    return combat_log
    """

    floor = active_run_state["floor"]

    player = active_run_state["player"]
    room_enemies = floor["rooms"][floor["current_room_index"]]["enemies"]
    combat_state = active_run_state["combat_state"]

    combat_system = CombatSystem(player, room_enemies, combat_state)

    combat_log = combat_system.proceed_action("attack", target_enemy_name)

    return combat_log
