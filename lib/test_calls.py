from mongomock import MongoClient
from datetime import datetime, timedelta
from .calls import *
import pytest
from pymongo import MongoClient

records = [
    { 'name': 'mark', 'worker': 'bar', 'called': False, 'attempts': [hours_ago(2), hours_ago(0.5)]},
    { 'name': 'mark', 'worker': 'bar', 'called': False, 'attempts': [datetime.utcnow() - timedelta(hours = 1.5)]},
    { 'name': 'mark', 'worker': 'bar', 'called': False},
    { 'name': 'mark', 'worker': 'bar', 'called': True},
    { 'name': 'mark', 'worker': 'foo', 'called': True},
    { 'name': 'mark', 'worker': 'foo', 'called': True}
]

@pytest.fixture(scope="module")
def collection():
    client = MongoClient()
    collection = client['hw-test'].messages
    collection.insert_many(records)
    yield collection
    collection.drop()
    client.close()

def test_group_call_counts(collection):
    counts = get_call_counts(collection, 1.0)
    grouped = list(group_call_counts(counts))
    assert(grouped == [{'worker': 'bar', 'count': (1,2)}, {'worker': 'foo', 'count': (2,0)}])
    counts = get_call_counts(collection, 2.0)
    grouped = list(group_call_counts(counts))
    assert(grouped == [{'worker': 'bar', 'count': (1,1)}, {'worker': 'foo', 'count': (2,0)}])

def test_get_call_counts(collection):
    counts = list(get_call_counts(collection, 1.0))
    assert(counts == [{'_id': {'worker': 'bar', 'called': False}, 'count': 2}, {'_id': {'worker': 'bar', 'called': True}, 'count': 1}, {'_id': {'worker': 'foo', 'called': True}, 'count': 2}])

# def test_get_needed_calls(collection):
#     assert(get_needed_calls(collection, 1.0, 0.5) == [{'worker': 'bar', 'needed': 1}, {'worker': 'foo', 'needed': 1}])

def test_needed_calls_gets_calls():
    assert(needed_calls({ 'worker': 'bar', 'count': (2,5)}, 0.5) == 2)
    assert(needed_calls({ 'worker': 'bar', 'count': (2,6)}, 0.5) == 2)
    assert(needed_calls({ 'worker': 'bar', 'count': (2,7)}, 0.5) == 3)

def test_needed_calls_handles_zeros():
    assert(needed_calls({ 'worker': 'bar', 'count': (2,0)}, 0.5) == 0)
    assert(needed_calls({ 'worker': 'bar', 'count': (0,7)}, 0.5) == 4)
