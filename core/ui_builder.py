from data.presets import UI_LABELS, ENEMIES, ITEMS
from core.state_wrapper import StateWrapper


def get_state_type(log: dict, state: dict) -> str:
    # TODO: сделай обработку смерти. в комбате поставь проверку и делай просто забег "active": False
    log_type = log["type"]

    if log_type == "death":
        return "dead"

    if log_type == "entrance":
        return "entrance"

    if log_type == "combat":
        if log["combat_ended"]:
            return "explore"

        return "combat"

    if log_type == "move":
        if log["event"] == "combat":
            return "combat"

        return "explore"

    if log_type == "inventory":
        return state["menu_context"]["type"]

    if log_type == "continue":
        return state["menu_context"]["type"]

    return state["menu_context"]["type"]

def get_buttons(log: dict, state: dict, state_type: str) -> list:
    menu_context = state["menu_context"]
    opened_menu = menu_context["opened_menu"]

    if opened_menu is not None:
        if opened_menu == "inventory":
            # Current inventory logic
            if log["type"] == "inventory":
                if log["action"] == "open":
                    return _inventory_buttons(state)
                if log["action"] in ("select", "move"):
                    return _inventory_select_buttons(state)
            # Fallback for inventory
            return _inventory_buttons(state)
        return _menu_buttons(state, opened_menu)

    match state_type:
        case "dead":
            return _dead_buttons()
        case "combat":
            return _combat_buttons(state)
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

    if doors.get("forward") is not None:
        buttons.append({"label": UI_LABELS["move:forward"], "action": "move:forward"})

    if doors.get("backward") is not None:
        buttons.append({"label": UI_LABELS["move:backward"], "action": "move:backward"})

    if doors.get("left") is not None:
        buttons.append({"label": UI_LABELS["move:left"], "action": "move:left"})

    if doors.get("right") is not None:
        buttons.append({"label": UI_LABELS["move:right"], "action": "move:right"})

    if doors.get("down"):
        buttons.append({"label": UI_LABELS["move:down"], "action": "move:down"})

    if floor.get("fork_stack"):
        buttons.append({"label": UI_LABELS["move:to_fork"], "action": "move:to_fork"})

    buttons.append({"label": UI_LABELS["inventory_open:inventory"], "action": "inventory_open:inventory"})
    buttons.append({"label": UI_LABELS["inventory_open:room_loot"], "action": "inventory_open:room_loot"})

    return buttons


def _combat_buttons(state: dict) -> list:
    buttons = []

    combat_state = state.get("combat_state", {})
    enemies = combat_state.get("enemies") or {}

    for key_name, data in enemies.items():
        if data.get("health", 0) > 0:
            enemy_text_name = ENEMIES[key_name]["text_name"]
            enemy_hp = data["health"]
            label = f"{UI_LABELS['attack']} {enemy_text_name} ({enemy_hp} HP)"
            buttons.append(Button(label=label, action=f"attack:{key_name}"))

    buttons.append({"label": UI_LABELS["inventory_open:inventory"], "action": "inventory_open:inventory"})
    # buttons.append({"label": UI_LABELS["defence"], "action": "defence"})

    return buttons


def _inventory_buttons(state: dict) -> list:
    state_wrapped = StateWrapper(state)
    buttons = []

    inventory_state = state["inventory_state"]
    # selected_item_key_name = inventory_state["selected_item_key_name"]
    # selected_item_source = inventory_state["selected_item_source"]
    loot_source_key_name = inventory_state["loot_source"]

    inventory = state_wrapped.get_container("inventory")
    loot_source = state_wrapped.get_container(loot_source_key_name)


    for key_name in inventory:
        text_name = ITEMS[key_name]["text_name"]
        buttons.append(Button(label=text_name, action=f"inventory_select:{key_name}:inventory"))

    buttons.append({"label": UI_LABELS["buttons_splitter"], "action": "noop"})

    for key_name in loot_source:
        text_name = ITEMS[key_name]["text_name"]
        buttons.append(Button(label=text_name, action=f"inventory_select:{key_name}:{loot_source_key_name}"))

    buttons.append({"label": UI_LABELS["back_the_menu"], "action": "back_the_menu"})

    return buttons

def _inventory_select_buttons(state: dict) -> list:
    buttons = []

    inventory_state = state["inventory_state"]
    selected_item_key_name = inventory_state["selected_item_key_name"]
    selected_item_source = inventory_state["selected_item_source"]
    loot_source_key_name = inventory_state["loot_source"]

    text_name = ITEMS[selected_item_key_name]["text_name"]

    destination = loot_source_key_name if selected_item_source == "inventory" else "inventory"
    buttons.append({"label": f"[ {text_name} ]",
                    "action": "noop"})

    buttons.append({"label": f"{UI_LABELS["move_item_to"]} {UI_LABELS[destination]}",
                    "action": f"move_item_to:{destination}"})

    buttons.append({"label": f"{UI_LABELS["use_item"]}",
                    "action": "use_item"})

    buttons.append({"label": UI_LABELS["back_the_menu"],
                    "action": "back_the_menu"})

    return buttons

def _dead_buttons() -> list:
    return [
        {"label": UI_LABELS["start_again"], "action": "start_again"},
        {"label": UI_LABELS["goto_menu:main_menu"], "action": "goto_menu:main_menu"}
    ]

def _menu_buttons(state: dict, menu: str) -> list:
    buttons = []

    if menu == "main_menu":
        buttons = [
            {"label": UI_LABELS["menu:main_menu:new_game"], "action": "menu:main_menu:new_game"},
            {"label": UI_LABELS["menu:main_menu:continue"], "action": "menu:main_menu:continue"},
            {"label": UI_LABELS["menu:main_menu:upgrades"], "action": "goto_menu:upgrades_menu"},
            {"label": UI_LABELS["menu:main_menu:help"], "action": "goto_menu:help_menu"}
        ]
    elif menu == "upgrades_menu":
        buttons = [
            {"label": UI_LABELS["menu:upgrades_menu:heal"], "action": "menu:upgrades_menu:heal"},
            {"label": UI_LABELS["menu:upgrades_menu:damage"], "action": "menu:upgrades_menu:damage"},
            {"label": UI_LABELS["menu:upgrades_menu:defence"], "action": "menu:upgrades_menu:defence"},
            {"label": UI_LABELS["menu:upgrades_menu:back"], "action": "goto_menu:main_menu"}
        ]
    elif menu == "help_menu":
        buttons = [
            {"label": UI_LABELS["menu:help_menu:back"], "action": "goto_menu:main_menu"}
        ]
    elif menu == "dead":
        return _dead_buttons()

    # Add back button for all menus except main and dead
    if menu not in ("main_menu", "dead"):
        buttons.append({"label": UI_LABELS["back_the_menu"], "action": "back_the_menu"})

    return buttons
