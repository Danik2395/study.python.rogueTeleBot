import asyncio
import random

from data.presets import Contract
random.seed(42)

from pprint import pprint
from core.rogue_interface import RogueInterface, process_action

# USER_ID: int = 1

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

        action_log = await process_action(user_id, action, interface)

        pprint(action_log)

    await interface.database.close()

if __name__ == "__main__":
    asyncio.run(main())
