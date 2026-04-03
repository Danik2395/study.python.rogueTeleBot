from data.presets import LOG, ITEMS

class InventorySystem:
    def __init__(self, container_getter, inventory_state: dict):
        self.inventory_state = inventory_state
        self.get_container = container_getter

    def move_item(self, destination_key_name: str) -> dict:
        item_key_name = self.inventory_state["selected_item_key_name"]
        source_key_name = self.inventory_state["selected_item_source"]
        # TODO: у тебя несколько одинаковых предметов не может выпасть в комнате, но их несколько одинаковых можено подобрать, и они будут уже в инвенторе.
        # исправь это

        log = LOG["inventory_log_template"].copy()
        log["action"] = "move"
        log["source"] = source_key_name
        log["item_key_name"] = item_key_name
        log["move_destination"] = destination_key_name

        source = self.get_container(source_key_name)
        destination = self.get_container(destination_key_name)

        if isinstance(source, list):
            if item_key_name in source:
                source.remove(item_key_name)
        elif isinstance(source, dict):
            self._remove_from_dict_container(source, item_key_name)

        if isinstance(destination, list):
            destination.append(item_key_name)
        else:
            self._move_to_dict_container(destination, item_key_name)

        self.inventory_state["selected_item_source"] = destination_key_name

        return log

    def use_item(self, player: dict) -> dict:
        key_name = self.inventory_state["selected_item_key_name"]
        item_type = ITEMS[key_name]["type"]
        match item_type:
            case "food":
                return self._use_food(key_name, player)

            case "weapon":
                return self._equip(key_name, "weapon", player)

            case "armour":
                return self._equip(key_name, "armour", player)

            case _:
                return LOG["inventory_log_template"].copy()

    def _use_food(self, key_name: str, player: dict) -> dict:
        heal = ITEMS[key_name]["heal"]
        player["current_health"] += heal
        if player["current_health"] > player["base_health"]:
            player["current_health"] = player["base_health"]

        source_key_name = self.inventory_state["selected_item_source"]
        source = self.get_container(source_key_name)
        if isinstance(source, list):
            source.remove(key_name)

        log = LOG["inventory_log_template"].copy()
        log["action"] = "use"
        log["item_key_name"] = key_name
        log["source"] = source_key_name
        return log

    def _equip(self, item_key_name: str, slot: str, player: dict) -> dict:
        equipped = player["equipped_items"]
        current = equipped[slot]
        if current is not None:
            player["inventory"].append(current)

        equipped[slot] = item_key_name

        source_key_name = self.inventory_state["selected_item_source"]
        source = self.get_container(source_key_name)
        if isinstance(source, list):
            source.remove(item_key_name)

        elif isinstance(source, dict):
            self._remove_from_dict_container(source, item_key_name)

        log = LOG["inventory_log_template"].copy()
        log["action"] = "equip"
        log["item_key_name"] = item_key_name
        log["source"] = source_key_name
        log["slot"] = slot
        return log

    def _move_to_dict_container(self, dest: dict, key_name: str) -> None:
        slot = ITEMS[key_name]["type"]
        dest[slot] = key_name

    def _remove_from_dict_container(self, src: dict, key_name: str) -> None:
        slot = ITEMS[key_name]["type"]
        src[slot] = None
