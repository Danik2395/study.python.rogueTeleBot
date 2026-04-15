import json
import hashlib
import random

from typing import Any
from openai import AsyncOpenAI
from os import environ
from dotenv import load_dotenv

from database.database import Database
from data.presets import PROMPTS, ITEMS, ENEMIES, LOG_LABELS, FTEXT

load_dotenv()


class LogHandler:
    """
     Class that converts action log into text via LLM.
     Return already generated action if hash in database.
    """

    def __init__(self, database: Database):
        self.database = database
        self.client = AsyncOpenAI(api_key=environ['DEEPSEEK_API_KEY'], base_url="https://api.deepseek.com")
        self.state: dict

    async def render(self, log: dict[str, Any], state: dict, state_type: str) -> str:
        self.state = state

        log_type = log.get("type")
        log_hash = self._hash_log(log)

        menu_context = state["menu_context"]
        opened_menu = menu_context["opened_menu"]

        player = state["player"]
        base_health = player["base_health"]
        current_health = player["current_health"]
        base_defence = player["base_defence"]
        base_damage = player["base_damage"]
        base_speed = player["base_speed"]

        starus_bar = f"❤️ {current_health}/{base_health} | ⚔️ {base_damage} | 🛡 {base_defence} | ⚡ {base_speed}"

        if await self.database.is_log_cash_exists(log_hash):
            cash_text = await self.database.get_log_cash(log_hash)

            if opened_menu not in ("menu_recall", "menu_expanse", "menu_help"):
                cash_text += f"\n\n{starus_bar}"

        match log_type:
            case "move":
                text = await self._render_move(log)
            case "death":
                text = await self._render_death(log)
            case "combat":
                text = await self._render_combat(log)
            case "inventory":
                text = await self._render_inventory(log)
            case "entrance":
                text = await self._render_entrance(log)
            case "continue":
                text = await self._render_continue(log)
            case "recall":
                text = await self._render_recall(log)
            case _:
                text =  "Событие произошло, но текст для него пока не готов."

        await self.database.save_log_cash(log_hash, text)

        if opened_menu not in ("menu_recall", "menu_expance", "menu_help"):
            text+= f"\n\n{starus_bar}"

        return text

    def _hash_log(self, log: dict[str, Any]) -> str:
        log_str = json.dumps(log, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(log_str.encode('utf-8')).hexdigest()

    async def _generate_text(self, specified_system_content: str, user_content: str) -> str | None:
        """
        Returns LLM generated text
        """

        system_content = f"{PROMPTS["general_system_prompt"]}\n{specified_system_content}"

        completion = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ],
            temperature=0.7
        )
        return completion.choices[0].message.content

    async def _render_move(self, log: dict[str, Any]) -> str:
        room_index = log.get("room_index")
        direction = log.get("direction", "в неизвестном направлении")
        is_fork = log.get("is_fork", False)
        is_new_room = log.get("is_new_room", False)
        event = log.get("event", None)
        consequence = log.get("consequence")

        floor = self.state["floor"]
        rooms = floor["rooms"]
        room = rooms[room_index]

        room_text_name = room["text_name"]
        room_mood = room["mood"]
        is_cleared = room["cleared"]
        room_enemies = room["enemies"]
        room_loot = room["loot"]
        room_doors = room["doors"]

        user_content = f"""
            Movement direction: {direction}
            Room by count: {room_index}
            Is the room new: {is_new_room}
            Moved to fork (more one or more unexplored rooms): {is_fork}
            Room name: {room_text_name}
            How it is in the room: {room_mood}
            If room cleared form enemies: {is_cleared}
            Room Enemies: {room_enemies}
            What loot is in room: {room_loot}
            Event that happened: {event}
            Room doors: {room_doors}
             Consequences/Effects upon entry: {consequence}
        """

        system_content = PROMPTS["move"]
        text = await self._generate_text(system_content, user_content)

        if not text:
            text = f"Вы переходите в {room_text_name}"

        return text


    async def _render_death(self, log: dict[str, Any]) -> str:
        enemy_key = log.get("enemy")
        damage = log.get("damage")

        enemy = ENEMIES[enemy_key].get("text_name", enemy_key)

        user_content = f"""
            Last attacked enemy: {enemy}
            Damage taken: {damage}
        """

        system_content = PROMPTS["death"]
        text = await self._generate_text(system_content, user_content)

        if not text:
            text = f"Ты погибаешь."
        return text

    async def _render_combat(self, log: dict[str, Any]) -> str:
        action = log.get("action")
        turns = log.get("turns")
        enemies_turn_triggered = log.get("enemies_turn_triggered")
        combat_ended = log.get("combat_ended", False)
        consequence = log.get("consequence")

        consequence_str = ""
        if consequence:
            if isinstance(consequence, dict):
                consequence = [consequence]
            parts = []
            for c in consequence:
                attacker_key = c.get("attacker")
                target_key = c.get("target")
                stat = c.get("stat", "health")
                delta = c.get("delta", 0)
                dead = c.get("dead", False)

                if attacker_key is None:
                    attacker_key = "кто-то"
                if target_key is None:
                    target_key = "кого-то"

                attacker = attacker_key
                target = target_key
                if attacker_key == "player":
                    attacker = "Игрок"
                else:
                    attacker = ENEMIES[attacker_key].get("text_name", attacker_key)

                if target_key == "player":
                    target = "тебя"
                else:
                    target = ENEMIES[target_key].get("text_name", target_key)

                line = f"{attacker} изменяет {stat} у {target} на {delta}."
                if dead:
                    line += f" {target} погибает."
                parts.append(line)

            consequence_str = " ".join(parts)

        user_content = f"""
            Players action: {action}
            Turns remaining: {turns}
            Enemies turn triggered: {enemies_turn_triggered}
            Combat ended: {combat_ended}
            Consequence of the combat: {consequence_str}
        """

        system_content = PROMPTS["combat"]
        text = await self._generate_text(system_content, user_content)

        if not text:
            text = "Бой продолжается."
        return text

    async def _render_inventory(self, log: dict[str, Any]) -> str:
        action = log.get("action")
        item_key_name = log.get("item_key_name", "предмет")
        source = log.get("source")
        move_destination = log.get("move_destination")
        slot = log.get("slot")
        count_delta = log.get("count_delta")
        count_in_source = log.get("count_in_source")
        count_in_destination = log.get("count_in_destination")

        # Преобразуем ключи в читаемые названия
        source_readable = source
        destination_readable = move_destination
        if source is None:
            source_readable = "неизвестно"
        else:
            source_readable = LOG_LABELS[source]

        if move_destination is None:
            destination_readable = "неизвестно"
        else:
            destination_readable = LOG_LABELS[move_destination]

        item_text_name = ITEMS.get(item_key_name, {}).get("text_name", item_key_name)

        user_content = f"""
            Action in inventory: {action}
            Item: {item_text_name} (key: {item_key_name})
            Source: {source_readable} ({source})
            Destination: {destination_readable} ({move_destination})
            Slot: {slot}
            Count delta: {count_delta}
            Count in source: {count_in_source}
            Count in destination: {count_in_destination}
        """

        system_content = PROMPTS["inventory"]
        text = await self._generate_text(system_content, user_content)

        if not text:
            text = f"Действие с предметом {item_text_name}."
        return text

    async def _render_entrance(self, log: dict[str, Any]) -> str:
        current_floor_index = log.get("current_floor_index")
        prompt = log.get("prompt")
        biom_text_name = log.get("biom_text_name")

        user_content = f"""
            Current floor index: {current_floor_index}
            Biom name: {biom_text_name}
            Prompt of the room: {prompt}
        """

        system_content = PROMPTS["entrance"]
        text = await self._generate_text(system_content, user_content)

        if not text:
            text = f"Вы спускаетесь на этаж {current_floor_index}."
        return text

    async def _render_recall(self, log: dict[str, Any]) -> str:
        action = log["action"]
        stat = log["stat"]
        memory_fragments_delta = log["memory_fragments_delta"]
        recall_attempt_status = "failed" if action is None else "success"

        user_content = f"""
            Action in recall menu: {action}
            Recall attempt status: {recall_attempt_status}
            On what stat is action: {stat}
            Memory fragments delta: {memory_fragments_delta}
        """

        system_content = PROMPTS["recall"]
        text = await self._generate_text(system_content, user_content)

        if not text:
            text = f"Вы что-то вспомнили"
        return text

    async def _render_continue(self, log: dict[str, Any]) -> str:
        menu_key_name = log.get("menu")
        if menu_key_name is not None:
            menu_text = random.choice(FTEXT[menu_key_name])
            return menu_text

        user_content = "Continue of the game."

        system_content = PROMPTS["continue"]
        text = await self._generate_text(system_content, user_content)

        if not text:
            text = "Вы находитесь всё там же."
        return text
