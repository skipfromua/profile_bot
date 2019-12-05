import pymongo

client = pymongo.MongoClient('mongodb://heroku_vb5m3v2n:2mg5essj5ubph7o641fhroiun@ds157923.mlab.com:57923/heroku_vb5m3v2n?retryWrites=false')
users_db = client.get_database()["users_db"]