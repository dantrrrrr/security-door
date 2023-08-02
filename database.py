import pymongo

client = pymongo.MongoClient("mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@string")
db = client['door']  # Replace 'door' with your database name

users_collection = db['users']
logs_collection = db['logs']
