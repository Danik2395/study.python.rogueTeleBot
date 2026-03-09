import random
from data.presets import ITEMS, ENEMIES


class Dummy:
    """Base class for life creatures"""

    def __init__(
            self,
            name: str,
            health: int,
            defence: int,
            damage: int,
            speed: int,
            ) -> None:
        self.name = name

        self.base_health = health
        self.extra_health = 0
        self.current_health = health

        self.base_damage = damage
        self.extra_damage = 0

        self.base_defence = defence
        self.extra_defence = 0

        self.base_speed = speed
        self.add_weight = 0

    # ===PROPERTIES===
    @property
    def max_health(self) -> int:
        return self.base_health + self.extra_health

    @property
    def damage(self) -> int:
        return self.base_damage + self.extra_damage

    @property
    def defence(self) -> int:
        return self.base_defence + self.extra_defence

    @property
    def speed(self) -> int:
        return self.base_speed - self.add_weight


    # ===ACTIONS===
    def take_damage(self, impact: int) -> None:
        """Decreasing health by impact if it can beat the defence"""

        # If defence is greater then impact
        actual_damage = max(0, impact - self.defence)
        self.current_health -= actual_damage

        if self.current_health < 0:
            self.current_health = 0

    def heal(self, amount: int) -> None:
        """Increacing health by amount not over max_health"""

        self.current_health += amount

        if self.current_health > self.max_health:
            self.current_health = self.max_health


class Player(Dummy):
    """Player class. Sets properties parcing values from jsons"""

    class Dead(Exception):
        """Exception that occured on the players death"""

        def __init__(self, log: dict):
            super().__init__("player_dead")
            self.log = log


    def __init__(self, health: int, defence: int, damage: int, speed: int, equipped_items: dict) -> None:
        super().__init__("Player", health, defence, damage, speed)
        self.equipped_items = equipped_items
        # self._set_stats()

    # def _set_stats(self) -> None:
        if self.equipped_items:
            damage, defence, weight = 0, 0, 0

            # "eq" = { "weapon": "sword", ... }
            # "sword" = { ..., "damage": 1, ... }
            for ITEMS_key in self.equipped_items.values():
                item = ITEMS.get(ITEMS_key)
                damage += item.get("damage", 0)
                defence += item.get("defence", 0)
                weight += item.get("weight", 0)

            self.extra_damage = damage
            self.extra_defence = defence
            self.add_weight = weight


class Enemy(Dummy):
    """
    Class for the combat system that sets enemies stats.
    Needed to proceed combat action onto player
    """

    def __init__(self, enemy_data: dict) -> None:
        # enemy_template = ENEMIES[enemy_name]

        rand_name = ["тень", "присутствие", "силуэт", "сущность"]
        self.name = enemy_data.get("name", random.choice(rand_name))
        self.current_health = enemy_data.get("health", random.randint(5, 15))
        self.base_damage = enemy_data.get("damage", random.randint(1, 20))
        self.base_defence = enemy_data.get("defence", random.randint(3, 15))
        self.base_speed = enemy_data.get("speed", random.randint(5, 30))
