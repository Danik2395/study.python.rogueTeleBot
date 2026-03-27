from data.presets import BRIDGE_SPEC
from dataclasses import dataclass

@dataclass
class ParsedAction:
    command: str
    params: dict[str, str]

class ActionParser:
    """
    Class to decompose complex command
    Returns
    """

    def __init__(self):
        self.schemas = BRIDGE_SPEC["command_schemas"]

    def parse(self, action_str: str) -> "ParsedAction":
        command, *args = action_str.split(":")

        schema = self.schemas[command]
        arg_names = schema["args"]

        params = {}
        for i, name in enumerate(arg_names):
            params[name] = args[i]

        return ParsedAction(command=command, params=params)
