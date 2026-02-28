#
# systems.py
#

import random
from presets import LAYOUT, ITEMS, ENEMIES

class RoomSystem:
    """Class for room manipulating"""

    @staticmethod
    @staticmethod
    def _get_pool(dirty_pool: list, pool_amount_limits: list) -> list:
        """Returns list of "pool" limited by amount"""

        if not dirty_pool: return []
        
        pool = list()

        if not pool_amount_limits: pool_amount_limits = [0, 2]
        low, high, *buff = pool_amount_limits
        pool_amount = random.randint(low, high)
        if pool_amount == 0: return pool

        pool = random.sample(dirty_pool, k=pool_amount)
        return pool


class FloorSystem:
    """Class for floor generation"""
# TODO: сделать генерацию начальной комнаты
    def __init__(
            self,
            floor: dict
            ) -> None:
        self.floor_index = floor["index"]

        self.biom_key
        self.biom: dict
        self.floor_scale: float 
        self._set_biom()
        self._set_scale()

        self.floor_enemies_pool: list
        self.floor_loot_pool: list
        self._set_loot_pool()
        self._set_enemies_pool()

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

    def _set_enemies_pool(self) -> None:
        """Filter all enemies to lower scope of the floor"""

        self.floor_enemies_pool = [
                enemy for enemy in ENEMIES

                if enemy["min_floor"] <= self.floor_index
                and self.biom_key in enemy["biom"]
                ]

    def _set_loot_pool(self) -> None:
        """Filter items"""

        self.floor_loot_pool = [
                item for item in ITEMS

                if item["min_floor"] <= self.floor_index
                ]

    def gen_room(self, direction: str) -> dict:
        """Randomly creates a new room depending on the floor and room index"""

        self.rooms_curr_amount += 1
        room_index = self.rooms_curr_amount

        # Room template
        # If the room is entrance then return template
        new_room = {
                "index": room_index,
                "type": "entrance" if room_index == 0 else None,
                "name": None,
                "mood": None,
                "cleared": True,
                "enemies": None,
                "loot": None,
                "exits": {
                        "forward": None,
                        "backward": None,
                        "left": None,
                        "right": None,
                        "down": None
                    }
                }

        if room_index == 0:
            room_mood = LAYOUT["entrance_promt"]
            new_room["mood"] = random.choice(room_mood[str(self.floor_index)])

            return new_room

        # Else if it is regular room
        room_type = random.choice(LAYOUT["type"]) 

        room_name = random.choice(self.biom["name"]) 
        room_mood = random.choice(self.biom["mood"])

        if room_type == "combat":
            enemies_amount = self.biom["enemies_amount"]
            room_enemies = RoomSystem._get_pool(self.floor_enemies_pool, enemies_amount)
            new_room["enemies"] = room_enemies


            # TODO: Это для логики этажа сделать нужно

        loot_amount = random.choice(self.biom["loot_amount"])
        room_loot = RoomSystem._get_pool(self.floor_loot_pool, loot_amount)

        new_room["type"] = room_type
        new_room["name"] = room_name
        new_room["mood"] = room_mood
        new_room["loot"] = room_loot

