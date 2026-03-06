from typing import Any


class LogSystem:
    """
     Plug for the LogSystem
    """

    def render(self, log: dict[str, Any]) -> str:
        log_type = log.get("type")

        if log_type == "move":
            return self._render_move(log)

        if log_type == "death":
            return self._render_death(log)

        if log_type == "combat":
            return self._render_combat(log)

        return "Событие произошло, но текст для него пока не готов."

    def _render_move(self, log: dict[str, Any]) -> str:
        room_index = log.get("room_index")
        is_fork = log.get("is_fork", False)
        is_new_room = log.get("is_new_room", False)

        if room_index is None:
            return "Ты не смог пройти дальше."

        if is_new_room and is_fork:
            return f"Ты входишь в новую комнату {room_index}. Здесь несколько путей."

        if is_new_room:
            return f"Ты входишь в новую комнату {room_index}."

        if is_fork:
            return f"Ты возвращаешься в комнату {room_index}. Перед тобой снова развилка."

        return f"Ты переходишь в комнату {room_index}."

    def _render_death(self, log: dict[str, Any]) -> str:
        enemy = log.get("enemy", "враг")
        damage = log.get("damage", 0)
        return f"{enemy} наносит {damage} урона. Ты погибаешь."

    def _render_item(self, log: dict[str, Any]) -> str:
        item = log.get("transition_item", "предмет")
        target = log.get("transition_into", "инвентарь")
        is_items_left = log.get("is_items_left", True)

        if is_items_left:
            return f"Ты берёшь {item} и переносишь в {target}."

        return f"Ты берёшь {item} и переносишь в {target}. Больше предметов здесь нет."

    def _render_combat(self, log: dict[str, Any]) -> str:
        consequences = log.get("consequence")

        if not consequences:
            text = "Схватка продолжается."
        else:
            if isinstance(consequences, dict):
                consequences = [consequences]

            parts: list[str] = []
            for c in consequences:
                attacker = c.get("attacker", "кто-то")
                target = c.get("target", "кого-то")
                stat = c.get("stat", "health")
                delta = c.get("delta", 0)
                dead = c.get("dead", False)

                line = f"{attacker} изменяет {stat} у {target} на {delta}."
                if dead:
                    line += f" {target} погибает."
                parts.append(line)

            text = " ".join(parts)

        turns = log.get("turns")
        if turns is not None:
            text += f" Ходов осталось: {turns}."

        if log.get("enemies_turn_triggered"):
            text += " Враги отвечают."

        if log.get("combat_ended"):
            text += " Бой окончен."

        return text
