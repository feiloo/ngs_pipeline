import datetime
import json
import requests

assert 'filemaker_user' in config
assert 'filemaker_psw' in config
assert 'filemaker_server' in config

session_url = 'https://ukb1144/fmi/data/v1/databases/molpatho_Leistungserfassung/sessions'
def get_token():
    r = requests.post(
            session_url, 
            auth=(config['filemaker_user'],config['filemaker_psw']), 
            verify=False,
            headers={'Content-Type': 'application/json'})
    

    # filemakers session tokens last for 15 minutes
    ttl = 14*1/(24*60) # in days, around 14 minutes
    cache_timer = (datetime.datetime.now() + datetime.timedelta(ttl)).timestamp()
    with open('/tmp/fmrest_cache','w') as f:
        d = json.dumps({'token':r.json(), 'time':str(cache_timer)})
        f.write(d)

def auth():
    if not os.path.exists('/tmp/fmrest_cache'):
        get_token()

    with open('/tmp/fmrest_cache','r') as f:
        d = json.loads(f.read())

    cache_time = datetime.datetime.fromtimestamp(ceil(float(d['time'])))
    if cache_time < datetime.datetime.now():
        print('renewing token')
        get_token()

    token = d['token']['response']['token']
    return token

fm_baseurl = f"https://{config['filemaker_server']}/fmi/data/v1/databases"

def get_records():
    record_url = fm_baseurl+'/molpatho_Leistungserfassung/layouts/Leistungserfassung/records?_limit=10&_offset=40000'
    r = requests.get(
            record_url, 
            verify=False,
            headers={'Content-Type': 'application/json',
                "Authorization": f"Bearer {token}"}
                )
    return r.json()

def find_records():
    record_url = fm_baseurl+'/molpatho_Leistungserfassung/layouts/Leistungserfassung/_find'
    d = json.dumps({"query":[{"Zeitstempel":">=10/18/2022"}],
                "limit":100
                })
    r = requests.post(
            record_url, 
            data=d,
            verify=False,
            headers={'Content-Type': 'application/json',
                "Authorization": f"Bearer {token}"}
                )
    return r.json()
    
token = auth()
#records = get_records()
records = find_records()
#print(str(records).replace("'", '"'))
#print(records['response']['data'][0]['fieldData'])
