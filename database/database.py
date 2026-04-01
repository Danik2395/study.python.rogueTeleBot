import aiosqlite
import json
from os import getenv
from dotenv import load_dotenv

load_dotenv()
DATABASE = getenv("DATABASE_PATH")

class Database:
    def __init__(self, db, cur):
        self.db = db
        self.cur = cur

    @classmethod
    async def create(cls) -> "Database":
        db = await aiosqlite.connect("database/rogue_database.db")
        cur = await db.cursor()

        instance = cls(db, cur)
        await instance._create_users_table()

        return instance

    async def get_user_run_state(self, user_id: int) -> dict:
        await self.cur.execute(
            "SELECT user_active_run FROM users_data WHERE user_id = ?", (user_id,)
        )
        row = await self.cur.fetchone()
        return json.loads(row[0]) if row else {}

    async def get_user_global_data(self, user_id: int) -> dict:
        await self.cur.execute(
            "SELECT user_global_data FROM users_data WHERE user_id = ?", (user_id,)
        )
        row = await self.cur.fetchone()
        return json.loads(row[0]) if row else {}

    async def save_user_run_state(self, user_id: int, state: dict) -> None:
        await self.cur.execute("""
            INSERT INTO users_data (user_id, user_active_run)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET user_active_run = excluded.user_active_run
        """, (user_id, json.dumps(state)))
        await self.db.commit()

    async def save_user_global_data(self, user_id: int, data: dict) -> None:
        await self.cur.execute("""
            INSERT INTO users_data (user_id, user_global_data)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET user_global_data = excluded.user_global_data
        """, (user_id, json.dumps(data)))
        await self.db.commit()

    async def is_user_exists(self, user_id: int) -> bool:
        await self.cur.execute(
                "select 1 from users_data where user_id = ?", # Only check wheather user exists
                (user_id,)
                )
        row = await self.cur.fetchone()
        return True if row else False

    async def _create_users_table(self) -> None:
        table = """
        create table if not exists users_data (
                user_id integer primary key,
                user_active_run json,
                user_global_data json
                );
        """

        await self.cur.execute(table)
        await self.db.commit()

    async def close(self) -> None:
        await self.db.close()
