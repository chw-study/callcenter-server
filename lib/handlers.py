import datetime as dt
from nltk.tokenize import wordpunct_tokenize, word_tokenize
import re

def new_message_handler(collection, msg):
    txt = msg['text']
    try:
        timestamp = dt.datetime.strptime(msg['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
        parsed = parse_text(txt)
    except:
        timestamp = dt.datetime.now()
        parsed = {}

    message = {
        'text': msg.get('text', ''),
        'called': False,
        'timestamp': timestamp,
        'workerPhone': msg.get('phone'),
        'worker': msg.get('phone'),
        'run': int(msg.get('run', 0)),
        'phone': parsed.get('phone'),
        'name': parsed.get('name')
    }
    return collection.insert(message)

def parse_text(text):
    words = word_tokenize(text)
    p = re.compile('\d+')
    text = [word for word in words if not re.search('\d+', word)]
    nums = [word for word in words if re.search('\d+', word)]
    nums = p.findall(''.join(nums))
    phone = int(''.join(nums))

    p = re.compile("[.,\/#!$%\^&\*;:{}=\-_`~()]")
    name = ' '.join([s for s in [p.sub('', t) for t in text] if s])

    return {
        'phone': phone,
        'name': name
    }
