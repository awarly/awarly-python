# Awarly Python bindings
# API docs at http://awarly.com/docs
# Author: Christian Hentschel <ch@awarly.com>

import re 
import sys
import json
import urllib2

from urllib import urlencode
from urllib2 import HTTPError

API_HOST = 'https://awarly.com'

app_key = None
app_secret = None

_access_token = None

# Regex for validate time in "24:00 -0300" format.
valid_time = re.compile('^([01][0-9]|2[0-4]):[0-6][0-9] [+-]([0[0-9]|1[0-4])[0-6][0-9]$')

def is_numeric(x):
    return isinstance(x, (int, long, float))

def is_valid_radius(x):
    return isinstance(x, int) and (x > 0) and (x < 10000)

def is_valid_lat(x):
    return is_numeric(x) and (x <= 90) and (x >= -90)
    
def is_valid_lng(x):
    return is_numeric(x) and (x <= 180) and (x >= -180)

def is_valid_time(x):
    return valid_time.match(x)
     
def is_valid_dtype(x):
    return isinstance(x, str) and x in ('android', 'ios', 'blackberry')
     
class pushPayload():
    def __init__(self, alert, badge=0, sound="default", content_available=False, title=None, **kwargs):
        assert(isinstance(alert, str))
        assert(isinstance(badge, int))
        assert(isinstance(sound, str))

        self.data = {
            'alert': alert, 'badge': badge, 'sound': sound
        }
        
        if content_available:
            self.data['content-available'] = 1
    
        if title:
            assert(isinstance(title, str))
            self.data['title'] = title
            
        #Fill aditional key value pairs
         
        for k, v in kwargs.items():
            if k in ['alert', 'badge', 'sound', 'content-available', 'title']:
                continue
            
            assert(isinstance(k, str))
            assert(isinstance(v, str))
            self.data[k] = v

    def to_dict():
        return json.dumps(self.data)

def _get_access_token():
    global _access_token
    
    data = urlencode({
        'client_id': app_key,
        'client_secret': app_secret,
        'grant_type': 'client_credentials'
    })
    req = urllib2.Request(API_HOST + '/oauth/access_token?' + data)
    req.get_method = lambda: 'POST'

    ret = urllib2.urlopen(req)        
    body = json.loads( ret.read() )

    _access_token = body['access_token']

def _auth_request(method, url, data=None):
    if not _access_token:
        _get_access_token()

    req = urllib2.Request(API_HOST + url)
    req.add_header("Authorization", "Bearer %s" % _access_token)
    req.get_method = lambda: method
    if data:
        req.add_header("Content-Type", "application/json")
        req.add_data(data)

    return urllib2.urlopen(req)

def push(payload, device_types=None, channels=None, oids=None, exclude_oids=None, geo=None):
    assert(isinstance(oids, list))
    assert(isinstance(payload, pushPayload))
    data = {
        'payload': payload.data
    }

    if device_type:
        assert(isinstance(oids, list))
        data['types'] = device_types
            
    if oids:
        assert(isinstance(oids, list))
        data['oids'] = oids

    if channels:
        assert(isinstance(channels, list))
        data['channels'] = channels

    if geo:
        assert(isinstance(geo, list))
        assert(is_valid_lat(geo[0]))
        assert(is_valid_lng(geo[1]))
        assert(is_valid_radius(geo[2]))
    
        data['geo'] = { 'lat': geo[0], 'lng': geo[1], 'radius':geo[2] }

    if exclude_oids:
        assert(isinstance(exclude_oids, list))
        data['exclude_oids'] = exclude_oids

    ret = _auth_request(
        'POST', '/api/push', json.dumps([data])
    )
        
def deviceList():
    ret = _auth_request('GET', '/api/devices')   
    return json.loads(ret.read())

def deviceCount():
    ret = _auth_request('GET', '/api/devices/count')
    return json.loads(ret.read())

def deviceGet(device_oid):
    assert(isinstance(device_oid, str))

    ret = _auth_request('GET', '/api/devices/' + device_oid)
    return json.loads(ret.read())

def deviceFeedback():
    ret = _auth_request('GET', '/api/feedback')
    return json.loads(ret.read())

