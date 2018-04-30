from mongomock import MongoClient
from datetime import datetime, timedelta
from .calls import *
import pytest
from pymongo import MongoClient

records = [
    { 'name': 'mark', 'workerPhone': 'bar', 'attempts': [hours_ago(2), hours_ago(0.5)]},
    { 'name': 'mark', 'workerPhone': 'bar', 'attempts': [datetime.utcnow() - timedelta(hours = 1.5)]},
    { 'name': 'mark', 'workerPhone': 'bar'},
    { 'name': 'mark', 'workerPhone': 'bar', 'called': True},
    { 'name': 'mark', 'workerPhone': 'foo', 'called': True},
    { 'name': 'mark', 'workerPhone': 'foo', 'called': True},
    { 'name': 'clue', 'workerPhone': 'baz'},
    { 'text': 'baz'}
]

workers = [
    { 'name': 'bob', 'reporting_number': 'bar', 'chw_district': 'test'},
    { 'name': 'sally', 'reporting_number': 'foo', 'chw_district': 'test'},
    { 'name': 'mark', 'reporting_number': 'baz', 'chw_district': 'other'}
]

@pytest.fixture(scope="module")
def collection():
    client = MongoClient()
    db = client['hw-test']
    collection = db.messages
    collection.insert_many(records)
    yield collection
    collection.drop()
    client.close()

@pytest.fixture(scope="module")
def workers_coll():
    client = MongoClient()
    db = client['hw-test']
    db.workers.insert_many(workers)
    yield db.workers
    db.workers.drop()
    client.close()


def test_needed_calls(collection):
    needed = list(get_needed_calls(collection, 1.0,  {'foo': 'sally', 'bar': 'bob'}))
    assert(needed == [{'workerPhone': 'bar', 'needed': 3}, {'workerPhone': 'foo', 'needed': 0}])

def test_needed_calls_filters_numbers(collection):
    needed = list(get_needed_calls(collection, 1.0,  {'bar': 'bob'}))
    assert(needed == [{'workerPhone': 'bar', 'needed': 3}])

def test_group_call_counts(collection):
    counts = get_call_counts(collection, {'foo': 'sally', 'bar': 'bob'})
    grouped = list(group_call_counts(counts))
    assert(grouped == [{'workerPhone': 'bar', 'count': (1,3)}, {'workerPhone': 'foo', 'count': (2,0)}])

def test_get_call_counts(collection):
    counts = list(get_call_counts(collection,  {'foo': 'sally', 'bar': 'bob'}))
    assert(counts == [{'_id': {'workerPhone': 'bar'}, 'count': 3}, {'_id': {'workerPhone': 'bar', 'called': True}, 'count': 1}, {'_id': {'workerPhone': 'foo', 'called': True}, 'count': 2}])

def test_get_call_counts_filters_numbers(collection):
    counts = list(get_call_counts(collection,  {'foo': 'sally'}))
    assert(counts == [{'_id': {'workerPhone': 'foo', 'called': True}, 'count': 2}])

def test_needed_calls_gets_calls():
    assert(needed_calls({ 'workerPhone': 'bar', 'count': (2,5)}, 0.5) == 2)
    assert(needed_calls({ 'workerPhone': 'bar', 'count': (2,6)}, 0.5) == 2)
    assert(needed_calls({ 'workerPhone': 'bar', 'count': (2,7)}, 0.5) == 3)

def test_needed_calls_handles_zeros():
    assert(needed_calls({ 'workerPhone': 'bar', 'count': (2,0)}, 0.5) == 0)
    assert(needed_calls({ 'workerPhone': 'bar', 'count': (0,7)}, 0.5) == 4)

def test_get_records_does_not_return_any_if_none_fit_bill(collection):
    lookup = {'foo': 'sally', 'bar': 'bob'}
    needed = [{'workerPhone': 'foo', 'needed': 1}, {'workerPhone': 'bar', 'needed': 0}]
    recs = list(get_records(collection, needed, 0.25, lookup))
    assert(len(recs) == 0)

def test_get_records_listens_to_hours(collection, workers_coll):
    lookup = get_worker_lookup(workers_coll, 'test')
    needed = [{'workerPhone': 'foo', 'needed': 1}, {'workerPhone': 'bar', 'needed': 2}]
    recs = list(get_records(collection, needed, 5.00, lookup))
    assert(len(recs) == 1)
    assert(recs[0]['workerName'] == 'bob')
    recs = list(get_records(collection, needed, 1.00, lookup))
    assert(recs[0]['workerName'] == 'bob')
    assert(recs[1]['workerName'] == 'bob')
    assert(len(recs) == 2)


def test_get_records_listens_to_district(collection, workers_coll):
    lookup = get_worker_lookup(workers_coll, 'other')
    needed = [{'workerPhone': 'baz', 'needed': 1}]
    recs = list(get_records(collection, needed, 1.00, lookup))
    assert(len(recs) == 1)
    assert(recs[0]['workerName'] == 'mark')

def test_get_worker_lookup(workers_coll):
    lookup = get_worker_lookup(workers_coll, 'other')
    assert (lookup == {'baz': 'mark'})
    # test cache doesn't break it
    lookup = get_worker_lookup(workers_coll, 'other')
    assert (lookup == {'baz': 'mark'})
