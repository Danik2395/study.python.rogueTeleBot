from data.presets import LOG

class InventorySystem:
    def __init__(self, container_getter, inventory_state: dict):
        self.inventory_state = inventory_state
        self.get_container = container_getter

        # TODO: сделай чтоб можно было в room["loot"] хранить несколько источников лута и открывать их из "explore" мода.
        # типа не захардкоженый словарь со ссылками на self поля, а сделать как-то через json чтоб можно было быстро получить ссылку на место, где лежит эта штука

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

        source.remove(item_key_name)
        destination.append(item_key_name)

        self.inventory_state["selected_item_source"] = destination_key_name

        return log
