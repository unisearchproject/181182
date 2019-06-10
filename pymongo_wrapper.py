class PyMongoWrapper:

    def __init__(self, mongo_client, mongo_db):
        self.mongo_client = pymongo.MongoClient(mongo_client)
        self.db = self.mongo_client[mongo_db]

    def set_state(self, user_id, function):
        # устанавливаем состояние для юзера по user_id и функции
        self.db.users.update_one(
            {'user_id': int(user_id)},
            {'$set': {'state': function.__name__}},
            upsert=True
        )