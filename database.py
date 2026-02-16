import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        # MongoDB से जुड़ना
        self.client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URL"))
        self.db = self.client["Immortal_Anibot"]
        self.col = self.db["files"]

    async def save_file(self, file_hash, file_data):
        """फाइल की जानकारी सेव करना"""
        doc = {
            "file_hash": file_hash,
            "file_name": file_data['name'],
            "mirrors": file_data['mirrors'],
            "hls_link": f"{os.getenv('CF_DOMAIN')}/watch/{file_hash}"
        }
        await self.col.update_one({"file_hash": file_hash}, {"$set": doc}, upsert=True)

db = Database()