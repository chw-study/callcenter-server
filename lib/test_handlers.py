from .handlers import *
from pymongo import MongoClient
import pytest
import datetime as dt

@pytest.fixture(scope="module")
def collection():
    client = MongoClient()
    collection = client['hw-test'].messages
    yield collection
    collection.drop()
    client.close()

messages = [
    {'text': 'foo', 'phone': '+234', 'time': '2017-11-20T20:48:00.897894Z', 'run': '7723478'}
]

def test_new_message_handler(collection):
    new_message_handler(collection, messages[0])
    found = list(collection.find())
    assert(found[0]['workerPhone'] == '+234')
    assert(found[0]['text'] == 'foo')
    assert(found[0]['run'] == 7723478)
    assert(type(found[0]['timestamp']) == dt.datetime)
    collection.drop()

def test_new_message_handler_does_not_write_if_no_text(collection):
    try:
        new_message_handler(collection, {'phone': '234'})
    except:
        pass
    found = list(collection.find())
    assert(len(found) == 0)
    collection.drop()


def test_new_message_handler_works_with_default_date(collection):
    new_message_handler(collection, {'phone': '234', 'text': 'foo'})
    found = list(collection.find())
    assert(len(found) == 1)
    assert(type(found[0]['timestamp']) == dt.datetime)
    collection.drop()

def test_parse_text():
    parsed = parse_text('+234-5098 034 nand,an .rao f/oo')
    assert(parsed == {'phone': 2345098034, 'name': 'nand an rao foo'})
    parsed = parse_text('nand f^doo. +54 (542).545')
    assert(parsed == {'phone': 54542545, 'name': 'nand fdoo'})
