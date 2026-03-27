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

    async def inventory_open(self, user_id: int, loot_source: str = "inventory") -> dict:
        state = await self.database.get_state(user_id)

        log = engine.inventory_open(loot_source, state)

        return await self._finalize(user_id, state, log)

    async def inventory_select_item(self, user_id: int, item_key_name: str, source: str) -> dict:
        state = await self.database.get_state(user_id)

        log = engine.inventory_select(item_key_name, source, state)

        return await self._finalize(user_id, state, log)

    async def inventory_move_item(self, user_id: int, destination_key_name: str) -> dict:
        state = await self.database.get_state(user_id)

        log = engine.inventory_move(destination_key_name, state)

        return await self._finalize(user_id, state, log)

    # async def inventory_use_item(self, user_id: int) -> dict:
    #     state = await self.database.get_state(user_id)
    #
    #     log = engine.inventory_use(state)
    #
    #     return await self._finalize(user_id, state, log)

    async def goto_menu(self, user_id: int, menu: str) -> dict:
        """Open a menu overlay"""

        state = await self.database.get_state(user_id)
        state["menu_context"]["opened_menu"] = menu

        await self.database.save_state(user_id, state)

        return await self.continue_run(user_id)

    async def menu(self, user_id: int, menu: str, action: str) -> dict:
        """Perform action within a menu"""

        state = await self.database.get_state(user_id)
        state["menu_context"]["opened_menu"] = menu

        if menu == "main_menu" and action == "new_game":
            return await self.init_run(user_id)

        return await self.continue_run(user_id)

    async def back_the_menu(self, user_id: int) -> dict:
        """Close current overlay menu"""

        state = await self.database.get_state(user_id)
        opened_menu = state["menu_context"]["opened_menu"]

        if opened_menu is not None:
            # Reset inventory state if closing inventory
            if opened_menu == "inventory":
                state["inventory_state"] = {
                    "selected_item_key_name": None,
                    "loot_source": None,
                    "selected_item_source": None
                }
            state["menu_context"]["opened_menu"] = None

            await self.database.save_state(user_id, state)

        return await self.continue_run(user_id)

    async def start_again(self, user_id: int) -> dict:
        """Start over after death"""

        return await self.init_run(user_id)

    async def _finalize(self, user_id: int, state: dict, log: dict) -> dict:
        text_from_log = self.log_handler.render(log)

        contract = BRIDGE_CONTRACT.copy()
        contract["text"] = text_from_log

        state_type = ui_builder.get_state_type(log, state)
        contract["state_type"] = state_type
        contract["buttons"] = ui_builder.get_buttons(log, state, state_type)

        state["menu_context"]["type"] = state_type

        await self.database.save_state(user_id, state)

        # await self.database.close()

        return contract
