import core.engine as engine
import core.ui_builder as ui_builder
from database.database import Database
from core.log_handler import LogHandler

from data.presets import BRIDGE_CONTRACT, LOG


class RogueInterface:
    def __init__(self, database: "Database", log_handler: "LogHandler") -> None:
        self.log_handler = log_handler
        self.database = database

    @classmethod
    async def create(cls) -> "RogueInterface":
        database = await Database.create()
        log_handler = LogHandler()

        interface = RogueInterface(database, log_handler)

        return interface

    async def init_run(self, user_id: int) -> dict:
        init_run_log, new_run_state = engine.init_run()

        return await self._finalize(user_id, new_run_state, init_run_log)

    async def continue_run(self, user_id: int) -> dict:
        active_run_state = await self.database.get_state(user_id)

        continue_log = LOG["continue_run_log_template"].copy()

        return await self._finalize(user_id, active_run_state, continue_log)

    async def move(self, user_id: int, direction: str) -> dict:
        active_run_state = await self.database.get_state(user_id)

        move_log = engine.move(direction, active_run_state)

        return await self._finalize(user_id, active_run_state, move_log)

    async def move_to_fork(self, user_id: int) -> dict:
        active_run_state = await self.database.get_state(user_id)

        move_log = engine.move_to_fork(active_run_state)

        return await self._finalize(user_id, active_run_state, move_log)

    async def attack(self, user_id: int, target_enemy_name: str) -> dict:
        active_run_state = await self.database.get_state(user_id)

        combat_log = engine.attack(target_enemy_name, active_run_state)

        return await self._finalize(user_id, active_run_state, combat_log)

    async def take_item(self, user_id: int, item_name: str) -> dict:
        active_run_state = await  self.database.get_state(user_id)
        log = engine.take_item(item_name, active_run_state)
        return await self._finalize(user_id, active_run_state, log)

    async def _finalize(self, user_id: int, state: dict, log: dict) -> dict:
        text_from_log = self.log_handler.render(log)

        contract = BRIDGE_CONTRACT.copy()
        contract["text"] = text_from_log

        state_type = ui_builder.get_state_type(log, state)
        contract["state_type"] = state_type
        contract["buttons"] = ui_builder.get_buttons(log, state, state_type)

        state["last_state_type"] = state_type

        await self.database.save_state(user_id, state)

        # await self.database.close()

        return contract
