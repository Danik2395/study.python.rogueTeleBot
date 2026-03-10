import json

class Database:
    def __init__(self):
        self._store = {}

    def get_state(self, user_id: int) -> dict:
        return self._store[user_id]

    def save_state(self, user_id: int, state: dict) -> None:
        self._store[user_id] = state

    def delete_state(self, user_id: int) -> None:
        self._store.pop(user_id, None)
