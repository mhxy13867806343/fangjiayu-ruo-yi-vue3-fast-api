import asyncio
from config.database import engine
from sqlalchemy import text

async def check_users():
    async with engine.connect() as conn:
        result = await conn.execute(text('SELECT user_id, register_time, create_time FROM h5_user'))
        users = result.fetchall()
        for user in users:
            print(f'User ID: {user[0]}, Register Time: {user[1]}, Create Time: {user[2]}')

if __name__ == "__main__":
    asyncio.run(check_users())
