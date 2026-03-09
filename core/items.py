class Item:
    """Class for items that are giving general properties"""

    def __init__(
            self,
            name: str,
            damage: int,
            weight: int,
            ) -> None:
        self.name = name
        self.damage = damage
        self.weight = weight


class Food(Item):
    """Food that provides heal"""

    def __init__(self, name: str, damage: int, weight: int, heal: int, poison: int) -> None:
        super().__init__(name, damage, weight)
        self.heal = heal
        self.poison = poison


class Weapon(Item):
    """Weapon increases players extra_damage"""

    def __init__(self, name: str, damage: int, weight: int) -> None:
        super().__init__(name, damage, weight)
