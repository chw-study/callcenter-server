from flask import Flask, request
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import ReturnDocument
from bson.json_util import dumps
from bson.son import SON
from bson.objectid import ObjectId
from flask_cors import CORS, cross_origin
from toolz import assoc_in, assoc, dissoc, get_in
import os, sys, logging, json
import datetime as dt
from itertools import islice
import logging
from .calls import hours_ago, get_records, get_needed_calls, get_worker_lookup
from .handlers import new_message_handler

log_level = getattr(logging, os.environ.get('LOG_LEVEL', 'INFO').upper())
logging.basicConfig(level = logging.DEBUG)

# Make app
print('Making app: ' + __name__)
app = Flask(__name__)
CORS(app)

# Connect to Mongo --> TODO: close connection on shutdown hook!
client = MongoClient(
    os.environ.get('MONGO_HOST') or None,
    username = os.environ.get('MONGO_USER') or None,
    password = os.environ.get('MONGO_PASS') or None,
    ssl = bool(os.getenv('MONGO_SSL'))
)

DB = 'healthworkers'

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


# maybe this should just go to a new collection of attempts
@app.route('/messages/<msg_id>/attempt', methods=['POST'])
def handle_attempt(msg_id):
    collection = client[DB].messages
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
    collection = client[DB].messages
    update = collection.find_one_and_update(
        { '_id': ObjectId(msg_id)},
        {'$set': data},
        return_document=ReturnDocument.AFTER)
    return dump(update)

# TODO: remove this and all associated handlers + NLTK?
@app.route('/messages', methods=['POST'])
def new_message():
    collection = client[DB].messages
    msg = {k:request.form[k] for k in ['text', 'phone', 'time', 'run']}
    new_message_handler(collection, msg)
    return 'Success'

@app.route('/messages', methods=['GET'])
def get_articles():
    coll = client[DB].messages
    hours = int(request.args.get('hours', 6))
    percent = float(request.args.get('percent', 0.20))
    start = int(request.args.get('start', 0))
    num = int(request.args.get('num', 1))

    # Get (memoized) district phone-numbers/names from DB
    district = request.args.get('district')
    district_lookup = get_worker_lookup(client[DB].workers, district)

    # get records and return
    needed = get_needed_calls(coll, percent, district_lookup)
    cursor = get_records(coll, needed, hours, district_lookup)
    result = dump(islice(cursor, start+num))
    return result
