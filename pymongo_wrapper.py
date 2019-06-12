import pymongo
from bson.objectid import ObjectId

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

    def get_state(self, user_id):
        # получаем состояние юзера по user_id
        req = self.db.users.find_one({'user_id': int(user_id)}, {'state': 1})
        return req['state'] if req else None

    ###

    def set_vars(self, user_id: int, **set_values):
        # сохраняем нужные переменные для юзера
        self.db.vars.update_one(
            {'user_id': int(user_id)},
            {'$set': set_values},
            upsert=True
        )

    def get_vars(self, user_id: int):
        # получаем все переменные юзера
        return list(
            self.db.vars.find_one({'user_id': int(user_id)})
        )

    def get_var(self, user_id: int, var: str):
        # получаем одну нужную переменную юзера
        return self.db.vars.find_one(
            {'user_id': int(user_id)},
            {'_id': 0, var: 1}
        )[var]

    ###

    def save_programs(self, univer_title, programs_url):
        # сохраняем название и ссылку на программы универа
        insert = self.db.urls.insert_one(
            {
                'url': programs_url,
                'title': univer_title
            }
        )
        return str(insert.inserted_id)

    def get_programs(self, object_id: str):
        # получаем данные, что сохраняет функция выше
        return self.db.urls.find_one(
            {'_id': ObjectId(object_id)}, {'_id': 0}
        )