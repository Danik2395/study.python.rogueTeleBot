import random
from core.entities import Player, Enemy
from data.presets import LOG, ENEMIES, COMBAT_RULES

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

        # Enemies from state
        self.enemies_data: dict
        # Enemies objects
        self.enemies_objects: dict[str, Enemy]

        self.player = Player(
                player["current_health"],
                player["base_defence"],
                player["base_damage"],
                player["base_speed"],
                player["equipped_items"]
                )
        self.turns = combat_state["turns"]

        self._set_enemies()

        if self.turns is None:
            self._set_turns()

    def _set_enemies(self) -> None:
        """
        Parces data for enemies in room from enemies dictionary
        And creates Enemy objects for combat operations
        """

        self.enemies_data = self.combat_state["enemies"]

        # If its the first action take data from presets
        if self.enemies_data is None:
            self.enemies_data = {
                    name: ENEMIES[name].copy() for name in self.room_enemies
                    }

        # Then converting dict to the objects
        self.enemies_objects = {
                name: Enemy(enemy_data) for name, enemy_data in self.enemies_data.items()
                }

    def _set_turns(self) -> None:
       self.turns = self.player.speed // COMBAT_RULES["turn_delimiter"]

    def proceed_action(self, action_type: str, target_enemy_name: str = "") -> dict:
        """Proceeds player actions and returns combat action log"""
# TODO: сделать систему для логов, и туда уже передавать это всё
# типа движок получает jsonы от интерфейса после sql запроса по id пользователя, системы их меняют и отдают логи
# в систему логов, которая обрабатывает их, и движок отдаёт готовый текст с логом или без в интерфейс
# который записывает всё обратно в бд и выводит текст в боте

        match action_type:
            case "attack":
                log = LOG["combat_log_template"].copy()
                log["type"] = action_type
                log["consequence"] = []
                consequence = LOG["combat_consequence_log_template"].copy()

                consequence["attacker"] = "player"
                consequence["target"] = target_enemy_name
                consequence["stat"] = "damage"

                damage_scale = random.choice(COMBAT_RULES["damage_scale_limits"])
                low_damage, high_damage, *buff = damage_scale

                # Rolling player damage
                player_damage = random.randint(int(self.player.damage * low_damage), int(self.player.damage * high_damage))

                # Applying damage to the target
                target_enemy = self.enemies_objects[target_enemy_name]
                targ_enemy_health_before = target_enemy.current_health
                target_enemy.take_damage(player_damage)
                delta_damage = target_enemy.current_health - targ_enemy_health_before
                consequence["delta"] = delta_damage

                # Setting dead flag in consequence
                if target_enemy.current_health <= 0:
                    consequence["dead"] = True

                # Parcing all left alive enemies and rewriting enemies in the battle
                # It is possible to leave enemies untouched but it require additional logic
                self.enemies_objects = {
                        name: enemy_object for name, enemy_object in self.enemies_objects.items()
                        if enemy_object.current_health > 0
                    }

                # Rewriting enemies in combat state for valid data
                self.combat_state["enemies"] = {
                        name: {
                            "health": enemy_object.current_health,
                            "damage": enemy_object.base_damage,
                            "defence": enemy_object.base_defence,
                            "speed": enemy_object.base_speed
                            } for name, enemy_object in self.enemies_objects.items()
                        }

                if not self.enemies_objects:
                    self.combat_state["in_combat"] = False
                    log["combat_ended"] = True

                    return log

                # Appending consequence to the log after players attack
                log["consequence"].append(consequence)

                self.combat_state["turns"] -= 1

                # Enemies turn
                if self.combat_state["turns"] <= 0:

                    log["enemies_turn_triggered"] = True

                    # enemy stands for enemy_object. To shorten typing
                    for name, enemy in self.enemies_objects.items():
                        consequence = LOG["combat_consequence_log_template"].copy()

                        consequence["attacker"] = name
                        consequence["target"] = "player"
                        consequence["stat"] = "damage"

                        enemy_damage = random.randint(int(enemy.damage * low_damage), int(enemy.damage * high_damage))

                        player_health_before = self.player.current_health
                        self.player.take_damage(enemy_damage)
                        delta_damage = self.player.current_health - player_health_before
                        consequence["delta"] = delta_damage

                        # If player dead transfering data to the upper structure
                        if self.player.current_health <= 0:
                            dead_log = LOG["dead_log_template"].copy()
                            dead_log["enemy"] = name
                            dead_log["damage"] = enemy_damage
                            raise self.player.Dead(dead_log)

                        log["combat_consequence_log_template"].append(consequence)

                    self._set_turns()

                return log

            case _:
                return {}
