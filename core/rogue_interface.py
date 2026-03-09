import engine as engine
import ui_builder as ui_builder
from database.database import Database
from log_handler import LogHandler

from data.presets import BRIDGE_CONTRACT


class RogueInterface:
    def __init__(self) -> None:
        self.log_handler = LogHandler()
        self.database = Database()

    def init_run(self, user_id: int) -> dict:
        init_run_log, new_run_state = engine.init_run()

        return self._finalize(user_id, new_run_state, init_run_log)

    def move(self, user_id: int, direction: str) -> dict:
        active_run_state = self.database.get_state(user_id)

        move_log = engine.move(direction, active_run_state)

        return self._finalize(user_id, active_run_state, move_log)

    def move_to_fork(self, user_id: int) -> dict:
        active_run_state = self.database.get_state(user_id)

        move_log = engine.move_to_fork(active_run_state)

        return self._finalize(user_id, active_run_state, move_log)

    def attack(self, user_id: int, target_enemy_name: str) -> dict:
        active_run_state = self.database.get_state(user_id)

        combat_log = engine.attack(target_enemy_name, active_run_state)

        return self._finalize(user_id, active_run_state, combat_log)

    def _finalize(self, user_id: int, state: dict, log: dict) -> dict:
        self.database.save_state(user_id, state)

        text_from_log = self.log_handler.render(log)

        contract = BRIDGE_CONTRACT.copy()
        contract["text"] = text_from_log

        state_type = ui_builder.get_state_type(log)
        contract["state_type"] = state_type
        contract["buttons"] = ui_builder.get_buttons(log, state, state_type)

        return contract
