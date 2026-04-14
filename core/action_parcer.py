from data.presets import COMMAND_SCHEMAS
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

    # def __init__(self):
    #     self.schemas = BRIDGE_SPEC["command_schemas"]
    #
    def parse(self, action_str: str) -> "ParsedAction":
        command, *args = action_str.split(":")

        schema = COMMAND_SCHEMAS[command]
        arg_names = schema["args"]

        params = {}
        for i, name in enumerate(arg_names):
            params[name] = args[i] if i < len(args) else None # Iterates on the arg names while there are some

        return ParsedAction(command=command, params=params)
