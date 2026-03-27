import asyncio
import random
random.seed(42)

from pprint import pprint
from core.rogue_interface import RogueInterface
from core.action_parcer import ActionParser

# USER_ID: int = 1

async def call(user_id: int, action: str, interface: "RogueInterface") -> dict:
    parser = ActionParser()
    parsed = parser.parse(action)

    if parsed.command == "init_run":
        return await interface.init_run(user_id)

    if parsed.command == "continue_run":
        return await interface.continue_run(user_id)

    if parsed.command == "back_the_menu":
        return await interface.back_the_menu(user_id)

    if parsed.command == "move":
        direction = parsed.params["direction"]
        if direction == "to_fork":
            return await interface.move_to_fork(user_id)
        return await interface.move(user_id, direction)

    if parsed.command == "attack":
        target = parsed.params["target_enemy_name"]
        return await interface.attack(user_id, target)

    if parsed.command == "inventory_open":
        loot_source = parsed.params["loot_source"]
        return await interface.inventory_open(user_id, loot_source)

    if parsed.command == "inventory_select":
        item_key_name = parsed.params["item_key_name"]
        source = parsed.params["source"]
        return await interface.inventory_select_item(user_id, item_key_name, source)

    if parsed.command == "move_item_to":
        destination = parsed.params["destination"]
        return await interface.inventory_move_item(user_id, destination)

    if parsed.command == "goto_menu":
        menu = parsed.params["menu"]
        return await interface.goto_menu(user_id, menu)

    if parsed.command == "menu":
        menu_type = parsed.params["menu_type"]
        action_name = parsed.params["action"]
        return await interface.menu(user_id, menu_type, action_name)

    if parsed.command == "start_again":
        return await interface.start_again(user_id)

    return {"error": f"unknown: {action}"}

async def main() -> None:
    interface = await RogueInterface.create()

    user_id = int(input("user_id: ").strip())
    new = True if input("init new run [y/N]: ").strip() in ("y", "Y") else False
    if new:
        pprint(await interface.init_run(user_id))
    else:
        pprint(await interface.continue_run(user_id))



    while True:
        action = input("\n> ").strip()
        if action in ("q", "quit"):
            break
        if action in ("show run", "sh run", "show rn", "sh rn"):
            pprint(await interface.database.get_state(user_id))
            continue

        action_log = await call(user_id, action, interface)

        pprint(action_log)

    await interface.database.close()

if __name__ == "__main__":
    asyncio.run(main())
