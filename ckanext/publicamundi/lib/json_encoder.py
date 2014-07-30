import json
import datetime

class JsonEncoder(json.JSONEncoder):
    '''Override default json.JSONEncoder behaviour so that it can serialize
    datetime objects
    '''
    def default(self, o):
        if isinstance(o, datetime.datetime) or isinstance(o, datetime.date) or \
           isinstance(o, datetime.time):
            return o.isoformat()
        else:
            return json.JSONEncoder.default(self, o)

