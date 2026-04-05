import random
from typing import Any
from data.presets import LAYOUT, ITEMS, ENEMIES, RULES, LOG

class FloorSystem:
    """Class for floor generation"""

    def __init__(
            self,
            floor: dict
            ) -> None:
        self.floor = floor
        self.floor_index = floor["index"]
        self.current_room = floor["current_room_index"]
        self.fork_stack = floor["fork_stack"]
        self.rooms = floor["rooms"]
        self.rooms_current_amount = len(self.rooms)

        self.biom_key: str
        self.biom: dict
        self.floor_scale: float
        self._set_biom()
        self._set_scale()

        self.floor_enemies_pool: list
        self.floor_loot_pool: list
        self._filter_loot_pool()
        self._filter_enemies_pool()

    def _set_biom(self) -> None:
        """Set biom to filter enemies"""

        match self.floor_index:
            case 1:
                self.biom_key = "cave"
            case 2:
                self.biom_key = "not_cave"
            case _:
                self.biom_key = "void"

        self.biom = LAYOUT["bioms"][self.biom_key]

    def _set_scale(self) -> None:
        """
        Set scale for the floor.
        To multiply enemies stats by it
        """

        dirty_scale = self.biom["floor_scale"]
        if not dirty_scale:
            self.floor_scale = 1.5
            return

        scale_limits = random.choice(dirty_scale)
        if not scale_limits: scale_limits = [1.0, 1.5]

        low, high, *buff = scale_limits
        self.floor_scale = random.uniform(low, high)

    def _filter_enemies_pool(self) -> None:
        """Filter all enemies to lower scope of the floor"""

        self.floor_enemies_pool = [
                enemy for enemy, data in ENEMIES.items()

                if data.get("min_floor", 1) <= self.floor_index
                and self.biom_key in data.get("biom", list(LAYOUT["bioms"]))
                ]

    def _filter_loot_pool(self) -> None:
        """Filter items"""

        self.floor_loot_pool = [
                item for item, data in ITEMS.items()

                if data.get("min_floor", 1) <= self.floor_index
                ]

    def _gen_room_enemy_pool(self, pool_amount_limits: list) -> list:
        if not self.floor_enemies_pool:
            return []
        if not pool_amount_limits:
            pool_amount_limits = [0, 2]
        low, high, *buff = pool_amount_limits
        amount = random.randint(low, high)
        if amount <= 0:
            return []
        amount = min(amount, len(self.floor_enemies_pool))
        return random.sample(self.floor_enemies_pool, k=amount)

    def _gen_room_loot_pool(self, pool_amount_limits: list) -> dict:
        if not self.floor_loot_pool:
            return {}
        if not pool_amount_limits:
            pool_amount_limits = [0, 2]
        low, high, *buff = pool_amount_limits
        amount = random.randint(low, high)
        if amount <= 0:
            return {}
        amount = min(amount, len(self.floor_loot_pool))
        keys = random.sample(self.floor_loot_pool, k=amount)
        return {k: {"count": 1} for k in keys} # TODO: сделать темплейты для генерации количества рандомного для предметов

    def _gen_room_doors(
            self,
            room_type: str,
            prev_room_doors: dict | None = None,
            prev_room_index: int = -1,
            backward_direction: str = ""
            ) -> dict:
        """
        If room is entrance then it extracts doors template from biom
        Throws a chance on the doors and creates them marked as "NEW"
        Sets a backward door to the room from player came if not entrance
        """

        # Python requirement
        if prev_room_doors is None:
            prev_room_doors = {}

        doors = {}
        rules = self.biom["branch_rules"]

        if room_type == "entrance":
            # Copy so we can change the template localy
            doors = self.biom["doors_template"].copy()
            power = rules["branch_power"]

            door_chance = rules["entrance_door_chance"]
            down_chance = rules["entrance_down_chance"]

        else:
            # Not a forged skeleton 'cause of the scalability
            doors: dict[str, Any] = dict.fromkeys(prev_room_doors, None)

            power = prev_room_doors["branch_power"] - rules["power_decrease"]

            # Setting previous room door
            doors[backward_direction] = prev_room_index

            door_chance = rules["door_chance"]
            down_chance = rules["down_chance"]

        if power <= 0:
            return doors
        doors["branch_power"] = power

        # Set to not to get an error
        valid_direction = set(self.biom["valid_directions"].copy())
        keys_to_remove = {backward_direction, "branch_power", "down"}
        door_keys = valid_direction - keys_to_remove

        for door_key in door_keys:
            if random.random() <= door_chance:
                doors[door_key] = "NEW"


        throw_down = power <= rules["down_chance"]

        if (
            throw_down
            and self.floor["down_in_room"] == -1
            and random.random() <= down_chance
        ):
            doors["down"] = True
            self.floor["down_in_room"] = prev_room_index + 1

        return doors

    def gen_room(self, prev_room: dict, backward_direction: str) -> dict:
        """
        Randomly generates new current room
        """

        # The first room is entrance room
        room_index = self.rooms_current_amount
        self.rooms_current_amount += 1

        # ===SETTING===
        room_type = random.choice(LAYOUT["room_type"])
        room_name = random.choice(self.biom["text_name"])
        room_mood = random.choice(self.biom["mood"])

        # ===DOORS===
        prev_room_doors = prev_room["doors"]
        prev_room_index = prev_room["index"]
        room_doors = self._gen_room_doors(room_type, prev_room_doors, prev_room_index, backward_direction)
        opposite_direction = RULES["opposite_direction"][backward_direction]
        prev_room_doors[opposite_direction] = room_index

        # ===ENEMIES===
        room_enemies = {}
        if room_type == "combat":
            enemies_amount = random.choice(self.biom["enemies_amount"])
            room_enemies = self._gen_room_enemy_pool(enemies_amount)

        # ===LOOT===
        loot_amount = random.choice(self.biom["loot_amount"])
        room_loot = self._gen_room_loot_pool(loot_amount)

        # TODO: убери это. всё должно из темплейтов браться
        new_room: dict[str, Any] = {
                "index": room_index,
                "type": "room",
                "room_type": room_type,
                "text_name": room_name,
                "mood": room_mood,
                "cleared": True if not room_enemies else False,
                "enemies": room_enemies,
                "loot": {
                    "room_loot": room_loot
                    },
                "doors": room_doors
                }
        self.rooms.append(new_room)
        return new_room

    def gen_entrance(self) -> dict:
        """Generate entrance room"""

        # Setting prompt for the entrance
        floor_entrance_log = LOG["floor_entrance_log_template"]

        entrance_prompt = LAYOUT["entrance_prompt"]
        entrance_chosen_prompt = random.choice(entrance_prompt[str(self.floor_index)])
        floor_entrance_log["prompt"] = entrance_chosen_prompt


        # TODO: нужно сделать проверку, чтобы логхэндлер отличал начало на этаже от входа повтороного в начальную комнату
        entrance: dict[str, Any] = {
                "index": 0,
                "type": "entrance",
                "room_type": "entrance",
                "text_name": None,
                # "mood": entrance_mood,
                "mood": None,
                "cleared": True,
                "enemies": None,
                "loot": {
                    "room_loot": {}
                    },
                "doors": self._gen_room_doors("entrance")
                }

        self.rooms.append(entrance)

        self.fork_stack.append(0)

        # return entrance
        return floor_entrance_log
