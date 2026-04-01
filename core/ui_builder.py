from data.presets import UI_LABELS, ENEMIES, ITEMS, Button
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

def get_game_buttons(log: dict, state: dict, state_type: str) -> list[Button]:
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
        return menu_buttons(state, opened_menu)

    match state_type:
        case "dead":
            return _dead_buttons()
        case "combat":
            return _combat_buttons(state)
        case "explore":
            return _explore_buttons(state)
        case _:
            return _explore_buttons(state)

def _explore_buttons(state: dict) -> list[Button]:
    buttons = []

    floor = state["floor"]
    room_index = floor["current_room_index"]
    room = floor["rooms"][room_index]
    doors = room.get("doors", {})

    if doors.get("forward") is not None:
        buttons.append(Button(label=UI_LABELS["move:forward"], action="move:forward"))

    if doors.get("backward") is not None:
        buttons.append(Button(label=UI_LABELS["move:backward"], action="move:backward"))

    if doors.get("left") is not None:
        buttons.append(Button(label=UI_LABELS["move:left"], action="move:left"))

    if doors.get("right") is not None:
        buttons.append(Button(label=UI_LABELS["move:right"], action="move:right"))

    if doors.get("down"):
        buttons.append(Button(label=UI_LABELS["move:down"], action="move:down"))

    if floor.get("fork_stack"):
        buttons.append(Button(label=UI_LABELS["move:to_fork"], action="move:to_fork"))

    buttons.append(Button(label=UI_LABELS["inventory_open:inventory"], action="inventory_open:inventory"))
    buttons.append(Button(label=UI_LABELS["inventory_open:room_loot"], action="inventory_open:room_loot"))

    return buttons


def _combat_buttons(state: dict) -> list[Button]:
    buttons = []

    combat_state = state.get("combat_state", {})
    enemies = combat_state.get("enemies") or {}

    for key_name, data in enemies.items():
        if data.get("health", 0) > 0:
            enemy_text_name = ENEMIES[key_name]["text_name"]
            enemy_hp = data["health"]
            label = f"{UI_LABELS['attack']} {enemy_text_name} ({enemy_hp} HP)"
            buttons.append(Button(label=label, action=f"attack:{key_name}"))

    buttons.append(Button(label=UI_LABELS["inventory_open:inventory"], action="inventory_open:inventory"))
    # buttons.append({"label": UI_LABELS["defence"], "action": "defence"})

    return buttons


def _inventory_buttons(state: dict) -> list[Button]:
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

    buttons.append(Button(label=UI_LABELS["buttons_splitter"], action="noop"))

    for key_name in loot_source:
        text_name = ITEMS[key_name]["text_name"]
        buttons.append(Button(label=text_name, action=f"inventory_select:{key_name}:{loot_source_key_name}"))

    buttons.append(Button(label=UI_LABELS["back_from_menu"], action="back_from_menu:inventory"))

    return buttons

def _inventory_select_buttons(state: dict) -> list[Button]:
    buttons = []

    inventory_state = state["inventory_state"]
    selected_item_key_name = inventory_state["selected_item_key_name"]
    selected_item_source = inventory_state["selected_item_source"]
    loot_source_key_name = inventory_state["loot_source"]

    text_name = ITEMS[selected_item_key_name]["text_name"]

    destination = loot_source_key_name if selected_item_source == "inventory" else "inventory"
    buttons.append(Button(label=f"[ {text_name} ]", action="noop"))

    buttons.append(Button(label=f"{UI_LABELS['move_item_to']} {UI_LABELS[destination]}", action=f"move_item_to:{destination}"))

    buttons.append(Button(label=f"{UI_LABELS['use_item']}", action="use_item"))

    buttons.append(Button(label=UI_LABELS["back_from_menu"], action="back_from_menu:inventory_select"))

    return buttons

def _dead_buttons() -> list[Button]:
    return [
        Button(label=UI_LABELS["start_again"], action="start_again"),
        Button(label=UI_LABELS["goto_menu:menu_main"], action="goto_menu:menu_main")
    ]

def menu_buttons(state: dict, key_menu: str) -> list[Button]:
    buttons = []

    if key_menu == "menu_main":
            buttons.append(Button(label=UI_LABELS["menu:menu_main:new_game"], action="menu:menu_main:new_game"))
            if state.get("active"):
                buttons.append(Button(label=UI_LABELS["menu:menu_main:continue"], action="menu:menu_main:continue"))
            buttons.append(Button(label=UI_LABELS["goto_menu:menu_upgrades"], action="goto_menu:menu_upgrades"))
            # Button(label=UI_LABELS["menu:menu_main:help"], action="goto_menu:menu_help")
    elif key_menu == "menu_upgrades":
        buttons = [
            Button(label=UI_LABELS["menu:menu_upgrades:heal"], action="menu:menu_upgrades:heal"),
            Button(label=UI_LABELS["menu:menu_upgrades:damage"], action="menu:menu_upgrades:damage"),
            Button(label=UI_LABELS["menu:menu_upgrades:defence"], action="menu:menu_upgrades:defence"),
            Button(label=UI_LABELS["back_from_menu"], action="back_from_menu:menu_upgrades")
            # Button(label=UI_LABELS["menu:menu_upgrades:back"], action="goto_menu:menu_main")
        ]
    elif key_menu == "menu_help":
        buttons = [
            Button(label=UI_LABELS["back_from_menu"], action="back_from_menu:menu_help")
        ]
    elif key_menu == "dead":
        return _dead_buttons()

    return buttons
