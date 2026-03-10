import random
random.seed(42)

from pprint import pprint
from core.rogue_interface import RogueInterface

USER_ID = 1
interface = RogueInterface()

def call(action: str) -> dict:
    if action == "init_run":
        return interface.init_run(USER_ID)
    if action == "move_to_fork":
        return interface.move_to_fork(USER_ID)
    if action.startswith("move_"):
        return interface.move(USER_ID, action[5:])
    if action.startswith("attack_"):
        return interface.attack(USER_ID, action[7:])
    if action.startswith("take_"):
        return interface.take_item(USER_ID, action[5:])
    return {"error": f"unknown: {action}"}

pprint(interface.init_run(USER_ID))

while True:
    raw = input("\n> ").strip()
    if raw in ("q", "quit"):
        break
    if raw in ("show run", "sh run", "show rn", "sh rn"):
        pprint(interface.database.get_state(USER_ID))
    pprint(call(raw))
