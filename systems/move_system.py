from data.presets import LOG

class MoveSystem:
    def __init__(
            self,
            floor: dict
            ) -> None:
        self.floor = floor
        self.fork_stack = floor["fork_stack"]

    @property
    def _current_room(self) -> dict:
        return self.floor["rooms"][self.floor["current_room"]]

    @property
    def _current_room_doors(self) -> dict:
        return self._current_room["doors"]

    def move(self, direction: str) -> dict:
        """
        Handles "movement" to the room
        Two flags will get all states of the desired room
        """

        log = LOG["move"].copy()

        new_current_room_sign = self._current_room_doors.get(direction)

        # Minimal exception handle
        if not new_current_room_sign:
            return log

        # If there is no room return log with flag
        if new_current_room_sign == "NEW":
            log["is_new_room"] = True
            return log

        new_rooms_count = 0
        for door in self._current_room_doors.values():
            if door == "NEW":
                new_rooms_count += 1

        if new_rooms_count >= 1 and self.floor["current_room"] not in self.fork_stack:
            self.fork_stack.append(self._current_room["index"])

        if new_rooms_count == 0 and self.floor["current_room"] in self.fork_stack: 
            self.fork_stack.remove(self._current_room["index"])

        # Changing current room
        self.floor["current_room"] = new_current_room_sign

        log["room_index"] = new_current_room_sign

        return log

    def move_to_fork(self) -> dict:
        """
        Handles "movement" to the last fork (room with more then one door)
        """

        log = LOG["move"].copy()
        log["is_fork"] = True

        if self.fork_stack:
            self.floor["current_room"] = self.fork_stack[-1]
        else:
            self.floor["current_room"] = 0

        log["room_index"] = self.floor["current_room"]

        return log
