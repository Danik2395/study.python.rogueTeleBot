#
# systems.py
#

from typing import Any
import random
from presets import LAYOUT, ITEMS, ENEMIES


class FloorSystem:
    """Class for floor generation"""
# TODO: сделать логику стека для веток
    def __init__(
            self,
            floor: dict
            ) -> None:
        self.floor_index = floor["index"]
        self.current_room = floor["current_room"]
        self.fork_stack = floor["fork_stack"]
        self.down_in_room = floor["down_in_room"]
        self.rooms = floor["rooms"]
        self.rooms_curr_amount = len(self.rooms)

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
                self.biom_key = "not cave"
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
                enemy for enemy in ENEMIES

                if enemy["min_floor"] <= self.floor_index
                and self.biom_key in enemy["biom"]
                ]

    def _filter_loot_pool(self) -> None:
        """Filter items"""

        self.floor_loot_pool = [
                item for item in ITEMS

                if item["min_floor"] <= self.floor_index
                ]

    @staticmethod
    def _get_room_content_pool(dirty_pool: list, pool_amount_limits: list) -> list:
        """Returns list of "pool" limited by amount"""

        if not dirty_pool: return []
        
        pool = []

        if not pool_amount_limits: pool_amount_limits = [0, 2]
        low, high, *buff = pool_amount_limits
        pool_amount = random.randint(low, high)
        if pool_amount == 0: return pool

        pool = random.sample(dirty_pool, k=pool_amount)
        return pool

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
            doors[backward_direction] = f"room_{prev_room_index}"
            
            door_chance = rules["door_chance"]
            down_chance = rules["down_chance"]

        if power <= 0:
            return doors
        doors["branch_power"] = power

        # Set to not to get an error
        keys_to_remove = {backward_direction, "branch_power", "down"}
        door_keys = set(doors.keys()) - keys_to_remove
        
        for door_key in door_keys:
            if random.random() <= door_chance:
                doors[door_key] = "NEW"


        throw_down = power <= rules["down_chance"]
        doors["down"] = True if throw_down and random.random() <= down_chance else False

        return doors

    def gen_room(self, prev_room_doors: dict, backward_direction: str) -> dict:
        """Randomly creates a new room depending on the floor and room index"""

        # The first room is entrance room
        room_index = self.rooms_curr_amount
        self.rooms_curr_amount += 1

        # ===SETTING===
        room_type = random.choice(LAYOUT["type"]) 
        room_name = random.choice(self.biom["name"]) 
        room_mood = random.choice(self.biom["mood"])

        # ===DOORS===
        # prev_room[direction] = f"room_{room_index}"
        room_doors = self._gen_room_doors(room_type, prev_room_doors, room_index, backward_direction)

        # ===ENEMIES===
        room_enemies = []
        if room_type == "combat":
            enemies_amount = self.biom["enemies_amount"]
            room_enemies_signs = self._get_room_content_pool(self.floor_enemies_pool, enemies_amount)

            for enemy_name in room_enemies_signs:
               health = ENEMIES[enemy_name]["health"]
              
               room_enemies[enemy_name] = {
                   "current_health": health * self.floor_scale
               }

        # ===LOOT===
        loot_amount = random.choice(self.biom["loot_amount"])
        room_loot = self._get_room_content_pool(self.floor_loot_pool, loot_amount)

        new_room: dict[str, Any] = {
                "index": room_index,
                "type": room_type,
                "name": room_name,
                "mood": room_mood,
                "cleared": True if not room_enemies else False,
                "enemies": room_enemies,
                "loot": room_loot,
                "doors": room_doors
                }
        return new_room

    def gen_entrance(self) -> dict:
        """Generate entrance room"""

        # Setting prompt for the entrance
        entr_prompt = LAYOUT["entrance_prompt"]
        entrance_mood = random.choice(entr_prompt[str(self.floor_index)])

        entrance: dict[str, Any] = {
                "index": 0,
                "type": "entrance",
                "name": None,
                "mood": entrance_mood,
                "cleared": True,
                "enemies": None,
                "loot": None,
                "doors": self._gen_room_doors("entrance")
                }

        return entrance
