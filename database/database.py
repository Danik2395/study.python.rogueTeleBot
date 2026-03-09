import json

class Database:
    """
    Plug for database
    """

    def __init__(self) -> None:
        pass

    def get_state(self, user_id: int) -> dict:
        with open("sample_run.json", "r", encoding="utf-8") as f:
            run_states =  json.load(f)
            return run_states[str(user_id)]

    def save_state(self, user_id: int, state: dict) -> None:
        pass
