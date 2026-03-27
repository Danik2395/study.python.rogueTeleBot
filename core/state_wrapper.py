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

    def get_container(self, source: str) -> list | dict:
        match source:
            case "inventory":
                return self.player["inventory"]
            case "room_loot":
                return self.current_room["loot"]["room_loot"]
            case _:
                return []
