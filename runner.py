import asyncio
import random
random.seed(42)

from pprint import pprint
from core.rogue_interface import RogueInterface

USER_ID: int = 1

async def call(action: str, interface: "RogueInterface") -> dict:
    if action == "init_run":
        return await interface.init_run(USER_ID)
    if action == "move_to_fork":
        return await interface.move_to_fork(USER_ID)
    if action.startswith("move_"):
        return await interface.move(USER_ID, action[5:])
    if action.startswith("attack_"):
        return await interface.attack(USER_ID, action[7:])
    if action.startswith("take_"):
        return await interface.take_item(USER_ID, action[5:])
    return {"error": f"unknown: {action}"}

async def main() -> None:
    interface = await RogueInterface.create()

    # USER_ID = int(input("user_id: ").strip())
    # new = True if input("init new run: ").strip() else False
    # if new:
    pprint(await interface.init_run(USER_ID))


    while True:
        action = input("\n> ").strip()
        if action in ("q", "quit"):
            break
        if action in ("show run", "sh run", "show rn", "sh rn"):
            pprint(await interface.database.get_state(USER_ID))

        action_log = await call(action, interface)

        pprint(action_log)

    await interface.database.close()

if __name__ == "__main__":
    asyncio.run(main())
