import copy

import core.engine as engine
import core.ui_builder as ui_builder
from database.database import Database
from core.log_handler import LogHandler
from core.action_parcer import ActionParser

from data.presets import Contract, LOG, PARENT_MENU


class RogueInterface:
    def __init__(self, database: "Database", log_handler: "LogHandler") -> None:
        self.log_handler = log_handler
        self.database = database

    @classmethod
    async def create(cls) -> "RogueInterface":
        database = await Database.create()
        log_handler = LogHandler(database)

        interface = RogueInterface(database, log_handler)

        return interface

    async def cmd_start(self, user_id: int) -> Contract:
        is_user_exists = await self.database.is_user_exists(user_id)

        if is_user_exists:
            state = await self.database.get_user_run_state(user_id)
        else:
            user_data = engine.init_data()
            state = copy.deepcopy(LOG["run_state_template"])
            state["menu_context"]["opened_menu"] = "menu_expanse"
            await self.database.save_user_global_data(user_id, user_data)
            await self.database.save_user_run_state(user_id, state)

        buttons = ui_builder.menu_buttons(state, "menu_expanse") # If state == {} wont show continue button

        return Contract(buttons=buttons)

    async def get_ui_message_id(self, user_id: int) -> int:
        ui_message_id =  await self.database.get_ui_message_id(user_id)

        if ui_message_id == 0:
            raise ValueError("no message in database")

        return ui_message_id

    async def save_ui_message_id(self, user_id: int, ui_message_id: int) -> None:
       await self.database.save_ui_message_id(user_id, ui_message_id)

    async def init_run(self, user_id: int) -> Contract:
        user_data = await self.database.get_user_global_data(user_id)
        init_run_log, new_run_state = engine.init_run(user_data)

        await self.database.save_user_global_data(user_id, user_data)

        return await self._finalize_game(user_id, new_run_state, init_run_log)

    async def continue_run(self, user_id: int, *, run_state: dict | None = None, show_menu: bool = False) -> Contract:
        if run_state is None:
            run_state = await self.database.get_user_run_state(user_id)

        continue_log = LOG["continue_run_log_template"].copy()
        if show_menu:
            menu_context = run_state["menu_context"]
            opened_menu = menu_context["opened_menu"]
            continue_log["menu"] = opened_menu

        return await self._finalize_game(user_id, run_state, continue_log)

    async def move(self, user_id: int, direction: str) -> Contract:
        run_state = await self.database.get_user_run_state(user_id)

        move_log = engine.move(direction, run_state)

        return await self._finalize_game(user_id, run_state, move_log)

    async def move_to_fork(self, user_id: int) -> Contract:
        run_state = await self.database.get_user_run_state(user_id)

        move_log = engine.move_to_fork(run_state)

        return await self._finalize_game(user_id, run_state, move_log)

    async def move_down(self, user_id: int) -> Contract:
        run_state = await self.database.get_user_run_state(user_id)
        user_data = await self.database.get_user_global_data(user_id)

        log = engine.move_down(run_state, user_data)

        await self.database.save_user_global_data(user_id, user_data)

        return await self._finalize_game(user_id, run_state, log)

    async def attack(self, user_id: int, target_enemy_name: str) -> Contract:
        run_state = await self.database.get_user_run_state(user_id)

        combat_log = engine.attack(target_enemy_name, run_state)

        return await self._finalize_game(user_id, run_state, combat_log)

    async def defence(self, user_id: int) -> Contract:
        run_state = await self.database.get_user_run_state(user_id)
        log = engine.defence(run_state)
        return await self._finalize_game(user_id, run_state, log)

    async def flee(self, user_id: int) -> Contract:
        run_state = await self.database.get_user_run_state(user_id)
        log = engine.flee(run_state)
        return await self._finalize_game(user_id, run_state, log)

    async def inventory_open(self, user_id: int, loot_source: str = "inventory") -> Contract:
        state = await self.database.get_user_run_state(user_id)

        log = engine.inventory_open(loot_source, state)

        return await self._finalize_game(user_id, state, log)

    async def inventory_select_item(self, user_id: int, item_key_name: str, source: str) -> Contract:
        state = await self.database.get_user_run_state(user_id)

        log = engine.inventory_select(item_key_name, source, state)

        return await self._finalize_game(user_id, state, log)

    async def inventory_move_item(self, user_id: int, destination_key_name: str, count: int | None = None) -> Contract:
        state = await self.database.get_user_run_state(user_id)

        log = engine.inventory_move(destination_key_name, state, count)

        return await self._finalize_game(user_id, state, log)

    async def inventory_use_item(self, user_id: int) -> Contract:
        state = await self.database.get_user_run_state(user_id)
        log = engine.inventory_use(state)
        return await self._finalize_game(user_id, state, log)

    async def inventory_equip_item(self, user_id: int, item_key_name: str, source: str) -> Contract:
        state = await self.database.get_user_run_state(user_id)
        inventory_state = state["inventory_state"]
        inventory_state["selected_item_key_name"] = item_key_name
        inventory_state["selected_item_source"] = source

        log = engine.inventory_equip(state)
        return await self._finalize_game(user_id, state, log)

    async def goto_menu(self, user_id: int, key_menu: str) -> Contract:
        """Open a menu overlay"""

        state = await self.database.get_user_run_state(user_id)
        state["menu_context"]["opened_menu"] = key_menu

        # await self.database.save_user_run_state(user_id, state)

        return await self.continue_run(user_id, run_state=state, show_menu=True)

    async def goto_menu_help(self, user_id: int) -> Contract:
        """Open a help menu overlay"""

        return await self.goto_menu(user_id, "menu_help")

    async def goto_menu_expanse(self, user_id: int) -> Contract:
        """Open a main menu overlay"""

        return await self.goto_menu(user_id, "menu_expanse")

    async def menu(self, user_id: int, key_menu: str, action: str) -> Contract:
        """Perform action within a menu"""

        state = await self.database.get_user_run_state(user_id)

        match key_menu:
            case "menu_expanse":
                if action == "new_game":
                    return await self.init_run(user_id)
                if action == "continue":
                    state["menu_context"]["opened_menu"] = None
                    return await self.continue_run(user_id, run_state=state)

            case "menu_recall":
                user_data = await self.database.get_user_global_data(user_id)
                log = engine.recall_stat(user_data, action)
                await self.database.save_user_global_data(user_id, user_data)
                return await self._finalize_game(user_id, state, log)

        state["menu_context"]["opened_menu"] = key_menu
        return await self.continue_run(user_id, run_state=state, show_menu=True)

    async def back_from_menu(self, user_id: int, source_key_menu: str) -> Contract:
        """Goes back from menu depends on the prewritten links"""

        state = await self.database.get_user_run_state(user_id)
        # opened_menu = state["menu_context"]["opened_menu"]

        if source_key_menu is not None:
            # Reset inventory state if closing inventory
            if source_key_menu in ("inventory", "inventory_select"):
                inventory_state = state["inventory_state"]

                inventory_state["selected_item_key_name"] =  None
                inventory_state["selected_item_source"] = None
                if source_key_menu != "inventory_select":
                    inventory_state["loot_source"] = None

            state["menu_context"]["opened_menu"] = PARENT_MENU[source_key_menu]

            return await self.continue_run(user_id, run_state=state, show_menu=True)

        return await self.continue_run(user_id, run_state=state)

    async def start_again(self, user_id: int) -> Contract:
        """Start over after death"""

        return await self.init_run(user_id)

    async def _finalize_game(self, user_id: int, state: dict, log: dict) -> Contract:
        text_from_log = await self.log_handler.render(log, state)

        contract = Contract(text=text_from_log)

        state_type = ui_builder.get_state_type(log, state)
        contract.state_type = state_type
        contract.buttons = ui_builder.get_game_buttons(log, state, state_type)

        menu_context = state["menu_context"]
        menu_context["type"] = state_type
        # menu_context["opened_menu"] = state_type

        await self.database.save_user_run_state(user_id, state)

        # await self.database.close()

        return contract

