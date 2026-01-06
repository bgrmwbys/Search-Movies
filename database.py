import motor.motor_asyncio
import re
from config import MONGO_URI, DB_NAME

class Database:
    def __init__(self):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        # אתחול ראשוני כדי למנוע שגיאות NoneType
        self.set_db_name(DB_NAME)

    def set_db_name(self, name):
        self.db = self._client[name]
        self.files = self.db.files
        self.users = self.db.users
        self.groups = self.db.groups
        self.settings = self.db.settings
        self.watched = self.db.watched
        print(f"✅ Database switched to: {name}")

    async def add_user(self, user_id, first_name):
        user = await self.users.find_one({'_id': user_id})
        if not user:
            await self.users.insert_one({'_id': user_id, 'first_name': first_name})
            return True
        return False

    async def add_group(self, chat_id, title):
        group = await self.groups.find_one({'_id': chat_id})
        if not group:
            await self.groups.insert_one({'_id': chat_id, 'title': title})
            return True
        return False

    async def get_all_users(self):
        return self.users.find({})

    async def get_all_groups(self):
        return self.groups.find({})

    async def save_file(self, file_data):
        exist = await self.files.find_one({'file_unique_id': file_data['file_unique_id']})
        if exist:
            return "duplicate"
        await self.files.insert_one(file_data)
        return "saved"

    async def get_file(self, _id):
        from bson.objectid import ObjectId
        try:
            return await self.files.find_one({'_id': ObjectId(_id)})
        except:
            return None

    async def search_files(self, query):
        clean_query = re.sub(r'[._\-]', ' ', query)
        words = clean_query.split()
        
        regex_list = []
        for word in words:
            escaped_word = re.escape(word)
            regex_list.append(re.compile(escaped_word, re.IGNORECASE))
        
        cursor = self.files.find({"file_name": {"$all": regex_list}})
        results = await cursor.to_list(length=100)
        
        def sort_key(item):
            name = item.get('file_name', '')
            s = re.search(r'(?:עונה|season|s)\s*(\d+)', name, re.I)
            e = re.search(r'(?:פרק|episode|e)\s*(\d+)', name, re.I)
            season = int(s.group(1)) if s else 0
            episode = int(e.group(1)) if e else 0
            return (season, episode)

        results.sort(key=sort_key)
        return results

    async def get_settings(self, chat_id):
        settings = await self.settings.find_one({'_id': chat_id})
        if not settings:
            return {'results_per_page': 10, 'display_mode': 'inline', 'search_trigger': 'all', 'show_image': True}
        return settings

    async def update_settings(self, chat_id, key, value):
        await self.settings.update_one({'_id': chat_id}, {'$set': {key: value}}, upsert=True)

    async def add_watched_channel(self, chat_id):
        await self.watched.update_one({'_id': chat_id}, {'$set': {'_id': chat_id}}, upsert=True)

    async def remove_watched_channel(self, chat_id):
        await self.watched.delete_one({'_id': chat_id})

    async def get_watched_channels(self):
        channels = await self.watched.find({}).to_list(length=1000)
        return [c['_id'] for c in channels]

    async def delete_all_files(self):
        result = await self.files.delete_many({})
        return result.deleted_count

    async def delete_all_users(self):
        result = await self.users.delete_many({})
        return result.deleted_count

    async def delete_all_groups(self):
        result = await self.groups.delete_many({})
        return result.deleted_count

    # --- מחיקה חכמה לשגיאות ---
    async def delete_file_by_unique_id(self, unique_id):
        await self.files.delete_one({'file_unique_id': unique_id})

    async def delete_files_by_chat_id(self, chat_id):
        result = await self.files.delete_many({'chat_id': chat_id})
        return result.deleted_count

db = Database()
