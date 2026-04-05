class StateWrapper:
    """
    Wrapper for skipping long queries for nested dicts.
    Could be used to pass the get_container method as a reference getter
    """
    def __init__(self, state: dict) -> None:
        self.state = state

        self.player = state["player"]
        self.floor = state["floor"]

    @property
    def current_room(self) -> dict:
        rooms = self.floor["rooms"]
        current_room_index = self.floor["current_room_index"]
        current_room = rooms[current_room_index]
        return current_room

    def get_container(self, source: str) -> dict:
        match source:
            case "inventory":
                return self.player["inventory"]
            case "room_loot":
                return self.current_room["loot"]["room_loot"]
            case "equipped_weapon":
                return self.player["equipped_items"]["equipped_weapon"]
            case "equipped_armour":
                return self.player["equipped_items"]["equipped_armour"]
            case "equipped_items":
                return self.player["equipped_items"]
            case _:
                return {}
