import aiosqlite
import json


class Database:
    def __init__(self, db, cur):
        self.db = db
        self.cur = cur

    @classmethod
    async def create(cls) -> "Database":
        db = await aiosqlite.connect("database/rogue_database.db")
        cur = await db.cursor()

        instance = cls(db, cur)
        await instance._create_users_data_table()
        await instance._create_users_state_table()

        return instance

    async def get_state(self, user_id: int) -> dict:
        await self.cur.execute(
            "SELECT user_active_run FROM users_state WHERE user_id = ?", (user_id,)
        )
        row = await self.cur.fetchone()
        return json.loads(row[0]) if row else {}

    async def save_state(self, user_id: int, state: dict) -> None:
        await self.cur.execute(
            "insert or replace into users_state (user_id, user_active_run) values (?, ?)",
            (user_id, json.dumps(state))
        )
        await self.db.commit()

    async def _create_users_data_table(self) -> None:
        table = """
        create table if not exists users_data (
                user_id integer primary key,
                user_total_runs int not null,
                max_floor_index int not null,
                global_upgrades json
                );
        """

        await self.cur.execute(table)
        await self.db.commit()

    async def _create_users_state_table(self) -> None:
        table = """
        create table if not exists users_state(
                user_id integer primary key,
                user_active_run json
                )
        """

        await self.cur.execute(table)
        await self.db.commit()

    async def close(self) -> None:
        await self.db.close()
