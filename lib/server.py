from flask import Flask, request
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import ReturnDocument
from bson.json_util import dumps
from bson.son import SON
from bson.objectid import ObjectId
import json
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup
from toolz import assoc_in, assoc, dissoc
import os
import sys
import datetime as dt
import logging
from itertools import islice
from .calls import hours_ago

# Make app
app = Flask(__name__)
CORS(app)

# # Connect to Mongo --> TODO: close connection on shutdown hook!
client = MongoClient(
    host = os.environ.get('MONGO_HOST') or None
)

def dump(raw):
    id_fixer = lambda r: assoc(r, '_id', str(r['_id']))
    try:
        return dumps([id_fixer(r) for r in raw])
    except TypeError as e:
        pass
    try:
        return dumps(id_fixer(raw))
    except AttributeError:
        return dumps(raw)




@app.route('/messages/<msg_id>/attempt', methods=['POST'])
def handle_attempt(msg_id):
    collection = client['healthworkers'].messages
    time = dt.datetime.now()
    update = collection.find_one_and_update(
        { '_id': ObjectId(msg_id)},
        {'$push': {'attempts': time }},
        return_document=ReturnDocument.AFTER)
    return dump(update)

@app.route('/messages/<msg_id>', methods=['PUT'])
def update_message(msg_id):
    data = request.json
    print(data)
    collection = client['healthworkers'].messages
    update = collection.find_one_and_update(
        { '_id': ObjectId(msg_id)},
        {'$set': data},
        return_document=ReturnDocument.AFTER)
    return dump(update)

@app.route('/messages', methods=['POST'])
def new_message():
    data = request.json
    print(data)
    return 'Success'

@app.route('/messages', methods=['GET'])
def get_articles():

    collection = client['healthworkers'].messages
    # start = int(request.args.get('start')) or 0
    # days = int(request.args.get('days')) or 10

    # find out
    ret = list(collection.find())
    return dump(ret)
    # l = list(cursor)[0: start+20]
    # return dumps(map(lambda x: x['item'] , l))
