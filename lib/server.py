from flask import Flask, request, Response
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import ReturnDocument
from bson.json_util import dumps, loads
from bson.son import SON
from bson.objectid import ObjectId
from flask_cors import CORS, cross_origin
from toolz import assoc_in, assoc, dissoc, get_in
import os, sys, logging, json
import datetime as dt
from itertools import islice
import logging
import redis

log_level = getattr(logging, os.environ.get('LOG_LEVEL', 'INFO').upper())
logging.basicConfig(level = logging.DEBUG)

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

r = redis.StrictRedis(host=os.getenv('REDIS_HOST', 'localhost'),
                      password=os.getenv('REDIS_PASS', None),
                      port=os.getenv('REDIS_PORT', 6379),
                      db=os.getenv('REDIS_DB', 0),
                      decode_responses=True)

@app.route('/messages/event', methods=['POST'])
def handle_event():
    collection = client[DB].events

    # we need to reconstruct the mongo datatypes (date)
    event = loads(request.data)
    event['event_time'] = dt.datetime.utcnow()
    update = collection.insert_one(event)
    return str(update.inserted_id)

@app.route('/messages', methods=['GET'])
def get_articles():
    district = request.args.get('district')
    result = r.rpop(district)
    if result:
        return Response(result, content_type = 'application/json')
    else:
        return 'Sorry! No records for that district', 404