class NoAction(Exception):
    """Exception to do nothing on empty button"""

    def __init__(self) -> None:
        super().__init__("no action")


async def process_action(user_id: int, action: str | None, rogue_interface: "RogueInterface") -> Contract:
    if action is None:
        return Contract(text="no action")

    parser = ActionParser()
    parsed = parser.parse(action)

    match parsed.command:
        case "back_from_menu":
            source_key_menu = parsed.params["source_key_menu"]
            return await rogue_interface.back_from_menu(user_id, source_key_menu)

        case "move":
            direction = parsed.params["direction"]
            if direction == "to_fork":
                return await rogue_interface.move_to_fork(user_id)
            if direction == "down":
                return await rogue_interface.move_down(user_id)
            return await rogue_interface.move(user_id, direction)

        case "combat":
            action = parsed.params["action"]
            if action == "attack":
                target = parsed.params["target_enemy_name"]
                return await rogue_interface.attack(user_id, target)
            if action == "defence":
                return await rogue_interface.defence(user_id)
            if action == "flee":
                return await rogue_interface.flee(user_id)

        case "inventory_open":
            loot_source = parsed.params["loot_source"]
            return await rogue_interface.inventory_open(user_id, loot_source)

        case "inventory_select":
            item_key_name = parsed.params["item_key_name"]
            source = parsed.params["source"]
            return await rogue_interface.inventory_select_item(user_id, item_key_name, source)

        case "move_item_count_to":
            count = int(parsed.params["count"])
            destination = parsed.params["destination"]
            return await rogue_interface.inventory_move_item(user_id, destination, count)

        case "move_item_to":
            destination = parsed.params["destination"]
            return await rogue_interface.inventory_move_item(user_id, destination)

        case "use_item":
            return await rogue_interface.inventory_use_item(user_id)

        case "equip":
            item_key_name = parsed.params["item_key_name"]
            source = parsed.params["source"]
            return await rogue_interface.inventory_equip_item(user_id, item_key_name, source)

        case "goto_menu":
            key_menu = parsed.params["key_menu"]
            return await rogue_interface.goto_menu(user_id, key_menu)

        case "menu":
            key_menu = parsed.params["key_menu"]
            action_name = parsed.params["action"]
            return await rogue_interface.menu(user_id, key_menu, action_name)

        case "start_again":
            return await rogue_interface.start_again(user_id)

        case "noop":
            raise NoAction

    return Contract(text=f"unknown: {action}")
