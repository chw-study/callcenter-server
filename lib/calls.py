import math
import datetime as dt
from itertools import groupby
from collections import OrderedDict
import logging
from toolz import assoc
from cacheout import Cache
import random
cache = Cache(maxsize=1024, ttl=180)

def hours_ago(hours):
    return dt.datetime.utcnow() - dt.timedelta(hours = hours)

def needed_calls(calls, percent):
    called, not_called = calls['count']
    called = called if called else 0
    not_called = not_called if not_called else 0
    target = int(math.ceil(percent * (called + not_called)))
    dif = target - called
    return 0 if dif < 0 else dif

def format_group(worker, group):
    group = list(group)
    called = [g['count'] for g in group if g['_id'].get('called')]
    not_called = [g['count'] for g in group if not g['_id'].get('called')]
    called = 0 if not called else called[0]
    not_called = 0 if not not_called else not_called[0]
    return {'workerPhone': worker, 'count': (called, not_called)}

def group_call_counts(calls):
    return (format_group(k,g) for k,g in
            groupby(calls, key = lambda c: c['_id']['workerPhone']))

def get_call_counts(collection, district_lookup):
    # TODO: Add "refused to give consent" fileter!!
    # TODO: Add filter for STALE records!!
    district_nums = list(district_lookup.keys())
    cursor = collection.aggregate([
        { '$match': {'workerPhone': { '$in': district_nums}}},
        { '$group': { '_id': {'workerPhone': '$workerPhone', 'called': '$called'}, 'count': { '$sum': 1 }}},
        { '$sort': OrderedDict([ ('_id.workerPhone', 1), ('_id.called', 1)])}
    ])
    cursor = [c for c in cursor]
    return (c for c in cursor if (c['_id'].get('workerPhone')))


def get_needed_calls(coll, percent, district_lookup):
    needed = ({'workerPhone': c['workerPhone'], 'needed': needed_calls(c, percent)}
            for c in group_call_counts(get_call_counts(coll, district_lookup)))
    needed = list(needed)
    random.shuffle(needed)
    return needed

def get_worker_lookup(coll, district):
    cached = cache.get(district)
    if cached:
        return cached
    res = coll.find({'chw_district': district })
    lookup = {r.get('reporting_number'): r.get('name') for r in res}
    cache.set(district, lookup)
    return lookup

def add_name(lookup, r):
    return assoc(r, 'workerName', lookup[r['workerPhone']])

def get_records(coll, needed, hours, lookup):
    # TODO: Add filter for STALE records!!
    cursors = (coll.aggregate([
        { '$match': { 'workerPhone': n['workerPhone'],
                        'called': None,
                        'noConsent': None,
                        'attempts': {'$not': { '$gte': hours_ago(hours) }}}},
        { '$sample': { 'size': n['needed'] }}
    ]) for n in needed if n['needed'] > 0)
    return (add_name(lookup, c) for i in cursors for c in i)
