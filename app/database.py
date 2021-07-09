from motor.motor_asyncio import AsyncIOMotorClient

from app.core import settings


class DataBase:
    client: AsyncIOMotorClient = None


db = DataBase()


async def connect_to_mongo():

    db.client = AsyncIOMotorClient(settings.MONGO_URL)[settings.MONGO_DB]


async def close_mongo_connection():
    db.client.close()
