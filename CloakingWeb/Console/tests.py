from django.test import TestCase

# Create your tests here.
from pymongo import MongoClient

# Requires the PyMongo package.
# https://api.mongodb.com/python/current

client = MongoClient('mongodb://34.151.127.107:27017/')
result = client['ABPage']['access'].aggregate([
    {
        '$match': {
            'Referer': 'https://www.google.com/', 
            'PageName': 'index', 
            'ABPage': 'B'
        }
    }, {
        '$project': {
            '_id': 1, 
            'state': 1
        }
    }, {
        '$group': {
            '_id': '$state', 
            'ids': {
                '$push': '$_id'
            }
        }
    }
])

need_delete_id = [res["ids"][1] for res in result]
print(len(need_delete_id))

