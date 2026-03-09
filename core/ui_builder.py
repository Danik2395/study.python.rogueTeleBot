from data.presets import UI_LABELS, ENEMIES, ITEMS


def get_state_type(log: dict) -> str:
    log_type = log.get("type")

    if log_type == "death":
        return "dead"

    if log_type == "combat":
        if log.get("combat_ended"):
            return  "explore"
        return "combat"

    if log_type == "move":
        if log.get("event") == "combat":
            return "combat"
        return "explore"

    if log_type == "item":
        if not log.get("is_items_left"):
            return "explore"
        return "loot"

    return "explore"


def get_buttons(log: dict, state: dict, state_type: str) -> list:
    match state_type:
        case "dead":
            return _dead_buttons()
        case "combat":
            return _combat_buttons(state)
        case "loot":
            return _loot_buttons(state)
        case "explore":
            return _explore_buttons(state)
        case _:
            return _explore_buttons(state)


def _explore_buttons(state: dict) -> list:
    buttons = []

    floor = state["floor"]
    room_index = floor["current_room_index"]
    room = floor["rooms"][room_index]
    doors = room.get("doors", {})

    if doors.get("forward"):
        buttons.append({"label": UI_LABELS["move_forward"], "action": "move_forward"})

    if doors.get("backward"):
        buttons.append({"label": UI_LABELS["move_backward"], "action": "move_backward"})

    if doors.get("left"):
        buttons.append({"label": UI_LABELS["move_left"], "action": "move_left"})

    if doors.get("right"):
        buttons.append({"label": UI_LABELS["move_right"], "action": "move_right"})

    if doors.get("down"):
        buttons.append({"label": UI_LABELS["move_down"], "action": "move_down"})

    if floor.get("fork_stack"):
        buttons.append({"label": UI_LABELS["move_to_fork"], "action": "move_to_fork"})

    buttons.append({"label": UI_LABELS["inventory"], "action": "inventory"})

    return buttons


def _combat_buttons(state: dict) -> list:
    buttons = []

    combat_state = state.get("combat_state", {})
    enemies = combat_state.get("enemies") or {}

    for name, data in enemies.items():
        if data.get("current_health", 0) > 0:
            enemy_name = ENEMIES[name]
            enemy_hp = data["current_health"]
            label = f"{UI_LABELS['attack']} {enemy_name} ({enemy_hp} HP)"
            buttons.append({"label": label, "action": f"attack_{name}"})

    # buttons.append({"label": UI_LABELS["defence"], "action": "defence"})

    return buttons


def _loot_buttons(state: dict) -> list:
    buttons = []

    floor = state["floor"]
    room_index = floor["current_room_index"]
    room = floor["rooms"][room_index]
    loot = room.get("loot") or []

    for name in loot:
        item_name = ITEMS[name]
        label = f"Взять {item_name}"
        buttons.append({"label": label, "action": f"take_{name}"})

    buttons.append({"label": UI_LABELS["menu_back"], "action": "menu_back"})

    return buttons


def _dead_buttons() -> list:
    return [
        {"label": UI_LABELS["start_again"], "action": "start_again"},
        {"label": UI_LABELS["to_game_screen"], "action": "to_game_screen"}
    ]
