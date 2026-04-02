from data.presets import LOG, LAYOUT

class MoveSystem:
    # TODO: нужно сделать переход на этажи. и сделать на user_data, чтоб оно прибавляло этаж максимальный
    def __init__(
            self,
            floor: dict
            ) -> None:
        self.floor = floor
        self.fork_stack = floor["fork_stack"]

    @property
    def current_room(self) -> dict:
        return self.floor["rooms"][self.floor["current_room_index"]]

    @property
    def current_room_doors(self) -> dict:
        return self.current_room["doors"]

    def move(self, direction: str) -> dict:
        """
        Handles "movement" to the room
        Two flags will get all states of the desired room
        """

        move_log = LOG["move_log_template"].copy()
        move_log["direction"] = direction

        new_current_room_index = self.current_room_doors.get(direction)

        # Minimal exception handle
        if new_current_room_index is None:
            return move_log

        # If there is no room return log with flag
        if new_current_room_index == "NEW":
            move_log["is_new_room"] = True
            return move_log

        new_rooms_count = 0
        for door in self.current_room_doors.values():
            if door == "NEW":
                new_rooms_count += 1

        if new_rooms_count >= 1 and self.floor["current_room_index"] not in self.fork_stack:
            self.fork_stack.append(self.current_room["index"])

        if new_rooms_count == 0 and self.floor["current_room_index"] in self.fork_stack:
            self.fork_stack.remove(self.current_room["index"])

        # Changing current room
        self.floor["current_room_index"] = new_current_room_index

        move_log["room_index"] = new_current_room_index

        return move_log

    def move_to_fork(self) -> dict:
        """
        Handles "movement" to the last fork (room with more then one door)
        """

        log = LOG["move_log_template"].copy()
        log["is_fork"] = True

        if self.fork_stack:
            self.floor["current_room_index"] = self.fork_stack[-1]
        else:
            self.floor["current_room_index"] = 0

        log["room_index"] = self.floor["current_room_index"]

        return log
