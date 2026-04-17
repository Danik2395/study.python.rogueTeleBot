from data.presets import UI_LABELS, ENEMIES, ITEMS, Button
from core.state_wrapper import StateWrapper


def get_state_type(log: dict, state: dict) -> str:
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

def get_game_buttons(log: dict, state: dict, state_type: str, user_data: dict | None) -> list[Button]:
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
        return menu_buttons(state, opened_menu, user_data)

    match state_type:
        case "dead":
            return _dead_buttons()
        case "combat":
            return _combat_buttons(state)
        case "explore":
            return _explore_buttons(state)
        case "entrance":
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
            label = f"{UI_LABELS['combat:attack']} {enemy_text_name} ({enemy_hp} HP)"
            buttons.append(Button(label=label, action=f"combat:attack:{key_name}"))

    buttons.append(Button(label=UI_LABELS["combat:defence"], action="combat:defence"))
    buttons.append(Button(label=UI_LABELS["combat:flee"], action="combat:flee"))
    buttons.append(Button(label=UI_LABELS["inventory_open:inventory"], action="inventory_open:inventory"))

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

    # === Equipped items ===

    buttons.append(Button(label=UI_LABELS["inventory_splitter:equipped"], action="noop"))

    equipped_containers = state["player"]["equipped_items"]
    emojis = UI_LABELS["emojis"]
    for container_key, container in equipped_containers.items():
        slot = container_key.replace("equipped_", "")
        if container:
            item_key_name, = container
            text_name = ITEMS[item_key_name]["text_name"]
            buttons.append(Button(label=f"{emojis[slot]} [ {text_name} ]", action=f"inventory_select:{item_key_name}:{container_key}"))
        else:
            buttons.append(Button(label=UI_LABELS[f"slot:{slot}:empty"], action="noop"))

    # === Inventory items ===

    if inventory:
        buttons.append(Button(label=UI_LABELS["inventory_splitter:inventory"], action="noop"))

        for key_name in inventory:
            text_name = ITEMS[key_name]["text_name"]
            buttons.append(Button(label=text_name, action=f"inventory_select:{key_name}:inventory"))


    # === Loot source items ===

    if loot_source_key_name != "inventory" and loot_source:
        buttons.append(Button(label=UI_LABELS["inventory_splitter:loot_source"], action="noop"))

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
    # destination = loot_source_key_name
    buttons.append(Button(label=f"[ {text_name} ]", action="noop"))

    state_wrapped = StateWrapper(state)
    source_container = state_wrapped.get_container(selected_item_source)
    item_count = source_container[selected_item_key_name].get("count", 1)

    # buttons.append(Button(label=f"{UI_LABELS['move_item_to']} {UI_LABELS[destination]}", action=f"move_item_to:{destination}"))
    if destination == selected_item_source:
        pass
    elif selected_item_source.startswith("equipped_"):
        pass
    else:
        buttons.append(Button(label=f"{UI_LABELS['move_item_to']} {UI_LABELS[destination]}", action=f"move_item_to:{destination}"))

    if item_count >= 2:
        buttons.append(Button(label=UI_LABELS["move_item_count_to:1"], action=f"move_item_count_to:1:{destination}"))
        buttons.append(Button(label=UI_LABELS["move_item_count_to:2"], action=f"move_item_count_to:2:{destination}"))
    if item_count >= 3:
        half = item_count // 2
        buttons.append(Button(label=UI_LABELS["move_item_count_to:half"], action=f"move_item_count_to:{half}:{destination}"))

    item_type = ITEMS[selected_item_key_name]["type"]

    if selected_item_source.startswith("equipped_"):
        slot = selected_item_source.replace("equipped_", "")
        action_btn = Button(label=UI_LABELS["unequip"], action=f"unequip:{slot}")
    elif item_type in ("weapon", "armour"):
        action_btn = Button(label=UI_LABELS["equip"], action=f"equip:{selected_item_key_name}:{selected_item_source}")
    else:
        action_btn = Button(label=UI_LABELS["use_item"], action="use_item")

    buttons.append(action_btn)

    buttons.append(Button(label=UI_LABELS["back_from_menu"], action="back_from_menu:inventory_select"))

    return buttons

def _dead_buttons() -> list[Button]:
    return [
        Button(label=UI_LABELS["start_again"], action="start_again"),
        Button(label=UI_LABELS["goto_menu:menu_expanse"], action="goto_menu:menu_expanse")
    ]

def menu_buttons(state: dict, key_menu: str, user_data: dict | None) -> list[Button]:
    buttons = []

    if key_menu == "menu_expanse":
            buttons.append(Button(label=UI_LABELS["menu:menu_expanse:new_game"], action="menu:menu_expanse:new_game"))
            if state.get("active"):
                buttons.append(Button(label=UI_LABELS["menu:menu_expanse:continue"], action="menu:menu_expanse:continue"))
            if not state.get("active"):
                buttons.append(Button(label=UI_LABELS["goto_menu:menu_recall"], action="goto_menu:menu_recall"))

    elif key_menu == "menu_recall":
        recall_costs = user_data["global_recalls"]["recall_cost"] if user_data else {}
        recall_names = ["health", "damage", "defence", "speed"]

        buttons = []
        for recall_name in recall_names:
            buttons.append(Button(label=f"{UI_LABELS[f"menu:menu_recall:{recall_name}"]} \
                                  {recall_costs[recall_name]}", action=f"menu:menu_recall:{recall_name}"))
        buttons.append(Button(label=f"{UI_LABELS["back_from_menu"]}", action="back_from_menu:menu_recall"))


    elif key_menu == "menu_help":
        buttons = [
            Button(label=UI_LABELS["goto_menu:menu_expanse"], action="goto_menu:menu_expanse")
        ]
    elif key_menu == "dead":
        return _dead_buttons()

    return buttons
