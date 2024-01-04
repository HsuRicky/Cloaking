from django.test import TestCase
from pprint import pprint

# Create your tests here.

from pymongo import MongoClient
from datetime import datetime

# Requires the PyMongo package.
# https://api.mongodb.com/python/current

start_ts = 1701705600
end_ts = 1701792000
gap_ts = 1701792000-1701705600

client = MongoClient('mongodb://34.151.127.107:27017/')
filter = {
    "time": {
        "$gte": start_ts-gap_ts,
        "$lt": end_ts-gap_ts,
    },
    'ABPage': 'B',
    'PageName': 'index'
}
project = {
    'Referer': 1,
    'gclid': 1,
    'state': 1,
    'time': 1
}

result = client['ABPage']['access'].find(
    filter=filter,
    projection=project
)

click = []
view = []
for res in result:
    view.append(res['gclid'])

    try:
        if 'google' not in res['Referer']:
            continue
    except:
        continue

    click.append(res['gclid'])


google_click_no_repeat = len(set(click))
google_click_total = len(click)

B_index_view_no_repeat = len(set(view))
B_index_view_total = len(view)


output1 = [
    [google_click_no_repeat, google_click_total,
        google_click_no_repeat/google_click_total],
    [B_index_view_no_repeat, B_index_view_total,
        B_index_view_no_repeat/B_index_view_total],
    [google_click_no_repeat/B_index_view_no_repeat,
        google_click_total/B_index_view_total, None],
]

pprint(output1)


output2 = [
    [google_click_no_repeat, None, None],
    [google_click_total, None, None],
    [B_index_view_no_repeat, None, None]
    [B_index_view_total, None, None],
    [google_click_no_repeat/google_click_total, None, None]
    [B_index_view_no_repeat/B_index_view_total, None, None],
]
