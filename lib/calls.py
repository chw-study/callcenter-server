import math
import datetime as dt
from itertools import groupby
from collections import OrderedDict

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
    return {'worker': worker, 'count': (called, not_called)}

def group_call_counts(calls):
    return (format_group(k,g) for k,g in
            groupby(calls, key = lambda c: c['_id']['worker']))

def get_call_counts(collection):
    cursor = collection.aggregate([
        { '$group': { '_id': {'worker': '$worker', 'called': '$called'}, 'count': { '$sum': 1 }}},
        { '$sort': OrderedDict([ ('_id.worker', 1), ('_id.called', 1)])}
    ])
    return (c for c in cursor if (c['_id'].get('worker')))


def get_needed_calls(coll, percent):
    return ({'worker': c['worker'], 'needed': needed_calls(c, percent)}
            for c in group_call_counts(get_call_counts(coll)))

def get_records(coll, needed, hours):
    cursors = ((coll
                .find({ 'worker': n['worker'],
                        'called': False,
                        'attempts': {'$not': { '$gte': hours_ago(hours) }}})
                .limit(n['needed']))
               for n in needed if n['needed'] > 0)
    return (c for i in cursors for c in i)
