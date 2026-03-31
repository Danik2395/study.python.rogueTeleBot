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

        self.player = player
        self.player_object = Player(
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

    @staticmethod
    def build_state_enemies(room_enemies: list) -> dict:
        return {
            key_name: ENEMIES[key_name].copy()
            for key_name in room_enemies
            # TODO: сделай, чтобы в этой инициализации и в методе ниже не было полей минимального этажа и биома
        }

    def _set_enemies(self) -> None:
        """
        Parces data for enemies in room from enemies dictionary
        And creates Enemy objects for combat operations
        """

        self.enemies_data = self.combat_state["enemies"]

        # If its the first action take data from presets
        if self.enemies_data is None:
            self.enemies_data = {
                    key_name: ENEMIES[key_name].copy() for key_name in self.room_enemies
                    }
            # Initialize combat_state["enemies"] on the first room visit
            self.combat_state["enemies"] = self.enemies_data

        # Then converting dict to the objects
        self.enemies_objects = {
                key_name: Enemy(key_name, enemy_data) for key_name, enemy_data in self.enemies_data.items()
                }

    def _set_turns(self) -> None:
       self.turns = self.player_object.speed // COMBAT_RULES["turn_delimiter"]
       self.combat_state["turns"] = self.turns

    def proceed_action(self, action_type: str, target_enemy_key_name: str = "") -> dict:
        """Proceeds player actions and returns combat action log"""

        match action_type:
            case "attack":
                log = LOG["combat_log_template"].copy()

                if target_enemy_key_name not in self.enemies_data:
                    return log

                log["action"] = action_type
                log["consequence"] = []
                consequence = LOG["combat_consequence_log_template"].copy()

                consequence["attacker"] = "player"
                consequence["target"] = target_enemy_key_name
                consequence["stat"] = "damage"

                damage_scale = random.choice(COMBAT_RULES["damage_scale_limits"])
                low_damage, high_damage, *buff = damage_scale

                # Rolling player damage
                player_damage = random.randint(int(self.player_object.damage * low_damage), int(self.player_object.damage * high_damage))

                # Applying damage to the target
                target_enemy = self.enemies_objects[target_enemy_key_name]
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
                        key_name: enemy_object for key_name, enemy_object in self.enemies_objects.items()
                        if enemy_object.current_health > 0
                    }

                # Rewriting enemies in combat state for valid data
                self.combat_state["enemies"] = {
                        key_name: {
                            "health": enemy_object.current_health,
                            "damage": enemy_object.base_damage,
                            "defence": enemy_object.base_defence,
                            "speed": enemy_object.base_speed
                            } for key_name, enemy_object in self.enemies_objects.items()
                        }

                # self.room_enemies = [key_name for key_name in self.enemies_objects.keys()]

                if not self.enemies_objects:
                    self.combat_state["in_combat"] = False
                    log["combat_ended"] = True
                    self.combat_state["turns"] = None

                    return log

                # Appending consequence to the log after players attack
                log["consequence"].append(consequence)

                self.combat_state["turns"] -= 1

                # Enemies turn
                if self.combat_state["turns"] <= 0:

                    log["enemies_turn_triggered"] = True

                    # enemy stands for enemy_object. To shorten typing
                    for key_name, enemy in self.enemies_objects.items():
                        consequence = LOG["combat_consequence_log_template"].copy()
                        # TODO: нужно сделать в системе логов, чтобы она доставала текстовые имена из темплейтов

                        consequence["attacker"] = key_name
                        consequence["target"] = "player"
                        consequence["stat"] = "damage"

                        enemy_damage = random.randint(int(enemy.damage * low_damage), int(enemy.damage * high_damage))

                        player_health_before = self.player_object.current_health
                        self.player_object.take_damage(enemy_damage)
                        delta_damage = self.player_object.current_health - player_health_before
                        consequence["delta"] = delta_damage

                        # If player dead transfering data to the upper structure
                        if self.player_object.current_health <= 0:
                            dead_log = LOG["dead_log_template"].copy()
                            dead_log["enemy"] = key_name
                            dead_log["damage"] = enemy_damage
                            raise self.player_object.Dead(dead_log)

                        log["consequence"].append(consequence)

                    self.player.update({
                        "base_health": self.player_object.base_health,
                        "current_health": self.player_object.current_health,
                        "base_damage": self.player_object.base_damage,
                        "base_defence": self.player_object.base_defence,
                        "base_speed": self.player_object.base_speed,
                        "equipped_items": self.player_object.equipped_items.copy()
                    })
                    self._set_turns()

                log["turns"] = self.combat_state["turns"]
                return log

            case _:
                return {}
