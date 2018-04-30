from mongomock import MongoClient
from datetime import datetime, timedelta
from .calls import *
import pytest
from pymongo import MongoClient

records = [
    { 'name': 'mark', 'workerPhone': 'bar', 'called': False, 'attempts': [hours_ago(2), hours_ago(0.5)]},
    { 'name': 'mark', 'workerPhone': 'bar', 'called': False, 'attempts': [datetime.utcnow() - timedelta(hours = 1.5)]},
    { 'name': 'mark', 'workerPhone': 'bar', 'called': False},
    { 'name': 'mark', 'workerPhone': 'bar', 'called': True},
    { 'name': 'mark', 'workerPhone': 'foo', 'called': True},
    { 'name': 'mark', 'workerPhone': 'foo', 'called': True},
    { 'text': 'baz'}
]

@pytest.fixture(scope="module")
def collection():
    client = MongoClient()
    collection = client['hw-test'].messages
    collection.insert_many(records)
    yield collection
    collection.drop()
    client.close()


def test_needed_calls(collection):
    needed = list(get_needed_calls(collection, 1.0))
    assert(needed == [{'workerPhone': 'bar', 'needed': 3}, {'workerPhone': 'foo', 'needed': 0}])

def test_group_call_counts(collection):
    counts = get_call_counts(collection)
    grouped = list(group_call_counts(counts))
    assert(grouped == [{'workerPhone': 'bar', 'count': (1,3)}, {'workerPhone': 'foo', 'count': (2,0)}])

def test_get_call_counts(collection):
    counts = list(get_call_counts(collection))
    assert(counts == [{'_id': {'workerPhone': 'bar', 'called': False}, 'count': 3}, {'_id': {'workerPhone': 'bar', 'called': True}, 'count': 1}, {'_id': {'workerPhone': 'foo', 'called': True}, 'count': 2}])

def test_needed_calls_gets_calls():
    assert(needed_calls({ 'workerPhone': 'bar', 'count': (2,5)}, 0.5) == 2)
    assert(needed_calls({ 'workerPhone': 'bar', 'count': (2,6)}, 0.5) == 2)
    assert(needed_calls({ 'workerPhone': 'bar', 'count': (2,7)}, 0.5) == 3)

def test_needed_calls_handles_zeros():
    assert(needed_calls({ 'workerPhone': 'bar', 'count': (2,0)}, 0.5) == 0)
    assert(needed_calls({ 'workerPhone': 'bar', 'count': (0,7)}, 0.5) == 4)

def test_get_records_does_not_return_any_if_none_fit_bill(collection):
    needed = [{'workerPhone': 'foo', 'needed': 1}, {'workerPhone': 'bar', 'needed': 0}]
    recs = list(get_records(collection, needed, 0.25))
    assert(len(recs) == 0)

def test_get_records_listens_to_hours(collection):
    needed = [{'workerPhone': 'foo', 'needed': 1}, {'workerPhone': 'bar', 'needed': 2}]
    recs = list(get_records(collection, needed, 5.00))
    assert(len(recs) == 1)
    recs = list(get_records(collection, needed, 1.00))
    assert(len(recs) == 2)
