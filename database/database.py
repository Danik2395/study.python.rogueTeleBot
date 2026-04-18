import aiosqlite
import json
from os import environ
from dotenv import load_dotenv

load_dotenv()
DATABASE = environ["DATABASE_PATH"]

class Database:
    def __init__(self, db, cur):
        self.db = db
        self.cur = cur

    @classmethod
    async def create(cls) -> "Database":
        db = await aiosqlite.connect(DATABASE)
        cur = await db.cursor()

        instance = cls(db, cur)
        await instance._create_users_table()
        await instance._create_ui_message_table()
        await instance._create_cash_table()

        return instance

    async def close(self) -> None:
        await self.db.close()

    # === Getters ===

    async def is_user_exists(self, user_id: int) -> bool:
        await self.cur.execute(
                "select 1 from Users_data where user_id = ?", # Only check wheather user exists
                (user_id,)
                )
        row = await self.cur.fetchone()
        return True if row else False

    async def is_log_cash_exists(self, log_hash: str) -> bool:
        await self.cur.execute(
                "select 1 from Log_cash where log_hash = ?",
                (log_hash,)
                )
        row = await self.cur.fetchone()
        return True if row else False

    async def get_user_run_state(self, user_id: int) -> dict:
        await self.cur.execute(
            "SELECT user_run_state FROM Users_data WHERE user_id = ?", (user_id,)
        )
        row = await self.cur.fetchone()
        return json.loads(row[0]) if row else {}

    async def get_user_global_data(self, user_id: int) -> dict:
        await self.cur.execute(
            "SELECT user_global_data FROM Users_data WHERE user_id = ?", (user_id,)
        )
        row = await self.cur.fetchone()
        return json.loads(row[0]) if row else {}

    async def get_ui_message_id(self, user_id: int) -> int:
        await self.cur.execute(
            "SELECT ui_message_id FROM UI_messages WHERE user_id = ?", (user_id,)
        )
        row = await self.cur.fetchone()
        return row[0] if row else 0

    async def get_log_cash(self, log_hash: str) -> str:
        await self.cur.execute(
            "SELECT log_text FROM Log_cash WHERE log_hash = ?", (log_hash,)
        )
        row = await self.cur.fetchone()
        return row[0] if row else ""

    # === Setters ===

    async def save_user_run_state(self, user_id: int, state: dict) -> None:
        await self.cur.execute("""
            INSERT INTO Users_data (user_id, user_run_state)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET user_run_state = excluded.user_run_state
        """, (user_id, json.dumps(state)))
        await self.db.commit()

    async def save_user_global_data(self, user_id: int, data: dict) -> None:
        await self.cur.execute("""
            INSERT INTO Users_data (user_id, user_global_data)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET user_global_data = excluded.user_global_data
        """, (user_id, json.dumps(data)))
        await self.db.commit()

    async def save_ui_message_id(self, user_id: int, ui_message_id: int) -> None:
        await self.cur.execute("""
            INSERT INTO UI_messages (user_id, ui_message_id)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET ui_message_id = excluded.ui_message_id
        """, (user_id, ui_message_id))
        await self.db.commit()

    async def save_log_cash(self,log_hash: str, log_text: str) -> None:
        await self.cur.execute("""
            INSERT INTO Log_cash (log_hash, log_text)
            VALUES (?, ?)
            ON CONFLICT(log_hash) DO UPDATE SET log_text = excluded.log_text
        """, (log_hash, log_text))
        await self.db.commit()

    # === Definitions ===

    async def _create_users_table(self) -> None:
        table = """
        create table if not exists Users_data (
                user_id integer primary key,
                user_run_state json,
                user_global_data json
                );
        """

        await self.cur.execute(table)
        await self.db.commit()

    async def _create_ui_message_table(self) -> None:
        table = """
        create table if not exists UI_messages (
                user_id integer primary key,
                ui_message_id int
                );
        """

        await self.cur.execute(table)
        await self.db.commit()

    async def _create_cash_table(self) -> None:
        table = """
        create table if not exists Log_cash (
                log_hash text primary key,
                log_text text not null,
                created_time Timestamp default current_timestamp
                );
        """

        await self.cur.execute(table)
        await self.db.commit()
