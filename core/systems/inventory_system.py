import copy
from data.presets import LOG, ITEMS, ITEM_TEMPLATE

class InventorySystem:
    def __init__(self, container_getter, inventory_state: dict):
        self.inventory_state = inventory_state
        self.get_container = container_getter

    @staticmethod
    def _increment_item_count(container: dict, item_key_name: str, count: int) -> None:
        if item_key_name in container:
            container[item_key_name]["count"] += count
        else:
            container[item_key_name] = copy.deepcopy(ITEM_TEMPLATE)
            container[item_key_name]["count"] = count

    @staticmethod
    def _decrement_item_count(container: dict, item_key_name: str, count: int) -> None:
        container[item_key_name]["count"] -= count
        if container[item_key_name]["count"] <= 0:
            del container[item_key_name]

    def move_item(self, destination_key_name: str, count: int | None = None) -> dict:
        item_key_name = self.inventory_state["selected_item_key_name"]
        source_key_name = self.inventory_state["selected_item_source"]

        source = self.get_container(source_key_name)
        destination = self.get_container(destination_key_name)

        actual_count = count if count is not None else source[item_key_name]["count"]
        log = LOG["inventory_log_template"].copy()
        log["action"] = "move"
        log["source"] = source_key_name
        log["item_key_name"] = item_key_name
        log["move_destination"] = destination_key_name
        log["count_delta"] = actual_count
        log["count_in_source"] = source[item_key_name]["count"]

        self._decrement_item_count(source, item_key_name, actual_count)
        self._increment_item_count(destination, item_key_name, actual_count)

        log["count_in_destination"] = destination[item_key_name]["count"]

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
        self._decrement_item_count(source, key_name, 1)

        log = LOG["inventory_log_template"].copy()
        log["action"] = "use"
        log["item_key_name"] = key_name
        log["source"] = source_key_name
        return log

    def _equip(self, item_key_name: str, slot: str, player: dict) -> dict:
        destination_key = f"equipped_{slot}"
        destination = self.get_container(destination_key)

        if destination:
            old_item_key_name, = destination
            self._increment_item_count(player["inventory"], old_item_key_name, 1)
            destination.clear()

        destination[item_key_name] = copy.deepcopy(ITEM_TEMPLATE)
        destination[item_key_name]["count"] = 1

        source_key_name = self.inventory_state["selected_item_source"]
        source = self.get_container(source_key_name)
        self._decrement_item_count(source, item_key_name, 1)

        log = LOG["inventory_log_template"].copy()
        log["action"] = "equip"
        log["item_key_name"] = item_key_name
        log["source"] = source_key_name
        log["slot"] = slot
        return log


