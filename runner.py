import asyncio
import random
random.seed(42)

from pprint import pprint
from core.rogue_interface import RogueInterface

# USER_ID: int = 1

async def call(user_id: int, action: str, interface: "RogueInterface") -> dict:
    action_splitted = action.split(":")
    action_command = action_splitted[0]
    action_args = action_splitted[1:]

    if action_command == "init_run":
        return await interface.init_run(user_id)

    if action_command == "continue_run":
        return await interface.continue_run(user_id)

    if action_command == "back_the_menu":
        return await interface.continue_run(user_id)

    if action_command == "move":
        if action_args[0] == "to_fork":
            return await interface.move_to_fork(user_id)

        return await interface.move(user_id, action_args[0])

    if action_command == "attack":
        return await interface.attack(user_id, action_args[0])

    if action_command == "inventory_open":
        return await interface.inventory_open(user_id, action_args[0])

    if action_command == "inventory_select":
        item_key_name = action_args[0]
        source = action_args[1]

        return await interface.inventory_select_item(user_id, item_key_name, source)

    if action_command == "move_item_to":
        return await interface.inventory_move_item(user_id, action_args[0])

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

        action_log = await call(user_id, action, interface)

        pprint(action_log)

    await interface.database.close()

if __name__ == "__main__":
    asyncio.run(main())
