#
# systems.py
#

from typing import Any
import random
from presets import LAYOUT, ITEMS, ENEMIES, COMBAT_RULES, LOG
from entities import Enemy, Player


class FloorSystem:
    """Class for floor generation"""
# TODO: сделать логику стека для веток
# TODO: а ещё сделать логирование; оно наверно в перемещении будет, а не в этажах.
# TODO: а ещё у тебя нет 100% выпадения выхода на следующий этаж. в плане он просто может не выпасть
# TODO: да и впринципе нет обработки выхода
    pass
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
                enemy for enemy, data in ENEMIES.items()

                if data.get("min_floor", 1) <= self.floor_index
                and self.biom_key in data.get("biom", LAYOUT["bioms"])
                ]

    def _filter_loot_pool(self) -> None:
        """Filter items"""

        self.floor_loot_pool = [
                item for item, data in ITEMS

                if data.get("min_floor", 1) <= self.floor_index
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
            doors[backward_direction] = prev_room_index
            
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
        room_doors = self._gen_room_doors(room_type, prev_room_doors, room_index, backward_direction)

        # ===ENEMIES===
        room_enemies = {}
        if room_type == "combat":
            enemies_amount = self.biom["enemies_amount"]
            room_enemies = self._get_room_content_pool(self.floor_enemies_pool, enemies_amount)

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
        self.rooms.append(new_room)
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

        self.rooms.append(entrance)
        return entrance


class CombatSystem:
    def __init__(
            self,
            player: dict,
            room_enemies: list,
            combat_state: dict
            ) -> None:
        self.room_enemies = room_enemies

        self.combat_state = combat_state
        self.combat_state["in_combat"] = True
        self.enemies: dict
        self.enemies_pack: dict[str, Enemy]
        
        self.player = Player(
                player["current_health"],
                player["defence"],
                player["damage"],
                player["speed"],
                player["equipped_items"]
                )
        self.turns = combat_state["turns"]

        self._set_enemies()
        self._get_turns()

    def _set_enemies(self) -> None:
        """
        Parces data for enemies in room from enemies dictionary
        And creates Enemy objects for combat operations
        """

        enemies = self.combat_state["enemies"]
        if enemies is None:
            enemies = {
                    name: ENEMIES[name] for name in self.room_enemies
                    }

        self.enemies_pack = {
                name: Enemy(name) for name in self.enemies 
                }

    def _get_turns(self) -> None:
       self.turns = self.player.speed // COMBAT_RULES["turn_delimiter"]

    def proceed_action(self, action_type: str, target_enemy: str = "") -> dict:
        """Proceeds player actions and returns combat action log"""
# TODO: сделать систему для логов, и туда уже передавать это всё
# типа движок получает jsonы от интерфейса после sql запроса по id пользователя, системы их меняют и отдают логи 
# в систему логов, которая обрабатывает их, и движок отдаёт готовый текст с логом или без в интерфейс
# который записывает всё обратно в бд и выводит текст в боте

        log = LOG["combat"].copy()
        log["consequence"] = []
        consequence = LOG["combat_consequence"].copy()

        log["type"] = action_type
        match action_type:
            case "attack":               
                consequence["target"] = target_enemy
                consequence["stat"] = "damage"

                damage_scale = random.choice(COMBAT_RULES["damage_scale_limits"])
                low_damage, high_damage, *buff = damage_scale

                # Rolling player damage
                player_damage = random.randint(int(self.player.damage * low_damage), int(self.player.damage * high_damage))

                # Applying damage to the target
                targ_enemy = self.enemies_pack[target_enemy]
                targ_enemy_health_before = targ_enemy.current_health
                targ_enemy.take_damage(player_damage)
                delta_damage = targ_enemy.current_health - targ_enemy_health_before
                consequence["delta"] = delta_damage

                # Setting dead flag in consequence
                if targ_enemy.current_health <= 0:
                    consequence["dead"] = True
                    
                # Parcing all left alive enemies and rewriting enemies in the battle
                # It is possible to leave enemies untouched but it require additional logic
                self.enemies_pack = {
                        name: enemy for name, enemy in self.enemies_pack.items() 
                        if enemy.current_health > 0
                    }

                self.combat_state["enemies"] = list(self.enemies_pack.keys())

                if not self.enemies_pack:
                    self.combat_state["in_combat"] = False
                    log["combat_ended"] = True

                    return log 

                # Appending consequence to the log after players attack
                log["consequence"].append(consequence)

                self.combat_state["turns"] -= 1

                # Enemies turn
                if self.combat_state["turns"] <= 0:

                    log["enemies_turn_triggered"] = True

                    for name, enemy in self.enemies_pack.items():
                        consequence["target"] = "player"
                        consequence["stat"] = "damage"
                        
                        enemy_damage = random.randint(int(enemy.damage * low_damage), int(enemy.damage * high_damage))

                        player_health_before = self.player.current_health
                        self.player.take_damage(enemy_damage)
                        delta_damage = self.player.current_health - player_health_before
                        consequence["delta"] = delta_damage

                        # If player dead transfering data to the upper structure
                        if self.player.current_health <= 0:
                            dead_log = LOG["dead_log"].copy()
                            dead_log["enemy"] = name
                            dead_log["damage"] = enemy_damage
                            raise self.player.Dead(dead_log)

                    self.combat_state["turns"] = self._get_turns()

                return log

            case _:
                return {}


class MoveSystem:
    def __init__(
            self,
            floor: dict
            ) -> None:
        self.floor = floor

    def _get_curr_room(self) -> dict:
        room_index = self.floor["current_room"]
        return self.floor["rooms"][room_index]

    def move(self, direction: str) -> dict:
        """
        Handles "movement"
        Two flags will get all states of the desired room
        """
        log = LOG["move"].copy()

        current_room = self._get_curr_room()
        new_current_room_sign = current_room["doors"].get(direction)

        # Minimal exception handle
        if not new_current_room_sign:
            return log

        # If there is no room return log with flag
        if new_current_room_sign == "NEW":
            log["is_new_room"] = True
            return log

        # Changing current room
        self.floor["current_room"] = new_current_room_sign

        log["room_index"] = new_current_room_sign

        return log
