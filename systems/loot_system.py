from data.presets import LOG

class LootSystem():
    def __init__(
            self,
            room: dict,
            player: dict
            ) -> None:
        self.room = room
        self.player = player

        self.loot = room["loot"]
        self.inventory = player["inventory"]

    # Two functions in case of some special flags are added to the log
    def take_item(self, item_name: str) -> dict:
        log = LOG["item"].copy()
        log["transition_into"] = "inventory"

        # Checking wether the item really is in the loot
        if item_name in self.loot:
            log["transition_item"] = item_name
            self.loot.remove(item_name)
            self.inventory.append(item_name)

        else:
            return log

        # If no items left setting the flag
        if not self.loot:
            log["is_items_left"] = False

        return log

    def put_item(self, item_name: str) -> dict:
        log = LOG["item"].copy()
        log["transition_into"] = "loot"

        if item_name in self.inventory:
            log["transition_item"] = item_name
            self.inventory.remove(item_name)
            self.loot.append(item_name)

        else:
            return log

        if not self.inventory:
            log["is_items_left"] = False

        return log
