import pymongo

client = pymongo.MongoClient('mongodb://pacific-thicket-10824.herokuapp.com/tutorial_bot')
users_db = client.get_database()["users_db"]